"""The obligations a `core-0` program owes, and the condition that reaches
each one.

SPEC.md, "Verification obligations and the initial fragment": every
potentially evaluated call emits a precondition obligation under its path
condition; each function emits obligations connecting its body to its
postcondition; example validity, contract definedness and structural
termination have separate records; an unreachable path can make an
obligation vacuous but does not remove it.

Nothing here attempts an obligation. This module has no solver, reads no
file, spawns nothing and keeps no state: it turns a typed program into the
list of what would have to be shown about it. Every obligation carries two
words that are constants of the type and not something a caller can set:
`not_attempted`, its standing as a statement, and `unsupported`, what
happened when something tried to settle it.

The inventory is built only for a program the checker accepted, so every
call it meets is resolved; a call that is not resolved is a programming
error here and refuses loudly.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import encoding, syntax

# What an obligation stands as, and what happened to the attempt to
# settle it: SPEC.md lines 270-284 keep the two apart and give each its
# own words, which share none. This tool has no solver, so nothing here
# supported an attempt and every entry carries both constants.
NOT_ATTEMPTED = "not_attempted"

# What confirms a candidate counterexample to an obligation. Each kind
# names one of these, and the unit that replays a candidate reads the
# same words, so neither of them spells a word the other does not know.
# The first three are refusals of the reference semantics; the fourth
# means no input can refute the kind at all.
BY_A_PRECONDITION = "precondition"
BY_A_POSTCONDITION = "postcondition"
BY_THE_EXAMPLE_ITSELF = "example"
BY_NOTHING = "nothing"

# The one that is not a refusal: the conclusion of the obligation is a
# condition about the value another function answers, so there is nothing
# for a call to refuse. The obligation replays the composition itself and
# says whether the reference semantics refuted it.
BY_THE_INVARIANT_AFTER_THE_STEP = "invariant_after_step"

# The two rules of core-0 that settle an obligation with no solver, each
# named once here and written out once in an answer that used it. An
# entry names its rule; the sentence stands beside the inventory, so a
# program of many functions does not carry the same paragraph a thousand
# times and two entries resting on one rule are seen to.
TOTALITY_OF_THE_PROFILE = "totality_of_the_profile"
ACYCLIC_CALLS = "acyclic_calls"

THE_RULES_OF_THE_PROFILE = {
    TOTALITY_OF_THE_PROFILE: (
        "Read over the total meaning of core-0, every operation the profile "
        "has is defined for every value of its declared types: there is no "
        "division and no other partial primitive, field selection is resolved "
        "from the operand's nominal type by the checker that accepted this "
        "program, and every match it contains was shown exhaustive. That is "
        "all this entry claims. It does not claim that running a clause "
        "answers a value, because three things can stop a run of one: a call "
        "whose precondition does not hold, a call whose postcondition does "
        "not hold, which the evaluator checks and refuses, and the evaluation "
        "depth budget, which stops a run that nests deeper than this tool "
        "runs. The first of those is a call_precondition obligation of its "
        "own, listed and settled separately; the second is the callee's own "
        "body_postcondition obligation, also listed; the third is a budget "
        "this tool declares and not a statement about the program. No solver "
        "is asked about an entry resting on this rule."
    ),
    ACYCLIC_CALLS: (
        "The combined dependency graph of bodies and contracts must be acyclic "
        "in core-0, and the checker that accepted this program refuses any "
        "program whose graph has a cycle. Every call such a function can reach "
        "therefore ends, and so does it. No solver is asked about an entry "
        "resting on this rule."
    ),
}


def the_rules_of_the_profile(named: set) -> dict:
    """The sentences of the rules an answer used, and of no others."""
    return {
        name: THE_RULES_OF_THE_PROFILE[name]
        for name in sorted(named)
        if name in THE_RULES_OF_THE_PROFILE
    }


NOTHING_WAS_ATTEMPTED = (
    "This tool has no solver and ran none of these obligations: every entry is "
    "still owed and its result is not_attempted. The list says what work remains "
    "and nothing else."
)


# --- where an obligation arises, and what reaches it -----------------------

@dataclass(frozen=True)
class Site:
    """Where in a declaration an obligation arises, as a structural path
    (`contract`, `body`, `ensures[1]/arg[0]`, `body/then`): never a line
    number, so reformatting a program leaves every identity unchanged."""

    segments: tuple[str, ...]

    def inside(self, segment: str) -> "Site":
        return Site(self.segments + (segment,))

    def text(self) -> str:
        return "/".join(self.segments)


@dataclass(frozen=True)
class Holds:
    """A condition reached because an expression of the program is true
    there: the test of an `if` on the way into its branch, or a clause of
    the function's own precondition."""

    expression: object

    def text(self) -> str:
        return text_of(self.expression)


