"""What this tool offers, as an agent reads it from `discover`.

The dispatcher knows which operations exist and which of them it
answers; the checker knows the language. Neither of them knows what a
request for an operation looks like, which of the operation categories
of SPEC.md an operation covers, or which operations are this tool's own.
That is what this module owns, and it writes no answer itself: it hands
the dispatcher the parts and the dispatcher prints them.

SPEC.md lines 465-470 ask the manifest to list the operations, the
signatures of the language and the resource limits, lines 469-470 ask
for an unimplemented operation to be advertised as unavailable, and line
475 says an agent must discover signatures and bindings without guessing
an undocumented API.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import checker

# What a client is told about a field of a request: it must send it, or
# it may leave it out.
REQUIRED = "required"
OPTIONAL = "optional"

# What a client is told about a field of an answer: every answer carries
# it, or exactly the answers whose status is `completed` carry it. A
# field that is there under a narrower condition says that condition in
# its own words.
ALWAYS = "always"
WHEN_COMPLETED = "when completed"


@dataclass(frozen=True)
class Field:
    """One field of a request or of an answer: its name, the kind of
    value it carries, when it is there and what it is for.

    Built only through the constructors below, so the word that says
    when a field is there is one of the words a client can look up, and
    never a spelling of its own.
    """

    name: str
    kind: str
    presence: str
    what: str

    @classmethod
    def must_be_sent(cls, name: str, kind: str, what: str) -> "Field":
        return cls(name, kind, REQUIRED, what)

    @classmethod
    def may_be_sent(cls, name: str, kind: str, what: str) -> "Field":
        return cls(name, kind, OPTIONAL, what)

    @classmethod
    def in_every_answer(cls, name: str, kind: str, what: str) -> "Field":
        return cls(name, kind, ALWAYS, what)

    @classmethod
    def when_completed(cls, name: str, kind: str, what: str) -> "Field":
        return cls(name, kind, WHEN_COMPLETED, what)

    @classmethod
    def when(cls, name: str, kind: str, condition: str, what: str) -> "Field":
        """A field that is there under a condition of its own, written
        out for a client that cannot read it from the two words above."""
        return cls(name, kind, condition, what)

    def published(self) -> dict:
        return {"kind": self.kind, "presence": self.presence, "what": self.what}


@dataclass(frozen=True)
class Fields:
    """The fields of one side of the traffic of an operation, and
    nothing else."""

    fields: tuple[Field, ...]

    def published(self) -> dict:
        return {field.name: field.published() for field in self.fields}


# --- the fields the request reader reads -----------------------------------
#
# The name of each field is written once, here, and the reader in
# service.py looks the field up under it and names it in its refusal, so
# the name an agent reads from the manifest is the name a refusal sends
# it to repair.

SOURCE = Field.may_be_sent(
    "source",
    "text",
    "the program this request is about, as one JSON string, with a line "
    "break written as \\n; a request without it is answered about a "
    "program with nothing in it",
)
FUNCTION = Field.must_be_sent(
    "function",
    "text",
    "the name the submitted program declares for the function to call",
)
DESCRIPTOR = Field.must_be_sent(
    "descriptor",
    "object",
    "the machine descriptor this request is about, as one JSON object: a "
    "separate versioned document naming the three types and the five role "
    "functions of a machine and the assumptions its runtime makes. Its "
    "shape is published under 'machine_descriptor_schema'",
)
ARGUMENTS = Field.may_be_sent(
    "arguments",
    "list of texts",
    "one text per parameter the function declares, each writing a value the "
    'way a program writes it, as "(Clock 12)" or "7"; a request without it '
    "supplies none",
)

# --- the fields every answer carries ---------------------------------------

OPERATION_ANSWERED = Field.in_every_answer(
    "operation",
    "text",
    "the operation this answer is about, as the request named it",
)
STATUS = Field.in_every_answer(
    "status", "text", "one of the statuses this manifest lists"
)
DIAGNOSTICS = Field.in_every_answer(
    "diagnostics",
    "list of diagnostics",
    "every refusal this answer carries, each of a category this manifest "
    "describes; an empty list when there is none",
)
CLAIM = Field.when_completed(
    "claim",
    "object",
    "what kind of statement this answer makes and how far it reaches",
)
SOURCE_DIGEST = Field.when_completed(
    "source_digest",
    "text",
    "the revision of the submitted source this answer is about, as its "
    "SHA-256; it says which text the answer is about and nothing more",
)
# The field is spelled as what it does rather than with the word
# provenance: that word carries 'proven' inside it, and an answer of this
# tool is read by callers that refuse any answer whose text claims
# something was proven. A field name is not the place to make a reader
# look twice.
STANDS_ON = Field.when_completed(
    "stands_on",
    "object",
    "what this answer stands on: under 'dependency_digest' the digest of "
    "this tool and of the language it reads, and under 'versions' the "
    "compiler, the encoding, the solver and the runtime behind it, each "
    "either a version or a sentence beginning 'not applicable:' with the "
    "reason there is none. An answer stands on that digest and on the "
    "revision under 'source_digest', and on nothing else",
)
EVERY_ANSWER = (OPERATION_ANSWERED, STATUS, DIAGNOSTICS)


@dataclass(frozen=True)
class Traffic:
    """The two shapes of one operation an agent may call: what it takes
    and what it answers."""

    request: Fields
    answer: Fields

    def may_be_called(self) -> bool:
        return True

    def published(self) -> dict:
        return {
            "request": {"fields": self.request.published()},
            "response": {"fields": self.answer.published()},
        }


@dataclass(frozen=True)
class NotAnsweredYet:
    """The traffic of an operation this tool refuses.

    It has no shape to publish: nothing is fixed about a request nobody
    can send yet, and publishing one would promise a client something it
    cannot do.
    """

    def may_be_called(self) -> bool:
        return False

    def published(self) -> dict:
        raise ValueError(
            "an operation this tool does not answer has no request shape to "
            "publish: nothing about it is fixed yet, and a client reading one "
            "would write a request that is refused. Publish a shape for it "
            "when the operation starts answering."
        )


def answering(request: tuple[Field, ...], answer: tuple[Field, ...]) -> Traffic:
    return Traffic(Fields(request), Fields(answer))


@dataclass(frozen=True)
class InACategory:
    """The standing of an operation that covers one of the operation
    categories SPEC.md names."""

    category: str

    def record(self, standings: "Standings", name: str, availability: str) -> None:
        standings.covers_a_category(self.category, name, availability)


@dataclass(frozen=True)
class BeyondTheProfile:
    """The standing of an operation this tool answers that SPEC.md names
    in none of its operation categories.

    An operation carries one standing, not a place in two lists, so it
    can be neither in a category and beyond the profile at once nor in
    neither of them.
    """

    reason: str

    def record(self, standings: "Standings", name: str, availability: str) -> None:
        standings.is_this_tools_own(name, self.reason)


class Standings:
    """The two lists an agent reads an operation's standing from: the
    categories of the profile, and the operations this tool added."""

    def __init__(self) -> None:
        self._categories: dict = {}
        self._beyond: dict = {}

    def covers_a_category(self, category: str, name: str, availability: str) -> None:
        self._refuse_a_second_claim(category, name)
        self._categories[category] = {
            "operation": name,
            "availability": availability,
        }

    def _refuse_a_second_claim(self, category: str, name: str) -> None:
        standing = self._categories.get(category)
        if standing is None:
            return
        raise ValueError(
            f"the operations {standing['operation']!r} and {name!r} both "
            f"cover the category {category!r}: an agent reads one operation "
            "per category, so the second would quietly take the place of the "
            "first and the first would disappear from the manifest while this "
            "tool still answers it. Give one of the two the category it "
            "covers and the other its own category, or write it as this "
            "tool's own with the reason, in THE_OPERATIONS in manifest.py."
        )

    def is_this_tools_own(self, name: str, reason: str) -> None:
        self._beyond[name] = reason

    def published(self) -> dict:
        return {"categories": self._categories, "beyond_profile": self._beyond}


@dataclass(frozen=True)
class Operation:
    """One operation this tool has: where it stands in the profile, and
    the shapes of its traffic when an agent may call it.

    A record at the boundary of the JSON answer, so it carries three
    parts rather than the two a domain object would.
    """

    name: str
    standing: "InACategory | BeyondTheProfile"
    traffic: "Traffic | NotAnsweredYet"

    def record_standing(self, standings: Standings, availability: str) -> None:
        self.standing.record(standings, self.name, availability)

    def may_be_called(self) -> bool:
        return self.traffic.may_be_called()

    def published_traffic(self) -> dict:
        return self.traffic.published()


@dataclass(frozen=True)
class Catalogue:
    """Every operation this tool has, and nothing else.

    Published only against the names the dispatcher advertises: a
    catalogue that describes another set of names cannot be published at
    all, so the manifest can neither leave out an operation this tool
    answers nor describe one it does not have.
    """

    operations: tuple[Operation, ...]

    def published(
        self, available: tuple[str, ...], unavailable: frozenset[str]
    ) -> dict:
        advertised = {name: "available" for name in available}
        advertised.update({name: "unavailable" for name in sorted(unavailable)})
        self._refuse_another_set(advertised)
        standings = Standings()
        shapes = {}
        for operation in self.operations:
            availability = advertised[operation.name]
            operation.record_standing(standings, availability)
            self._refuse_a_shape_that_disagrees(operation, availability)
            if operation.may_be_called():
                shapes[operation.name] = operation.published_traffic()
        return {**standings.published(), "operation_schemas": shapes}

    def _refuse_another_set(self, advertised: dict) -> None:
        described = {operation.name for operation in self.operations}
        if described == set(advertised):
            return
        raise ValueError(
            f"the manifest describes the operations {sorted(described)} and "
            f"this tool advertises {sorted(advertised)}: "
            f"{sorted(set(advertised) - described)} would be advertised with "
            f"nothing an agent can read about them, and "
            f"{sorted(described - set(advertised))} would be described "
            "without being answered. Add the operation to THE_OPERATIONS in "
            "manifest.py beside the others, with the category it covers or "
            "the reason it is this tool's own, or take it out of the "
            "operation tuples of service.py."
        )

    def _refuse_a_shape_that_disagrees(
        self, operation: Operation, availability: str
    ) -> None:
        if operation.may_be_called() == (availability == "available"):
            return
        raise ValueError(
            f"the operation {operation.name!r} is advertised as "
            f"{availability!r} and "
            f"{'carries' if operation.may_be_called() else 'carries no'} "
            "request and answer shape. An agent reads the shape of every "
            "operation it may call, and reads none for one it cannot. Give "
            f"{operation.name!r} its two shapes in manifest.py, or write it "
            "as not answered yet."
        )


# --- what this tool has ----------------------------------------------------

SOURCE_READING_REQUEST = (SOURCE,)
A_REFUSAL_OR_AN_ANSWER_ABOUT_A_SOURCE = EVERY_ANSWER + (CLAIM, SOURCE_DIGEST)

# The same, for the operations of the profile, which also say what they
# stand on. The `evaluate` operation is not one of them: SPEC.md names it
# in none of its operation categories, it is this tool's own, and its
# answer carries the claim and the revision alone.
AN_ANSWER_OF_THE_PROFILE = A_REFUSAL_OR_AN_ANSWER_ABOUT_A_SOURCE + (STANDS_ON,)

THE_OPERATIONS = Catalogue(
    (
        Operation(
            "discover",
            InACategory("discovery"),
            answering(
                (),
                EVERY_ANSWER
                + (
                    CLAIM,
                    STANDS_ON,
                    Field.when_completed(
                        "result",
                        "object",
                        "this manifest: the profile, the operations, the "
                        "categories, the statuses, the shapes, the language "
                        "and the resource limits",
                    ),
                ),
            ),
        ),
        Operation(
            "check",
            InACategory("checking"),
            answering(
                SOURCE_READING_REQUEST,
                AN_ANSWER_OF_THE_PROFILE
                + (
                    Field.when_completed(
                        "contract_report",
                        "object",
                        "which functions of the checked program promise "
                        "nothing, in the shape this manifest publishes under "
                        "contract_report",
                    ),
                ),
            ),
        ),
        Operation(
            "verify",
            InACategory("verification"),
            answering(
                SOURCE_READING_REQUEST,
                AN_ANSWER_OF_THE_PROFILE
                + (
                    Field.when_completed(
                        "result",
                        "object",
                        "the inventory of the obligations the program owes, "
                        "each beside what became of it. Every entry says "
                        "under 'result' where it stands as a statement -- "
                        "'proved', 'disproved', 'unknown' or 'not_attempted' "
                        "-- and under 'execution_status' what happened when "
                        "something tried to settle it. The two are read "
                        "apart: an entry nothing ran is not an entry nothing "
                        "is owed for. An entry proved carries "
                        "'discharged_by', which is 'solver' when one was "
                        "asked and 'structure' when a rule of core-0 settled "
                        "it; an entry left unsettled carries 'reason'; an "
                        "entry disproved carries 'counterexample', an input "
                        "of the declared types that breaks it and that this "
                        "tool refuses when it runs the program over it. A "
                        "counterexample carries 'replayed_within', the "
                        "declared budget the run that confirmed it stood "
                        "inside: the limit it names and the maximum that "
                        "limit allows are the ones published under "
                        "resource_limits",
                    ),
                    Field.when_completed(
                        "aggregate",
                        "object",
                        "where the program as a whole stands. Under 'result' "
                        "the word 'verified' or the word 'not_verified', and "
                        "under 'execution_status' what happened to the "
                        "attempt. 'verified' is said when, and only when, the "
                        "inventory is not empty and every obligation of it is "
                        "'proved', every "
                        "example the program declares was run and passed, and "
                        "the static checks passed; anything else is "
                        "'not_verified' with a 'reason' naming the "
                        "obligations that are not discharged and the examples "
                        "that did not pass or were never run. All three are "
                        "published beside the word: under 'obligations' how "
                        "many of them were discharged, which were not, and "
                        "how many a solver answered against how many a rule "
                        "of core-0 settled; under 'examples' how many passed, "
                        "which failed and how many were never run; under "
                        "'static_checks' that the checker accepted this "
                        "program. An answer whose solver could not be loaded "
                        "is 'not_verified' beside 'tool_failure': the answer "
                        "itself is still 'completed', because the inventory "
                        "is still there to read, and a failure of this tool "
                        "is never a statement about the program",
                    ),
                    Field.when(
                        "trust",
                        "object",
                        "when a solver was asked about at least one obligation",
                        "what the word 'proved' rests on: under "
                        "'trusted_from' what was trusted, under 'solver' and "
                        "'encoding' the solver asked and the translation "
                        "written for it, and under 'rechecked_by_this_tool' "
                        "whether this tool checked that result again, which "
                        "is false. SPEC.md lines 302-305 allow this tool to "
                        "trust a solver's validity result only while it "
                        "discloses that trust",
                    ),
                ),
            ),
        ),
        Operation(
            "examples",
            InACategory("examples"),
            answering(
                SOURCE_READING_REQUEST,
                AN_ANSWER_OF_THE_PROFILE
                + (
                    Field.when_completed(
                        "result",
                        "object",
                        "one entry per example the program declares, with the "
                        "value it expects, the value the function answered and "
                        "whether the two agree",
                    ),
                ),
            ),
        ),
        Operation(
            "evaluate",
            BeyondTheProfile(
                "SPEC.md lines 467-468 name seven operation categories and "
                "this operation is in none of them: it runs a function of a "
                "submitted program over arguments the request supplies. It is "
                "an extension of this tool, and answering it is no conformance "
                "to the profile."
            ),
            answering(
                (SOURCE, FUNCTION, ARGUMENTS),
                A_REFUSAL_OR_AN_ANSWER_ABOUT_A_SOURCE
                + (
                    Field.when(
                        "result",
                        "object",
                        "when the call answered a value",
                        "the value the function answered, written the way a "
                        "program writes it; a completed answer carrying a "
                        "refusal of a contract instead has none",
                    ),
                ),
            ),
        ),
        Operation(
            "machine",
            BeyondTheProfile(
                "SPEC.md lines 467-468 name seven operation categories and "
                "this operation is in none of them: it reads a machine "
                "descriptor, a separate versioned document, against the "
                "program the same request submits. It is an extension of "
                "this tool, and answering it is no conformance to the "
                "profile."
            ),
            answering(
                (SOURCE, DESCRIPTOR),
                AN_ANSWER_OF_THE_PROFILE
                + (
                    Field.when_completed(
                        "result",
                        "object",
                        "what each of the eight roles of the descriptor "
                        "resolved to in the submitted program -- under "
                        "'roles', one entry per role with the name the "
                        "descriptor gave it and the shape that name has -- "
                        "beside the descriptor version it was read in, under "
                        "'schema', and the assumptions the descriptor states, "
                        "under 'assumptions_stated'. Those assumptions are "
                        "read and checked by nothing. The answer says that "
                        "the roles resolve to declared types and checked "
                        "functions of the right shapes in this revision of "
                        "this program, and settles no claim about the machine "
                        "over its runs; 'what_this_says' in the result says "
                        "the same. The shape of a descriptor, and of every "
                        "role in it, is published under "
                        "'machine_descriptor_schema'",
                    ),
                ),
            ),
        ),
        Operation(
            "parse",
            InACategory("parsing"),
            answering(
                SOURCE_READING_REQUEST,
                AN_ANSWER_OF_THE_PROFILE
                + (
                    Field.when_completed(
                        "result",
                        "object",
                        "the syntax tree of the submitted program, "
                        "written in the shape this manifest publishes under "
                        "tree_schema: one node per part of the program, each "
                        "saying what it is and where it stands",
                    ),
                ),
            ),
        ),
        Operation(
            "format",
            InACategory("formatting"),
            answering(
                SOURCE_READING_REQUEST,
                AN_ANSWER_OF_THE_PROFILE
                + (
                    Field.when_completed(
                        "result",
                        "object",
                        "the one text the submitted program is written as, "
                        "under 'text': the same characters whichever way the "
                        "program was written, with every comment kept once "
                        "and in the order it was written. A comment stands "
                        "over the declaration that follows it, or after the "
                        "last declaration when none follows; so a comment "
                        "written inside a declaration rises out of it. The "
                        "'parse' operation stands a comment on the first node "
                        "that follows it at any depth instead, so the two "
                        "operations answer about different things and an "
                        "agent reading both must not expect one placing. A "
                        "requires or ensures clause with no condition in it "
                        "is written away, because core-0 reads it as the "
                        "empty conjunction, which is what an omitted clause "
                        "already means; every condition of a clause stands in "
                        "that one clause, in the order the source writes them",
                    ),
                ),
            ),
        ),
        Operation("build", InACategory("building"), NotAnsweredYet()),
    )
)


def the_language_published() -> dict:
    """Every type core-0 has and every operator, with the types each
    operator takes and the type it answers.

    Read from the checker's own tables, so what an agent writes a
    program from is what the checker reads it by.
    """
    return {
        "types": {core.name: core.published() for core in checker.CORE_TYPES},
        "operators": {
            name: operator.published()
            for name, operator in checker.BUILTIN_OPERATORS.items()
        },
    }


def published_parts(
    available: tuple[str, ...], unavailable: frozenset[str]
) -> dict:
    """The parts of the manifest this module owns, ready to be printed
    beside the parts the dispatcher already publishes."""
    return {
        **THE_OPERATIONS.published(available, unavailable),
        "language": the_language_published(),
    }
