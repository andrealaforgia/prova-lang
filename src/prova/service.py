"""Operation dispatch, manifest, response construction and diagnostics.

The only place that knows operation names.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from prova import (
    checker,
    evaluator,
    formatter,
    manifest,
    obligations,
    provenance,
    syntax,
    tree,
)
from prova.budgets import BudgetExhausted, Budgets, Exhaustion, Run, UnreadableBudget
from prova.reader import (
    LITERAL_DIGITS,
    READING_LIMIT,
    ReaderError,
    TooDeeplyNested,
    end_of,
    read_program,
    read_source,
)
from prova.values import render

AVAILABLE_OPERATIONS = (
    "check",
    "examples",
    "evaluate",
    "discover",
    "verify",
    "parse",
    "format",
)

# The operations that read a program from the `source` field of the
# request. Each of them is answered about a text, so each of them refuses
# a request whose `source` is not one.
SOURCE_READING_OPERATIONS = (
    "check",
    "examples",
    "evaluate",
    "verify",
    "parse",
    "format",
)
UNAVAILABLE_OPERATIONS = frozenset({"build"})

# What the tool answers when the source is not a program it can check.
# `invalid_program` means the source is a core-0 program that breaks a
# rule of core-0; `unsupported` means it is not a program of this profile
# at all (SPEC.md lines 51-54, 191-196).
UNSUPPORTED_STATUS = "unsupported"
UNSUPPORTED_CONSTRUCT = "unsupported_construct"

# What the tool answers when a budget it declares was passed while
# reading the request. Kept apart from `invalid_program`: the text may
# break no rule of core-0 at all, and SPEC.md line 505 requires that a
# limit never silently become a bound on what a program may mean.
RESOURCE_EXHAUSTED = "resource_exhausted"

# Every status an answered request carries, and what each one tells a
# caller. Published by the manifest, so the vocabulary is read from the
# tool. A request the service cannot read as a request at all never gets
# one of these: the command answers that itself, and the manifest says
# so beside this list.
STATUSES = {
    "completed": "the operation answered the request",
    "invalid_program": (
        "the source is a program of the core-0 profile and breaks one of the "
        "rules of core-0"
    ),
    UNSUPPORTED_STATUS: (
        "the source uses a construct the core-0 profile does not have, so it is "
        "outside this profile and no rule of core-0 was read over it"
    ),
    "invalid_input": (
        "the source is a core-0 program, but a value or a function name the "
        "request supplies is not one that program takes"
    ),
    RESOURCE_EXHAUSTED: (
        "a budget this tool declares was passed while reading the request, so "
        "the tool stopped there; no rule of core-0 was read over what it had, "
        "and the limit that was passed is published among the resource limits"
    ),
    "unavailable": "the operation is not one this tool answers yet",
}

# The operations whose answer carries the contract report. `check` is
# the answer whose completed status a reader can mistake for a
# meaningful result, so the report that says which functions promise
# nothing stands beside it; `verify` already answers that nothing was
# attempted, and an answer that refuses a program carries no report
# because no program was read.
CONTRACT_REPORT_OPERATIONS = ("check",)

# Every category a refusal carries, read from the kinds that say what
# each of them carries: the published list and the published shape are
# the same table, so a category can never be announced without its shape
# or carry a field the manifest does not name.
DIAGNOSTIC_CATEGORIES = tuple(checker.DIAGNOSTIC_KINDS)


# The two refusals in `handle` below are the only ones written as a
# dictionary here rather than built as a `checker.Diagnostic`: they
# answer about the request, not about a program, so they name no symbol,
# stand at no place in any text and carry no source revision. Deciding
# them must also enter nothing of the checker: an operation the tool
# does not answer attempts none of the work, which
# tests/properties/test_i1_s1_p4_p5.py observes from outside by tracing
# every module the process enters.
def handle(submitted: object, budgets: Budgets | None = None) -> dict:
    request = Request.read(submitted)
    if isinstance(request, MalformedRequest):
        return request.response_for(None)

    run = (budgets if budgets is not None else Budgets.declared()).start()
    try:
        return _answer(request, run)
    except BudgetExhausted as stopped:
        return budget_response(request.names_as_written(), stopped.exhaustion)


def _answer(request: "Request", run: Run) -> dict:
    """The answer to a request this tool could read, measured against
    the budgets of this run at every boundary between its stages."""
    operation = request.asks_for()
    run.stop_if_exhausted()
    if operation in SOURCE_READING_OPERATIONS:
        source = request.source()
        if isinstance(source, MalformedRequest):
            return source.response_for(operation)
        run.stop_if_source_too_large(source.characters)
        if operation == "check":
            return _run_check(source, run)
        if operation == "examples":
            return _run_examples(source, run)
        if operation == "verify":
            return _run_verify(source, run)
        if operation == "parse":
            return _run_parse(source, run)
        if operation == "format":
            return _run_format(source, run)
        asked = request.evaluation_asked()
        if isinstance(asked, MalformedRequest):
            return asked.response_for(operation)
        return _run_evaluate(source, asked, run)
    if operation == "discover":
        return _run_discover()
    if operation in UNAVAILABLE_OPERATIONS:
        return {
            "operation": operation,
            "status": "unavailable",
            "diagnostics": [
                {
                    "category": "operation_unavailable",
                    "reason": f"operation {operation!r} is not available in I1",
                }
            ],
        }
    return {
        "operation": request.names_as_written(),
        "status": "unavailable",
        "diagnostics": [
            {
                "category": "unknown_operation",
                "reason": (
                    f"operation {request.names_as_written()!r} is not recognized"
                ),
            }
        ],
    }


def answer_text(submitted: object, budgets: Budgets | None = None) -> str:
    """The text of the one answer to `submitted`, inside the answer
    budget of this run.

    The one place an answer becomes the characters a caller reads, so
    the size this tool measures is the size it would have printed. An
    answer too large is replaced whole: the first part of one carries no
    outcome, and a caller that parsed it would read a result this tool
    never finished writing. The refusal that replaces it is this tool's
    smallest answer and is printed whatever the budget says, which the
    manifest states beside the budget.
    """
    within = budgets if budgets is not None else Budgets.declared()
    answer = handle(submitted, within)
    text = json.dumps(answer)
    exhausted = within.answer_exhausted_by(text)
    if exhausted is None:
        return text
    return json.dumps(budget_response(answer.get("operation"), exhausted))


def budget_response(operation: object, exhaustion: Exhaustion) -> dict:
    """The one answer a run stopped inside a budget gives.

    It carries the status, and one refusal naming the budget, what it
    allowed and what was reached. There is no claim, no result and no
    revision of a source in it: the tool stopped inside a budget of its
    own and read no rule of the language over anything.
    """
    return {
        "operation": operation,
        "status": RESOURCE_EXHAUSTED,
        "diagnostics": [
            _diagnostic_dict(
                checker.Diagnostic(
                    exhaustion.category,
                    exhaustion.message,
                    about=checker.AboutTwoCounts(
                        exhaustion.budget, exhaustion.maximum, exhaustion.reached
                    ),
                )
            )
        ],
    }


def budgets_refused(unreadable: UnreadableBudget) -> dict:
    """The answer to a caller that wrote a budget this tool cannot read.

    The same answer a field of a request that cannot be read gets, named
    the same way: the variable to repair, and why.
    """
    return MalformedRequest.about(
        unreadable.variable, unreadable.reason
    ).response_for(None)


@dataclass(frozen=True)
class MalformedRequest:
    """Every field of a request this tool could not read, each named
    beside the reason it could not be read.

    Several, because the fields are independent: a client that wrote
    two of them wrongly learns about both in one answer rather than
    repairing one and meeting the next. It holds nothing but the list,
    so an answer about a request the tool never read cannot appear to
    report on a program.
    """

    defects: tuple[tuple[str, str], ...]

    @classmethod
    def about(cls, field: str, reason: str) -> "MalformedRequest":
        return cls(((field, reason),))

    @classmethod
    def not_readable_as_json(cls, why: str, place: str) -> "MalformedRequest":
        """The answer to text that is not a JSON request at all.

        Answered rather than reported as a failure of the tool: text
        that stops partway, or holds nothing, is a client that built its
        request wrongly, and telling it the tool broke sends it to look
        in the wrong place. A failure of the tool itself is a different
        thing and keeps the name it had.
        """
        return cls.about(
            "request",
            f"the text sent to this tool is not JSON{place}: {why}. This tool "
            "reads one JSON object per request from its standard input, and "
            "text that stops partway or holds nothing carries no request to "
            "read; send one complete JSON object carrying at least an "
            "'operation' field, and read the operations this tool answers "
            "from the 'discover' operation",
        )

    def and_also(self, other: "MalformedRequest") -> "MalformedRequest":
        return MalformedRequest(self.defects + other.defects)

    def response_for(self, operation: object) -> dict:
        return {
            "operation": operation,
            "status": "invalid_input",
            "diagnostics": [
                _diagnostic_dict(
                    checker.Diagnostic(
                        "malformed_request",
                        reason,
                        about=checker.AboutASymbol(field),
                    )
                )
                for field, reason in self.defects
            ],
        }


@dataclass(frozen=True)
class SubmittedText:
    """One text a request carries, known to be writable as UTF-8.

    Every text a request carries is turned back into bytes somewhere:
    the source is hashed for the revision an answer carries, every text
    is measured in bytes against the input budget, and all of them are
    written into the JSON answer. A character that cannot be written as
    UTF-8 -- half of a surrogate pair, which a client that decoded bytes
    badly sends -- has no bytes at all, and the step that reached for
    them used to end the run with nothing on standard output.

    Built only by `read` below, which refuses such a text by name, so a
    step that takes one of these is reached with a text that can be
    written and never has to defend itself. Python still lets a caller
    build one around any text by hand; nothing in this tool does, and
    the one path that reads a request refuses.
    """

    characters: str

    @classmethod
    def read(cls, field: str, written: str) -> "SubmittedText | MalformedRequest":
        try:
            written.encode("utf-8")
        except UnicodeEncodeError as half_a_character:
            return MalformedRequest.about(
                field,
                f"the {field!r} field of the request holds a character at "
                f"position {half_a_character.start} that cannot be written as "
                f"UTF-8 ("
                f"{written[half_a_character.start]!r}: "
                f"{half_a_character.reason}): this tool reads every text a "
                "request carries as the bytes it is written in -- it takes "
                "the revision an answer carries from those bytes and measures "
                "its budgets in them -- and half of a character has no bytes "
                "to read; send the field as text whose characters can all be "
                "written as UTF-8, writing a character outside the basic "
                "plane as the one character it is rather than as the two "
                "halves of its UTF-16 escape",
            )
        return cls(written)


@dataclass(frozen=True)
class FunctionName:
    """The name of a function a request asks this tool to call.

    Built only by reading a request, and only from a JSON string, so a
    step that takes one is reached with a name and never with a list or
    a number. Python still lets a caller build one around any value by
    hand; nothing in this tool does, and the one path that reads a
    request refuses.
    """

    spelling: str

    @classmethod
    def read(cls, asked: object) -> "FunctionName | MalformedRequest":
        if isinstance(asked, str):
            written = SubmittedText.read(manifest.FUNCTION.name, asked)
            if isinstance(written, MalformedRequest):
                return written
            return cls(written.characters)
        return MalformedRequest.about(
            manifest.FUNCTION.name,
            f"the 'function' field of the request holds "
            f"{type(asked).__name__}, not the name of a function: this tool "
            "looks a function up by the name its program declares for it, and "
            "a value of another kind names nothing to look up; send the "
            "function as one JSON string, and read the names a program "
            "declares by sending it to the 'check' operation first",
        )


@dataclass(frozen=True)
class ArgumentTexts:
    """The texts of the values a request supplies as arguments, one per
    parameter the function declares.

    Every element is known to be a text that can be written as UTF-8
    before the first of them is read, so a list holding one number, or
    one half of a character, refuses by name rather than breaking the
    reader on the way through.
    """

    texts: tuple[SubmittedText, ...]

    @classmethod
    def read(cls, supplied: object) -> "ArgumentTexts | MalformedRequest":
        if not isinstance(supplied, list):
            return MalformedRequest.about(
                manifest.ARGUMENTS.name,
                f"the 'arguments' field of the request holds "
                f"{type(supplied).__name__}, not a list of the texts of "
                "values: this tool reads one value from each text, and a "
                "value of another kind holds no list of texts to read; send "
                "the arguments as a JSON list of strings, one string per "
                "parameter the function declares, and an empty list when it "
                "declares none",
            )
        unreadable: list[tuple[str, str]] = []
        texts: list[SubmittedText] = []
        for place, written in enumerate(supplied):
            named = f"{manifest.ARGUMENTS.name}[{place}]"
            if not isinstance(written, str):
                unreadable.append(
                    (
                        named,
                        f"the argument at place {place} of the request holds "
                        f"{type(written).__name__}, not the text of a value: this "
                        "tool reads a value from the characters of each argument, "
                        "and a value of another kind holds no characters to read; "
                        "send that argument as one JSON string, writing the value "
                        "the way a program writes it, as \"(Clock 12)\" or \"7\"",
                    )
                )
                continue
            read = SubmittedText.read(named, written)
            if isinstance(read, MalformedRequest):
                unreadable.extend(read.defects)
                continue
            texts.append(read)
        if unreadable:
            return MalformedRequest(tuple(unreadable))
        return cls(tuple(texts))


@dataclass(frozen=True)
class EvaluationAsked:
    """What a request asks an evaluation to do: which function, and with
    which argument texts."""

    function: FunctionName
    arguments: ArgumentTexts


@dataclass(frozen=True)
class Request:
    """The one reader of a field of a submitted request.

    Nothing else in this tool reads a field, so a field holding a kind
    of value the tool cannot use is refused once, by name, before any
    work starts -- rather than by whichever step happened to reach for
    it first, in whatever way that step happened to break.
    """

    submitted: dict

    @classmethod
    def read(cls, submitted: object) -> "Request | MalformedRequest":
        if isinstance(submitted, dict):
            return cls(submitted)
        return MalformedRequest.about(
            "request",
            f"the request is {type(submitted).__name__}, not an object with "
            "fields: this tool reads the operation to run, and what to run it "
            "over, from named fields, and a value of another kind has none; "
            "send one JSON object carrying at least an 'operation' field, and "
            "read the operations this tool answers from the 'discover' "
            "operation",
        )

    def names_as_written(self) -> object:
        """The operation field exactly as the request wrote it, whatever
        kind of value that is, so a refusal quotes back what was sent."""
        return self.submitted.get("operation")

    def asks_for(self) -> str | None:
        """The operation this request asks for, or `None` when its
        operation field holds no name at all.

        A value of another kind names no operation this tool has, which
        is the same thing a misspelled name says, so both get the same
        answer and neither is read as a name by the steps below.
        """
        asked = self.names_as_written()
        return asked if isinstance(asked, str) else None

    def source(self) -> "SubmittedText | MalformedRequest":
        """The text of the program the request submits.

        Read before anything else about the request, because every later
        answer is about a text: the revision an answer carries is the
        revision of those characters, and a value of another kind, or a
        text that cannot be written as UTF-8, has none.
        """
        written = self.submitted.get(manifest.SOURCE.name, "")
        if isinstance(written, str):
            return SubmittedText.read(manifest.SOURCE.name, written)
        return MalformedRequest.about(
            manifest.SOURCE.name,
            f"the 'source' field of the request holds "
            f"{type(written).__name__}, not the text of a program: this tool "
            "reads a program from the characters of that field, and a value "
            "of another kind holds no characters to read; send the program as "
            "one JSON string, writing a line break as \\n",
        )

    def evaluation_asked(self) -> "EvaluationAsked | MalformedRequest":
        """Which function the request asks to call and with which
        argument texts, or every field of the two that could not be read.

        Both are read in one pass: they are independent, so a client
        that wrote both wrongly is told about both at once.
        """
        function = FunctionName.read(self.submitted.get(manifest.FUNCTION.name))
        arguments = ArgumentTexts.read(
            self.submitted.get(manifest.ARGUMENTS.name, [])
        )
        if isinstance(function, MalformedRequest):
            if isinstance(arguments, MalformedRequest):
                return function.and_also(arguments)
            return function
        if isinstance(arguments, MalformedRequest):
            return arguments
        return EvaluationAsked(function, arguments)


def _run_discover() -> dict:
    availability = {name: "available" for name in AVAILABLE_OPERATIONS}
    availability.update({name: "unavailable" for name in sorted(UNAVAILABLE_OPERATIONS)})
    return {
        "operation": "discover",
        "status": "completed",
        "claim": {"kind": "manifest", "scope": "this tool"},
        "diagnostics": [],
        "result": {
            "profile": {"name": "core-0", "coverage": "partial"},
            "operations": availability,
            "statuses": dict(STATUSES),
            "diagnostic_categories": list(DIAGNOSTIC_CATEGORIES),
            "contract_report": checker.contract_report_published(
                CONTRACT_REPORT_OPERATIONS
            ),
            "tree_schema": tree.SCHEMA.published(),
            "diagnostic_schemas": {
                category: checker.DIAGNOSTIC_KINDS[category].published()
                for category in DIAGNOSTIC_CATEGORIES
            },
            "documentation": {
                "evaluate": (
                    "A completed evaluate response means the function's postconditions "
                    "were checked and held for the supplied input; it is not a proof "
                    "for all inputs."
                ),
                "statuses": (
                    "Every status an answered request carries, and every "
                    "request is answered: text that is not JSON at all is "
                    "answered too, with 'invalid_input', so a caller never "
                    "has to tell a refusal from a tool that broke. "
                    "'tool_failure' is kept for a failure of this tool "
                    "itself, which is not an answer to a request, and is "
                    "therefore not one of the statuses listed."
                ),
                "diagnostic_schemas": (
                    "What a diagnostic of each category carries beside its "
                    "category and its sentence: the fields and the kind of "
                    "value each carries, where its place stands and what "
                    "that place points into, and whether it carries the revision "
                    "of a submitted source. A revision says which text the "
                    "diagnostic is about and claims nothing about that text: "
                    "a source the tool refused before checking it through "
                    "carries one too."
                ),
                "operation_schemas": (
                    "What each operation an agent may call takes and what its "
                    "answer carries: one entry per field, with the kind of "
                    "value it carries, when it is there and what it is for. "
                    "The operation field itself is not one of them: a request "
                    "whose operation field carries another kind of value, or "
                    "a name this tool does not have, names no operation at "
                    "all and is answered 'unavailable'."
                ),
                "integer_literals": (
                    f"An integer literal in a text this tool reads -- the "
                    f"source of a program or the value of an argument -- is "
                    f"read up to {LITERAL_DIGITS.maximum} digits long, and a "
                    "longer run of digits is refused where it stands with a "
                    "'syntax' refusal naming that length. The limit is on the "
                    "characters of a literal a text may write and not on what "
                    "a program may mean: an integer written inside it is read "
                    "and answered exactly, however far past 64 bits it is. "
                    f"{LITERAL_DIGITS.reason()}"
                ),
                "verify": (
                    "A completed verify response is an inventory only: it lists the "
                    "obligations the program owes and attempts none of them, so every "
                    "entry's result is not_attempted. This tool has no solver."
                ),
            },
            "resource_limits": {
                "enforced": True,
                "limits": {
                    READING_LIMIT.name: {
                        "maximum": READING_LIMIT.maximum,
                        "unit": "nested forms",
                        "status": RESOURCE_EXHAUSTED,
                        "category": checker.NESTING_LIMIT_EXCEEDED,
                        "reason": READING_LIMIT.reason(),
                    },
                    evaluator.EVALUATION_LIMIT.name: {
                        "maximum": evaluator.EVALUATION_LIMIT.maximum,
                        "unit": "evaluation steps standing inside one another",
                        "status": RESOURCE_EXHAUSTED,
                        "category": checker.EVALUATION_DEPTH_EXCEEDED,
                        "reason": evaluator.EVALUATION_LIMIT.reason(),
                    },
                },
                "budgets": Budgets.declared().published_for(
                    AVAILABLE_OPERATIONS, RESOURCE_EXHAUSTED
                ),
            },
            **manifest.published_parts(AVAILABLE_OPERATIONS, UNAVAILABLE_OPERATIONS),
        },
    }


@dataclass(frozen=True)
class SourceRevision:
    """The revision of one submitted source text: the SHA-256 of the
    exact bytes the request carried.

    The one thing that says which text an answer is about. A client
    recomputes it from what it sent, so two versions of a file are never
    confused for each other and evidence about one cannot certify the
    other.

    The hashing itself belongs to `provenance.Digest`, which this asks:
    the revision of a source and the digest over this tool's own
    description are one algorithm over two texts, and one place writes
    it.
    """

    digest: str

    @classmethod
    def of(cls, source: SubmittedText) -> "SourceRevision":
        """The revision of a text the request reader has already read.

        It takes the text as the reader built it, and not as characters
        a caller assembled: the bytes it hashes are known to exist
        because nothing but the reader builds one of these, and the
        reader refuses a text that has none.
        """
        return cls(provenance.Digest.of(source.characters).rendered())

    def rendered(self) -> str:
        return self.digest


def _source_digest(source: SubmittedText) -> str:
    return SourceRevision.of(source).rendered()


def _diagnostic_dict(
    diagnostic: checker.Diagnostic, revision: SourceRevision | None = None
) -> dict:
    """The one builder of the dictionary a client reads a refusal from.

    Every refusal of every operation comes through here, so a refusal of
    the reader and a refusal of a rule of core-0 reach a caller in the
    same shape, and nothing else in the tool writes a diagnostic.

    The revision of the text the request submitted is stamped here, in
    the one place every refusal passes, so no rule has to remember to
    carry it. It says which text the refusal is about and nothing else:
    an answer about a source the tool stopped reading still says which
    source that was.
    """
    kind = checker.DIAGNOSTIC_KINDS[diagnostic.category]
    entry = {"category": diagnostic.category, "reason": diagnostic.reason}
    if kind.says_which_text():
        entry["points_into"] = diagnostic.points_into
    if kind.revision == checker.ALWAYS:
        if revision is None:
            raise ValueError(
                f"a refusal of category {diagnostic.category!r} is being "
                "rendered without the revision of the text it is about, which "
                "its kind declares it carries: a client reads which version of "
                "its source the answer is about from that field; pass the "
                "SourceRevision of the submitted source, or declare the kind "
                "as carrying none"
            )
        entry["source_revision"] = revision.rendered()
    entry.update(diagnostic.about.fields())
    if diagnostic.location is not None:
        line, column = diagnostic.location
        entry["location"] = {"line": line, "column": column}
    if diagnostic.cycle is not None:
        entry["cycle"] = list(diagnostic.cycle.names())
    return entry


def _syntax_diagnostic(error: ReaderError | syntax.SyntaxError_) -> checker.Diagnostic:
    """The one diagnostic a source the tool cannot read as a core-0
    program carries.

    Every operation that reads source answers through this builder, so a
    source refused by the reader comes back the same way whichever
    operation met it, carrying the place the refusal stands at so a
    reader is sent to the line to repair.
    """
    return checker.Diagnostic("syntax", error.message, (error.line, error.column))


def _too_deep_to_run_diagnostic(
    refusal: evaluator.EvaluationTooDeep,
) -> checker.Diagnostic:
    """The one diagnostic a program the tool cannot run to the end
    carries: the limit beside the depth it reached, and the step that
    would have gone past it."""
    return checker.Diagnostic(
        checker.EVALUATION_DEPTH_EXCEEDED,
        refusal.message,
        (refusal.line, refusal.column),
        about=checker.AboutTwoCounts(
            evaluator.EVALUATION_LIMIT.name, refusal.limit, refusal.reached
        ),
    )


def _too_deep_to_run(
    operation: str, source: SubmittedText, refusal: evaluator.EvaluationTooDeep
) -> dict:
    return {
        "operation": operation,
        "status": RESOURCE_EXHAUSTED,
        "diagnostics": [
            _diagnostic_dict(
                _too_deep_to_run_diagnostic(refusal), SourceRevision.of(source)
            )
        ],
    }


def _too_deeply_nested_diagnostic(
    refusal: TooDeeplyNested, text: str
) -> checker.Diagnostic:
    """The one diagnostic a text that nests past the limit carries,
    whichever text it was.

    It names the limit the way the manifest names it, carries the limit
    beside the depth the text reached, and says which of the two texts a
    request holds the place stands in, so a caller is never left opening
    the wrong one.
    """
    return checker.Diagnostic(
        checker.NESTING_LIMIT_EXCEEDED,
        refusal.message,
        (refusal.line, refusal.column),
        about=checker.AboutTwoCounts(
            READING_LIMIT.name, refusal.limit, refusal.reached
        ),
        points_into=text,
    )


def _out_of_profile_diagnostic(
    refusal: syntax.UnsupportedConstruct,
) -> checker.Diagnostic:
    """The one diagnostic a source using a construct core-0 does not have
    carries: the construct named, why core-0 cannot give it a meaning,
    how to write the intent instead, and the place it stands at.
    """
    return checker.Diagnostic(
        UNSUPPORTED_CONSTRUCT,
        refusal.message,
        (refusal.line, refusal.column),
        about=checker.AboutAConstruct(refusal.construct.name),
    )


@dataclass(frozen=True)
class Refusal:
    """The one answer every operation that reads source gives when the
    source is not a core-0 program it can check: the status it carries,
    and the diagnostics that say why.

    It holds nothing else. There is no field for a claim, a result or a
    source digest, so an answer about a program the tool did not read
    through cannot appear to report one.
    """

    status: str
    diagnostics: tuple
    revision: SourceRevision

    def response_for(self, operation: str) -> dict:
        return {
            "operation": operation,
            "status": self.status,
            "diagnostics": [
                _diagnostic_dict(d, self.revision) for d in self.diagnostics
            ],
        }


def _checked_program(source: SubmittedText, run: Run):
    """The program `source` declares, checked against every rule of
    core-0 -- or the `Refusal` to answer with instead.

    Every operation that reads source asks here, so a source refused for
    one of them is refused the same way for all of them, and a caller
    moving between operations never meets two answers for one source.
    """
    revision = SourceRevision.of(source)
    try:
        program = syntax.parse_program(read_program(source.characters))
    except TooDeeplyNested as too_deep:
        return Refusal(
            RESOURCE_EXHAUSTED,
            (_too_deeply_nested_diagnostic(too_deep, "source"),),
            revision,
        )
    except syntax.UnsupportedConstruct as outside:
        return Refusal(
            UNSUPPORTED_STATUS, (_out_of_profile_diagnostic(outside),), revision
        )
    except (ReaderError, syntax.SyntaxError_) as error:
        return Refusal("invalid_program", (_syntax_diagnostic(error),), revision)

    run.stop_if_exhausted()
    diagnostics = checker.check_program(program)
    if diagnostics:
        return Refusal("invalid_program", tuple(diagnostics), revision)
    return program


def _run_check(source: SubmittedText, run: Run) -> dict:
    checked = _checked_program(source, run)
    if isinstance(checked, Refusal):
        return checked.response_for("check")
    program = checked

    return {
        "operation": "check",
        "status": "completed",
        "claim": {"kind": "static_check", "scope": "this input"},
        "source_digest": _source_digest(source),
        "diagnostics": [],
        "contract_report": checker.ContractReport.of(program).as_dict(),
    }


def _run_verify(source: SubmittedText, run: Run) -> dict:
    """The obligations the program owes, every one of them not attempted.

    Reads nothing but `source`, writes nothing and keeps nothing: asking
    twice changes neither the answer nor anything else.
    """
    checked = _checked_program(source, run)
    if isinstance(checked, Refusal):
        return checked.response_for("verify")
    program = checked

    return {
        "operation": "verify",
        "status": "completed",
        "claim": {"kind": "obligation_inventory", "scope": "this input"},
        "source_digest": _source_digest(source),
        "diagnostics": [],
        "result": {"inventory": obligations.inventory_for(program).as_dict()},
    }


def _run_parse(source: SubmittedText, run: Run) -> dict:
    """The tree the tool built for `source`.

    Reads the source through the rule every operation that reads one
    shares, so a source refused here is refused exactly as a check
    refuses it, and an answer that refuses carries no tree at all: a
    tree beside a refusal would read as a program this tool understood.

    The comments are asked of the reader again rather than carried
    through that shared rule: every other operation answers about the
    program alone, and widening what they all share for the one
    operation that reads prose would make every one of them carry it.
    """
    checked = _checked_program(source, run)
    if isinstance(checked, Refusal):
        return checked.response_for("parse")
    program = checked

    return {
        "operation": "parse",
        "status": "completed",
        "claim": {"kind": "syntax_tree", "scope": "this input"},
        "source_digest": _source_digest(source),
        "diagnostics": [],
        "result": {
            "tree": tree.tree_of(
                program, read_source(source.characters).comments
            )
        },
    }


def _run_format(source: SubmittedText, run: Run) -> dict:
    """The one text the submitted program is written as.

    Reads the source through the rule every operation that reads one
    shares, so a source refused here is refused exactly as a check
    refuses it, and an answer that refuses carries no text at all: text
    beside a refusal would read as a program this tool had understood
    and tidied, and an agent would write it to a file.

    The comments are asked of the reader again rather than carried
    through that shared rule, as `parse` already does and for the same
    reason: every other operation answers about the program alone, and
    widening what they all share for the two that read prose would make
    every one of them carry it.
    """
    checked = _checked_program(source, run)
    if isinstance(checked, Refusal):
        return checked.response_for("format")
    program = checked

    return {
        "operation": "format",
        "status": "completed",
        "claim": {"kind": "canonical_text", "scope": "this input"},
        "source_digest": _source_digest(source),
        "diagnostics": [],
        "result": {
            "text": formatter.canonical_text(
                program, read_source(source.characters).comments
            )
        },
    }


def _run_examples(source: SubmittedText, run: Run) -> dict:
    checked = _checked_program(source, run)
    if isinstance(checked, Refusal):
        return checked.response_for("examples")
    program = checked

    results = []
    for function in program.functions.values():
        for ordinal, example in enumerate(function.examples):
            entry = {
                "function": function.name,
                "ordinal": ordinal,
                "arguments": [render(a) for a in example.args],
                "expected": render(example.expected),
            }
            run.stop_if_exhausted()
            try:
                actual = evaluator.call_function(function, example.args, program)
            except evaluator.EvaluationTooDeep as too_deep:
                return _too_deep_to_run("examples", source, too_deep)
            except (evaluator.PreconditionViolation, evaluator.PostconditionViolation) as violation:
                entry["actual"] = None
                entry["passed"] = False
                entry["reason"] = str(violation)
            else:
                entry["actual"] = render(actual)
                entry["passed"] = evaluator.values_equal(actual, example.expected)
            results.append(entry)

    return {
        "operation": "examples",
        "status": "completed",
        "claim": {"kind": "examples", "scope": "declared examples"},
        "source_digest": _source_digest(source),
        "diagnostics": [],
        "result": {"examples": results},
    }


def _parse_value_text(text: SubmittedText) -> object:
    """The one value `text` writes, or the reader's refusal to read one.

    A refusal stands where the reader stopped in that text: at the value
    after the first when there are several, and at the end of the text
    when there is none.
    """
    forms = read_program(text.characters)
    if len(forms) != 1:
        extra = forms[1] if len(forms) > 1 else None
        line, column = (
            (extra.line, extra.column)
            if extra is not None
            else end_of(text.characters)
        )
        raise ReaderError(
            f"expected exactly one value, got {len(forms)}", line, column
        )
    return syntax.parse_value(forms[0])


def _declared_place(program, name: str) -> tuple[int, int]:
    """Where `program` declares the function `name`.

    A refusal about a call the request makes stands at the declaration
    it is a call to: the request carries no text of its own for a
    reader to open.
    """
    for declared in program.declarations.of_kind("function"):
        if declared.name == name:
            return (declared.line, declared.column)
    raise KeyError(name)


def _run_evaluate(source: SubmittedText, asked: EvaluationAsked, run: Run) -> dict:
    checked = _checked_program(source, run)
    if isinstance(checked, Refusal):
        return checked.response_for("evaluate")
    program = checked
    revision = SourceRevision.of(source)

    function_name = asked.function.spelling
    argument_texts = asked.arguments.texts
    function = program.functions.get(function_name)
    if function is None:
        return {
            "operation": "evaluate",
            "status": "invalid_input",
            "diagnostics": [
                _diagnostic_dict(
                    checker.Diagnostic(
                        "unknown_function",
                        f"no function named {function_name!r}",
                        about=checker.AboutASymbol(function_name),
                    ),
                    revision,
                )
            ],
        }

    place = _declared_place(program, function.name)
    try:
        args = tuple(_parse_value_text(text) for text in argument_texts)
    except TooDeeplyNested as too_deep:
        return {
            "operation": "evaluate",
            "status": RESOURCE_EXHAUSTED,
            "diagnostics": [
                _diagnostic_dict(
                    _too_deeply_nested_diagnostic(too_deep, "argument"), revision
                )
            ],
        }
    except (ReaderError, syntax.SyntaxError_) as error:
        return {
            "operation": "evaluate",
            "status": "invalid_input",
            "diagnostics": [
                _diagnostic_dict(
                    checker.Diagnostic(
                        "malformed_value",
                        error.message,
                        (error.line, error.column),
                        about=checker.AboutASymbol(function.name),
                        points_into="argument",
                    ),
                    revision,
                )
            ],
        }

    params = function.signature.params
    if len(args) != len(params):
        return {
            "operation": "evaluate",
            "status": "invalid_input",
            "diagnostics": [
                _diagnostic_dict(
                    checker.Diagnostic(
                        "arity_mismatch",
                        f"function {function_name!r} expects {len(params)} argument(s), "
                        f"got {len(args)}",
                        place,
                        about=checker.AboutTwoCounts(
                            function.name, len(params), len(args)
                        ),
                    ),
                    revision,
                )
            ],
        }

    try:
        for arg, parameter in zip(args, params):
            evaluator.check_value_type(
                arg, parameter.type_name, program, f"argument {parameter.name!r}"
            )
    except evaluator.MalformedValue as error:
        return {
            "operation": "evaluate",
            "status": "invalid_input",
            "diagnostics": [
                _diagnostic_dict(
                    checker.Diagnostic(
                        "malformed_value",
                        error.reason,
                        place,
                        about=checker.AboutASymbol(function.name),
                        points_into="source",
                    ),
                    revision,
                )
            ],
        }
    except evaluator.IllTypedValue as error:
        return {
            "operation": "evaluate",
            "status": "invalid_input",
            "diagnostics": [
                _diagnostic_dict(
                    checker.Diagnostic(
                        "ill_typed_value",
                        error.reason,
                        place,
                        about=checker.AboutASymbol(function.name),
                    ),
                    revision,
                )
            ],
        }

    run.stop_if_exhausted()
    try:
        result = evaluator.call_function(function, args, program)
    except evaluator.EvaluationTooDeep as too_deep:
        return _too_deep_to_run("evaluate", source, too_deep)
    except evaluator.PreconditionViolation as violation:
        return {
            "operation": "evaluate",
            "status": "completed",
            "claim": {"kind": "evaluation", "scope": "this input"},
            "source_digest": _source_digest(source),
            "diagnostics": [
                _diagnostic_dict(
                    checker.Diagnostic(
                        "precondition_violation",
                        str(violation),
                        place,
                        about=checker.AboutASymbol(function.name),
                    ),
                    revision,
                )
            ],
        }
    except evaluator.PostconditionViolation as violation:
        return {
            "operation": "evaluate",
            "status": "completed",
            "claim": {"kind": "evaluation", "scope": "this input"},
            "source_digest": _source_digest(source),
            "diagnostics": [
                _diagnostic_dict(
                    checker.Diagnostic(
                        "postcondition_violation",
                        str(violation),
                        place,
                        about=checker.AboutASymbol(function.name),
                    ),
                    revision,
                )
            ],
        }

    return {
        "operation": "evaluate",
        "status": "completed",
        "claim": {"kind": "evaluation", "scope": "this input"},
        "source_digest": _source_digest(source),
        "diagnostics": [],
        "result": {"value": render(result)},
    }