@dataclass(frozen=True)
class Fails:
    """A condition reached because an expression of the program is false
    there: the test of an `if` on the way into its other branch."""

    expression: object

    def text(self) -> str:
        return f"(not {text_of(self.expression)})"


@dataclass(frozen=True)
class Matches:
    """A condition reached because the scrutinee of a `match` has the
    shape one of its patterns writes."""

    scrutinee: object
    pattern: object

    def text(self) -> str:
        return f"(matches {text_of(self.scrutinee)} {pattern_text(self.pattern)})"


@dataclass(frozen=True)
class DoesNotMatch:
    """A condition reached because an earlier clause of a `match` did not
    take the value: clauses are tried in source order, so a later one is
    reached only where every earlier pattern failed."""

    scrutinee: object
    pattern: object

    def text(self) -> str:
        return (
            f"(not (matches {text_of(self.scrutinee)} "
            f"{pattern_text(self.pattern)}))"
        )


@dataclass(frozen=True)
class PathCondition:
    """What must hold for a site to be reached: the function's own
    precondition where the site is answered under it, then the branch and
    match conditions on the way down. It reads `true` only when there is
    none.

    Each clause is the condition it is -- an expression holding or
    failing, a pattern matching or not -- and not the text of one. A
    reader is shown the text; anything that has to decide what reaches a
    site, rather than print it, is given the program's own expressions.
    """

    clauses: tuple[object, ...] = ()

    def extended_with(self, clauses: tuple[object, ...]) -> "PathCondition":
        return PathCondition(self.clauses + clauses)

    def text(self) -> str:
        if not self.clauses:
            return "true"
        written = [clause.text() for clause in self.clauses]
        if len(written) == 1:
            return written[0]
        return "(and " + " ".join(written) + ")"


# --- what must be shown ----------------------------------------------------

@dataclass(frozen=True)
class Obligation:
    """One thing that would have to be shown about one function.

    No constructor takes either of its two words: `not_attempted` is the
    only standing an obligation can carry and `unsupported` the only
    thing that can have happened to it here, so an inventory reporting
    attempted work cannot be built at all.
    """

    function: str
    site: Site

    kind = "obligation"

    @property
    def identity(self) -> str:
        return f"{self.kind}:{self.function}:{self.site.text()}"

    # `BY_NOTHING` means no input can refute this kind: the kinds a rule
    # of the profile settles are never disproved, so nothing is ever
    # replayed for them.
    confirmed_by = BY_NOTHING

    # Whether a run of the program decides this kind outright. False for
    # every kind that ranges over inputs no single run exhausts: nothing
    # a run of one input shows proves such a statement. True only where
    # the input is written in the program itself, so there is one run to
    # make and its answer is the whole of the evidence.
    settled_by_running = False

    @property
    def whose_refusal_confirms_it(self) -> str:
        """Which function's own refusal confirms a candidate for this
        obligation.

        A run of one input can be refused by any function the run
        reaches, and most of those refusals say nothing about the
        obligation being settled: a body that never answers because a
        function it calls refused is not a body that broke its own
        promise. The kind names the one function whose refusal is the
        thing it denies, and the replay reads that name rather than
        taking any refusal it meets.
        """
        return self.function

    def rests_on(self) -> tuple[str, ...]:
        """The obligations of the same inventory this one is settled
        from, by identity.

        Empty for every kind that stands on its own claim. A kind that
        names some is settled after them and from what became of them,
        so one fact is decided once and two entries of one answer cannot
        disagree about it.
        """
        return ()

    def confirmed_by_replaying(self, program, claim, texts: tuple, args: tuple):
        """The witness a replay of this obligation's own composition
        confirms for `args`, or `None` when it confirms none.

        Answered only by the kinds whose conclusion no single call can
        refuse: such a kind runs the functions its claim composes and
        reads what they answered. Every other kind answers nothing here
        and is confirmed by a refusal instead, so there is one place per
        kind where a candidate becomes a counterexample.
        """
        return None

    def to_show(self) -> str:
        raise NotImplementedError("each kind of obligation says what it owes")

    def detail(self) -> dict:
        return {}

    def claim_in(self, program: syntax.Program):
        """This obligation as a claim a solver can be asked, as a
        construct the translation does not cover, or as a rule of the
        profile that settles it without one.

        Each kind states its own claim: what may be assumed about the
        inputs that reach it, and the one thing to be shown there.
        """
        return encoding.attempted(lambda: self._claim(program))

    def _claim(self, program: syntax.Program):
        raise NotImplementedError("each kind of obligation states its own claim")

    def nothing_satisfies_it_in(self, program: syntax.Program):
        """The claim that nothing at all satisfies what this obligation
        assumes, or `None` when it assumes nothing.

        An obligation that assumes nothing ranges over every input of
        its types and cannot hold for want of anything to range over, so
        it has no such claim. One that does assume something is valid
        whenever its assumptions are contradictory, which is no statement
        about the program at all: whoever asks a solver about the
        obligation asks this one too before taking the word.
        """
        return None

    def as_dict(self, finding) -> dict:
        entry = {
            "id": self.identity,
            "kind": self.kind,
            "function": self.function,
            "site": self.site.text(),
            "to_show": self.to_show(),
        }
        entry.update(self.detail())
        finding.written_into(entry)
        return entry


@dataclass(frozen=True)
class CallPrecondition(Obligation):
    """A call meets the precondition of the function it calls, wherever the
    condition that reaches it holds."""

    callee: str
    precondition_clauses: int
    path_condition: PathCondition
    call: syntax.Call

    kind = "call_precondition"
    confirmed_by = BY_A_PRECONDITION

    @property
    def whose_refusal_confirms_it(self) -> str:
        """The callee, and no other function.

        What this obligation denies is that the callee refuses the
        arguments this call passes it. A run refused by anything else --
        the calling function's own precondition, a function called
        before this one -- did not reach this call at all, and reading
        it as a confirmation would report a counterexample that never
        gets there.
        """
        return self.callee

    def to_show(self) -> str:
        return (
            f"the arguments this call passes to '{self.callee}' meet its precondition "
            f"whenever the condition that reaches the call is true"
        )

    def _in_scope_at_the_call(self, function, translation) -> dict:
        """What the call can name where it stands: the parameters of the
        function always, and its answer where the call stands in what the
        function promises.

        Only a postcondition may read `result` in core-0, so the answer
        is in scope there and nowhere else; a call in a precondition or
        in the body names the parameters alone.
        """
        bound = translation.parameters_of(function)
        if not self.site.segments[0].startswith("ensures"):
            return bound
        return {**bound, "result": translation.term_of(function.body, bound)}

    def detail(self) -> dict:
        return {
            "callee": self.callee,
            "precondition_clauses": self.precondition_clauses,
            "path_condition": self.path_condition.text(),
        }

    def _claim(self, program: syntax.Program):
        """The arguments this call passes meet the callee's precondition
        wherever the condition that reaches the call holds.

        The condition that reaches it is assumed, not shown: it is what
        makes a call behind a test provable where the same call with
        nothing in front of it is not.
        """
        function = program.functions[self.function]
        callee = program.functions[self.callee]
        translation = encoding.Translation(program)
        bound = self._in_scope_at_the_call(function, translation)
        return encoding.Claim(
            encoding.Shapes.of(program),
            encoding.variables_of(function),
            tuple(
                translation.condition_of(clause, bound)
                for clause in self.path_condition.clauses
            ),
            translation.conjunction_of(
                callee.requires,
                {
                    parameter.name: translation.term_of(argument, bound)
                    for parameter, argument in zip(
                        callee.signature.params, self.call.args
                    )
                },
            ),
        )


@dataclass(frozen=True)
class BodyPostcondition(Obligation):
    """A function's body answers what its postcondition states."""

    postcondition_clauses: int

    kind = "body_postcondition"
    confirmed_by = BY_A_POSTCONDITION

    def to_show(self) -> str:
        return (
            f"the body of '{self.function}' answers its postcondition for every input "
            f"that meets its precondition"
        )

    def detail(self) -> dict:
        return {"postcondition_clauses": self.postcondition_clauses}

    def _claim(self, program: syntax.Program):
        """What the body answers meets what the function promises, for
        every input of the declared types that meets its precondition."""
        function = program.functions[self.function]
        translation = encoding.Translation(program)
        bound = translation.parameters_of(function)
        answered = translation.term_of(function.body, bound)
        return encoding.Claim(
            encoding.Shapes.of(program),
            encoding.variables_of(function),
            tuple(
                translation.term_of(clause, bound) for clause in function.requires
            ),
            translation.conjunction_of(
                function.ensures, {**bound, "result": answered}
            ),
        )


@dataclass(frozen=True)
class ExampleValidity(Obligation):
    """A declared example is a valid example of its own function."""

    ordinal: int
    example: syntax.Example

    kind = "example_validity"
    confirmed_by = BY_THE_EXAMPLE_ITSELF

    # The arguments of an example are closed values written in the
    # program, so this obligation is about one run of one function over
    # one input. The reference semantics answers it outright: it says
    # whether that run reaches the end, whether the function keeps its
    # own contract over it, and what value it answers. No statement
    # about other inputs is involved, so no formula is the last word
    # here.
    settled_by_running = True

    def to_show(self) -> str:
        return (
            f"declared example {self.ordinal} of '{self.function}' has arguments of the "
            f"declared types that meet its precondition, and the result it states"
        )

    def detail(self) -> dict:
        return {"ordinal": self.ordinal}

    def _claim(self, program: syntax.Program):
        """The arguments of this example meet the precondition, and what
        the function answers over them is the value the example states.

        The arguments are closed values, so this claim is about no
        variable at all.
        """
        function = program.functions[self.function]
        translation = encoding.Translation(program)
        supplied = {
            parameter.name: translation.term_of_value(argument)
            for parameter, argument in zip(
                function.signature.params, self.example.args
            )
        }
        return encoding.Claim(
            encoding.Shapes.of(program),
            (),
            (),
            encoding.Term.all_of(
                (
                    translation.conjunction_of(function.requires, supplied),
                    encoding.Term.built(
                        encoding.EQUALS,
                        (
                            translation.term_of(function.body, supplied),
                            translation.term_of_value(self.example.expected),
                        ),
                    ),
                )
            ),
        )


@dataclass(frozen=True)
class ContractDefinedness(Obligation):
    """A function's contract is defined for every input of its types."""

    contract_clauses: int
    calls_in_the_contract: tuple[str, ...] = ()

    kind = "contract_definedness"

    def to_show(self) -> str:
        return (
            f"every clause of the contract of '{self.function}' is defined for every "
            f"input of the declared types"
        )

    def detail(self) -> dict:
        return {"contract_clauses": self.contract_clauses}

    def rests_on(self) -> tuple[str, ...]:
        """The precondition obligations of the calls the contract makes.

        The rule below settles the primitives of core-0, which are total,
        and says so itself: it does not claim that running a clause
        answers a value, because a call whose precondition does not hold
        stops the run. A contract that calls a function is defined
        everywhere exactly when each of those calls meets the callee's
        precondition wherever the clause before it has let the run get
        there -- which is what these obligations are. So this entry is
        settled from them rather than from the rule alone, and a contract
        with no call in it rests on nothing and is settled by the rule as
        it always was.
        """
        return self.calls_in_the_contract

    def _claim(self, program: syntax.Program):
        return encoding.ByRuleOfTheProfile(TOTALITY_OF_THE_PROFILE)


@dataclass(frozen=True)
class StructuralTermination(Obligation):
    """A function terminates because the calls it can reach are acyclic."""

    direct_calls: int

    kind = "structural_termination"

    def to_show(self) -> str:
        return (
            f"'{self.function}' terminates structurally: the calls it can reach are "
            f"acyclic and each of them terminates"
        )

    def detail(self) -> dict:
        return {"direct_calls": self.direct_calls}

    def _claim(self, program: syntax.Program):
        return encoding.ByRuleOfTheProfile(ACYCLIC_CALLS)


# --- the inventory ---------------------------------------------------------

@dataclass(frozen=True)
class Inventory:
    """The obligations a program owes, in declaration order.

    Two obligations may not share an identity: an identity names one
    obligation, so two answers can be compared entry by entry.
    """

    obligations: tuple[Obligation, ...]

    def __post_init__(self) -> None:
        identities = [obligation.identity for obligation in self.obligations]
        repeated = sorted({name for name in identities if identities.count(name) > 1})
        if repeated:
            raise ValueError(
                f"WHAT: {repeated} each name more than one obligation in the same "
                "inventory. "
                "WHY: an identity names one obligation, so that two answers about the "
                "same program can be compared entry by entry; repeated identities make "
                "that comparison meaningless. "
                "HOW: give each obligation a site that says where in the declaration it "
                "arises, as the walk over requires, ensures and the body does."
            )

    def with_also(self, more: tuple[Obligation, ...]) -> "Inventory":
        """This inventory with `more` owed after it.

        One inventory, so that the obligations of a machine are settled
        by the one loop that settles a program's own, reported by the one
        rule that reports them, and counted by the one word that is said
        over all of them. The identity rule above then holds across both
        sets rather than inside each.
        """
        return Inventory(self.obligations + more)

    def as_dict(self, findings: dict) -> dict:
        """Every obligation beside what became of it.

        One finding per obligation, by identity. An obligation with none
        refuses loudly rather than being written out as though nothing
        were owed for it: nothing may be silently skipped, and a list
        that quietly dropped an entry is the one way this answer could
        mislead without saying anything false.
        """
        self._refuse_an_obligation_with_no_finding(findings)
        entries = [
            obligation.as_dict(findings[obligation.identity])
            for obligation in self.obligations
        ]
        settled = [entry for entry in entries if entry["result"] != NOT_ATTEMPTED]
        rested_on = {entry.get("rule") for entry in entries if entry.get("rule")}
        return {
            "obligations": entries,
            "rules": the_rules_of_the_profile(rested_on),
            "totals": {
                "obligations": len(entries),
                "attempted": len(settled),
                "not_attempted": len(entries) - len(settled),
                "by_kind": self._by_kind(),
                "by_result": self._by_result(entries),
            },
            "note": self._note(entries, settled),
        }

    def _refuse_an_obligation_with_no_finding(self, findings: dict) -> None:
        missing = [
            obligation.identity
            for obligation in self.obligations
            if obligation.identity not in findings
        ]
        if not missing:
            return
        raise ValueError(
            f"WHAT: {missing} are obligations of this program with nothing "
            "said about what became of them. "
            "WHY: an answer that lists an obligation and says nothing about "
            "it reads as one nobody owes; nothing may be silently skipped. "
            "HOW: settle every obligation of the inventory, or carry a "
            "finding saying why it was not attempted."
        )

    def _by_result(self, entries: list) -> dict:
        counted: dict[str, int] = {}
        for entry in entries:
            counted[entry["result"]] = counted.get(entry["result"], 0) + 1
        return {result: counted[result] for result in sorted(counted)}

    def _note(self, entries: list, settled: list) -> str:
        """What a reader of the counts alone is told.

        It names what was settled and what was not, rather than how many
        were attempted: an obligation something tried and could not
        settle -- because it is outside what this tool translates, or
        because the solver could not be loaded or ran out of time -- is
        not a settled one, and a note that counted it as settled would
        say work was done that was not.
        """
        if not settled:
            return NOTHING_WAS_ATTEMPTED
        counted = self._by_result(entries)
        decided = counted.get("proved", 0) + counted.get("disproved", 0)
        return (
            f"{decided} of the {len(entries)} obligations of this program "
            f"were settled: {counted.get('proved', 0)} proved and "
            f"{counted.get('disproved', 0)} disproved. "
            f"{counted.get('unknown', 0)} were tried and could not be "
            f"settled, and {counted.get('not_attempted', 0)} were not "
            "attempted; each of those says why beside it. A result of "
            "'proved' is a statement about this revision of this source and "
            "nothing else; read the disclosure beside the inventory for what "
            "it rests on."
        )

    def _by_kind(self) -> dict:
        counted: dict[str, int] = {}
        for obligation in self.obligations:
            counted[obligation.kind] = counted.get(obligation.kind, 0) + 1
        return {kind: counted[kind] for kind in sorted(counted)}


def inventory_for(program: syntax.Program) -> Inventory:
    """Everything `program` owes, function by function in declaration order."""
    owed: list[Obligation] = []
    for function in program.functions.values():
        owed.extend(_owed_by(function, program))
    return Inventory(tuple(owed))


def _owed_by(function: syntax.Function, program: syntax.Program) -> list[Obligation]:
    contract_clauses = len(function.requires) + len(function.ensures)
    in_the_contract = _calls_in_the_contract_of(function, program)
    calls = in_the_contract + _calls_in_the_body_of(function, program)
    owed: list[Obligation] = [
        ContractDefinedness(
            function.name,
            Site(("contract",)),
            contract_clauses,
            tuple(call.identity for call in in_the_contract),
        )
    ]
    owed.extend(calls)
    owed.append(
        BodyPostcondition(function.name, Site(("body",)), len(function.ensures))
    )
    owed.extend(
        ExampleValidity(
            function.name, Site((f"example[{ordinal}]",)), ordinal, example
        )
        for ordinal, example in enumerate(function.examples)
    )
    owed.append(
        StructuralTermination(function.name, Site(("calls",)), len(calls))
    )
    return owed


def _calls_in_the_contract_of(
    function: syntax.Function, program: syntax.Program
) -> list[Obligation]:
    """Every call the contract of `function` makes, each under what
    reaches it."""
    owed: list[Obligation] = []
    for index, clause in enumerate(function.requires):
        owed.extend(
            _calls_in(
                clause,
                Site((f"requires[{index}]",)),
                function,
                program,
                _the_clauses_before(function.requires, index),
            )
        )
    under_its_own_precondition = _precondition_of(function)
    for index, clause in enumerate(function.ensures):
        owed.extend(
            _calls_in(
                clause,
                Site((f"ensures[{index}]",)),
                function,
                program,
                under_its_own_precondition,
            )
        )
    return owed


def _calls_in_the_body_of(
    function: syntax.Function, program: syntax.Program
) -> list[Obligation]:
    return _calls_in(
        function.body,
        Site(("body",)),
        function,
        program,
        _precondition_of(function),
    )


def _the_clauses_before(clauses: tuple, index: int) -> PathCondition:
    """What reaches the clause at `index` of a precondition.

    The evaluator checks the clauses of a precondition in source order
    and refuses at the first one that is not true, so a later clause runs
    only where every earlier clause held. A call in it may rely on that,
    exactly as a call in a branch may rely on the test in front of it,
    and a witness that breaks an earlier clause never reaches this one.
    The clause may still not assume itself: its own text is not among
    these.
    """
    return PathCondition(tuple(Holds(clause) for clause in clauses[:index]))


def _precondition_of(function: syntax.Function) -> PathCondition:
    """What a call in the postcondition or the body of `function` is reached
    under.

    SPEC.md, "Meaning of a claim": the claim is `Pre_f(x) implies ...`, so
    the postcondition is checked under the precondition and the body answers
    it for every input that meets the precondition. A call in the
    precondition itself is reached under the clauses written before it and
    no more: a precondition must be well-defined for every typed input
    reaching it and cannot assume itself true to justify a partial call.
    """
    return PathCondition(tuple(Holds(clause) for clause in function.requires))


def _calls_in(
    expression: object,
    site: Site,
    function: syntax.Function,
    program: syntax.Program,
    reached_under: PathCondition = PathCondition(),
) -> list[Obligation]:
    owed: list[Obligation] = []
    if isinstance(expression, syntax.Call):
        owed.append(_call_obligation(expression, site, reached_under, function, program))
    for part, segment, added in _parts_of(expression):
        owed.extend(
            _calls_in(
                part,
                site.inside(segment),
                function,
                program,
                reached_under.extended_with(added),
            )
        )
    return owed


def _call_obligation(
    call: syntax.Call,
    site: Site,
    reached_under: PathCondition,
    function: syntax.Function,
    program: syntax.Program,
) -> CallPrecondition:
    callee = program.functions.get(call.name)
    if callee is None:
        raise ValueError(
            f"WHAT: '{function.name}' calls '{call.name}' at {site.text()}, and the "
            "program declares no such function, so nothing was listed. "
            "WHY: the obligations of a program are listed only once every call is "
            "resolved; an obligation about a call to nothing would say nothing. "
            "HOW: run the check operation on this program first: it reports the call "
            "as an unknown_function diagnostic, and verify answers with that same "
            "refusal instead of a list."
        )
    return CallPrecondition(
        function.name, site, call.name, len(callee.requires), reached_under, call
    )


def _parts_of(expression: object) -> list[tuple[object, str, tuple[object, ...]]]:
    """Each subexpression of `expression` with the path segment that names
    it and the conditions that must hold to reach it."""
    if isinstance(expression, syntax.OperatorCall):
        return _parts_of_operator(expression)
    if isinstance(expression, (syntax.Call, syntax.ConstructorCall)):
        return [(arg, f"arg[{index}]", ()) for index, arg in enumerate(expression.args)]
    if isinstance(expression, syntax.FieldAccess):
        return [(expression.target, "target", ())]
    if isinstance(expression, syntax.Let):
        bound = [
            (binding.value, f"bind[{index}]", ())
            for index, binding in enumerate(expression.bindings)
        ]
        return bound + [(expression.body, "in", ())]
    if isinstance(expression, syntax.If):
        asked = expression.condition
        return [
            (expression.condition, "cond", ()),
            (expression.then_branch, "then", (Holds(asked),)),
            (expression.else_branch, "else", (Fails(asked),)),
        ]
    if isinstance(expression, syntax.Match):
        return _parts_of_match(expression)
    return []


def _parts_of_operator(
    expression: syntax.OperatorCall,
) -> list[tuple[object, str, tuple[object, ...]]]:
    """Each operand of an operator with what reaches it.

    `and` and `or` are the two operators of core-0 that do not evaluate
    every operand: the evaluator reads the first, and reads the second
    only where the first was true for `and` and where it was false for
    `or`. An operand nothing can reach is reached under a condition
    nothing satisfies, which is what makes a call behind a guard
    unreachable rather than unguarded. Every other operator evaluates
    all of its operands, so each is reached under nothing of its own.
    """
    if expression.operator not in _ONE_OPERAND_GUARDS_THE_NEXT:
        return [(arg, f"arg[{index}]", ()) for index, arg in enumerate(expression.args)]
    guarded_by = _ONE_OPERAND_GUARDS_THE_NEXT[expression.operator]
    parts: list[tuple[object, str, tuple[object, ...]]] = []
    reached: tuple[object, ...] = ()
    for index, arg in enumerate(expression.args):
        parts.append((arg, f"arg[{index}]", reached))
        reached = reached + (guarded_by(arg),)
    return parts


# The operators whose earlier operand decides whether the next one runs,
# and what the earlier one must have done for it to run.
_ONE_OPERAND_GUARDS_THE_NEXT = {"and": Holds, "or": Fails}


def _parts_of_match(
    expression: syntax.Match,
) -> list[tuple[object, str, tuple[object, ...]]]:
    """Each part of a match with what reaches it.

    Clauses are tried in source order, so a clause is reached where its
    own pattern matches and every pattern before it did not. A pattern
    that cannot fail adds nothing to the first of those and everything
    to the second: no value gets past a catch-all, so a clause written
    after one is reached under a condition nothing satisfies rather than
    under the patterns that can fail alone.
    """
    scrutinee = expression.scrutinee
    parts: list[tuple[object, str, tuple[object, ...]]] = [
        (expression.scrutinee, "scrutinee", ())
    ]
    earlier: tuple[object, ...] = ()
    for index, clause in enumerate(expression.clauses):
        reached = earlier + (
            (Matches(scrutinee, clause.pattern),) if _can_fail(clause.pattern) else ()
        )
        parts.append((clause.body, f"case[{index}]", reached))
        earlier = earlier + (DoesNotMatch(scrutinee, clause.pattern),)
    return parts


def _can_fail(pattern: object) -> bool:
    """Whether a value can fail to match the pattern. A wildcard or a plain
    name always matches, so it adds no condition to the clause it heads."""
    return not isinstance(pattern, (syntax.PatWildcard, syntax.PatVar))


# --- reading an expression back as text ------------------------------------

def text_of(expression: object) -> str:
    """`expression` written back in the source's own syntax, so a reported
    condition reads the way the program does."""
    if isinstance(expression, syntax.IntLit):
        return str(expression.value)
    if isinstance(expression, syntax.BoolLit):
        return "true" if expression.value else "false"
    if isinstance(expression, syntax.UnitLit):
        return "()"
    if isinstance(expression, syntax.NameRef):
        return expression.name
    if isinstance(expression, (syntax.Call, syntax.ConstructorCall)):
        return _applied(expression.name, expression.args)
    if isinstance(expression, syntax.OperatorCall):
        return _applied(expression.operator, expression.args)
    if isinstance(expression, syntax.FieldAccess):
        return f"(.{expression.field_name} {text_of(expression.target)})"
    if isinstance(expression, syntax.Let):
        return _let_text(expression)
    if isinstance(expression, syntax.If):
        return (
            f"(if {text_of(expression.condition)} {text_of(expression.then_branch)} "
            f"{text_of(expression.else_branch)})"
        )
    if isinstance(expression, syntax.Match):
        return _match_text(expression)
    raise ValueError(
        f"WHAT: {expression!r} is not an expression of the core-0 syntax tree, so the "
        "condition that reaches a call could not be written out. "
        "WHY: every condition reported beside an obligation is the program's own text; "
        "an unknown node would be reported as a condition nobody can read. "
        "HOW: add the node to prova.obligations.text_of, beside the syntax type it "
        "belongs to."
    )


def _applied(head: str, args: tuple) -> str:
    if not args:
        return f"({head})"
    return "(" + head + " " + " ".join(text_of(arg) for arg in args) + ")"


def _let_text(expression: syntax.Let) -> str:
    bindings = " ".join(
        f"({binding.name} {text_of(binding.value)})"
        for binding in expression.bindings
    )
    return f"(let ({bindings}) {text_of(expression.body)})"


def _match_text(expression: syntax.Match) -> str:
    clauses = " ".join(
        f"({pattern_text(clause.pattern)} {text_of(clause.body)})"
        for clause in expression.clauses
    )
    return f"(match {text_of(expression.scrutinee)} {clauses})"


def pattern_text(pattern: object) -> str:
    """`pattern` written back in the source's own syntax."""
    if isinstance(pattern, syntax.PatWildcard):
        return "_"
    if isinstance(pattern, syntax.PatVar):
        return pattern.name
    if isinstance(pattern, syntax.PatInt):
        return str(pattern.value)
    if isinstance(pattern, syntax.PatBool):
        return "true" if pattern.value else "false"
    if isinstance(pattern, syntax.PatUnit):
        return "()"
    if isinstance(pattern, syntax.PatConstructor):
        if not pattern.subpatterns:
            return f"({pattern.name})"
        inner = " ".join(pattern_text(sub) for sub in pattern.subpatterns)
        return f"({pattern.name} {inner})"
    raise ValueError(
        f"WHAT: {pattern!r} is not a pattern of the core-0 syntax tree, so the "
        "condition reaching a match clause could not be written out. "
        "WHY: every condition reported beside an obligation is the program's own text. "
        "HOW: add the pattern to prova.obligations.pattern_text, beside the syntax type "
        "it belongs to."
    )
