"""Operation dispatch, manifest, response construction and diagnostics.

The only place that knows operation names.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from prova import (
    building,
    checker,
    discharge,
    encoding,
    evaluator,
    examples,
    formatter,
    induction,
    machine,
    manifest,
    obligations,
    provenance,
    runtime,
    solving,
    syntax,
    tree,
    verdict,
)
from prova.budgets import (
    LOWERED_WITH,
    BudgetExhausted,
    Budgets,
    Exhaustion,
    Run,
    UnreadableBudget,
)
from prova.reader import (
    LITERAL_DIGITS,
    READING_LIMIT,
    ReaderError,
    TooDeeplyNested,
    end_of,
    read_program,
    read_source,
)
from prova.values import WRITTEN_DIGITS, TooLargeToWrite, render

AVAILABLE_OPERATIONS = (
    "check",
    "examples",
    "evaluate",
    "discover",
    "verify",
    "parse",
    "format",
    "machine",
    "step",
    "build",
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
    "machine",
    "step",
    "build",
)
# No operation of this tool is refused for not being answered yet. The
# answer below and the category it carries stay where they are, so an
# operation added without one keeps a refusal that says exactly that.
UNAVAILABLE_OPERATIONS = frozenset()

# The profile this tool answers for, written once: the manifest publishes
# it, and the digest of what an answer stands on is taken over it.
THE_PROFILE = {"name": "core-0", "coverage": "partial"}

# What this tool reports when it failed inside itself. Deliberately not
# one of the statuses below: those are the statuses of an answered
# request, and a failure of this tool is not an answer to one (SPEC.md
# lines 280-284).
TOOL_FAILURE = "tool_failure"

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
    verdict.NOT_VERIFIED: (
        "the source is a core-0 program and the whole of it was not shown: "
        "an operation that publishes something only for a program that was "
        "shown whole -- a build -- published nothing, and the refusal names "
        "what stopped it. It says nothing against the program itself: no "
        "rule of core-0 was broken, and the 'verify' operation answers the "
        "whole inventory for the same source"
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

    unwritable = request.unwritable_operation()
    if unwritable is not None:
        return unwritable.response_for(None)

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
            descriptor = request.machine_asked_if_sent()
            if isinstance(descriptor, MalformedRequest):
                return descriptor.response_for(operation)
            return _run_verify(source, descriptor, run)
        if operation == "parse":
            return _run_parse(source, run)
        if operation == "format":
            return _run_format(source, run)
        if operation == "machine":
            descriptor = request.machine_asked()
            if isinstance(descriptor, MalformedRequest):
                return descriptor.response_for(operation)
            return _run_machine(source, descriptor, run)
        if operation == "step":
            driving = request.step_asked()
            if isinstance(driving, MalformedRequest):
                return driving.response_for(operation)
            return _run_step(source, driving, run)
        if operation == "build":
            asked = request.build_asked()
            if isinstance(asked, MalformedRequest):
                return asked.response_for(operation)
            return _run_build(source, asked, run)
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

    It is also the outermost boundary of this tool: a failure of the tool
    itself gets no further than here. It is answered as a failure, rather
    than reaching a caller as a run that broke, or as a status of an
    answered request, which would say something was decided about the
    program.
    """
    within = budgets if budgets is not None else Budgets.declared()
    try:
        answer = handle(submitted, within)
        text = printable_answer(answer)
    except Exception as failure:  # noqa: BLE001 - the tool, not the request
        return printable_answer(tool_failure(failure))
    exhausted = within.answer_exhausted_by(text)
    if exhausted is None:
        return text
    return printable_answer(budget_response(answer.get("operation"), exhausted))


def printable_answer(answer: dict) -> str:
    """The characters of one answer, or of the refusal that replaces an
    answer carrying a text this tool cannot write.

    The one place an answer becomes the text a caller reads. Every text
    a request carries is already read by a rule that refuses half a
    character by name; this stands behind all of them, so that a text no
    reader named can never leave this tool and fail in the client that
    reads it instead.
    """
    found = _half_a_character_anywhere_in(answer)
    if found is None:
        return json.dumps(answer)
    _, half_a_character = found
    return json.dumps(
        MalformedRequest.about(
            "request",
            "this tool was about to answer with a text whose character at "
            f"position {half_a_character.start} cannot be written as UTF-8 "
            f"({half_a_character.reason}): every text a request carries is "
            "read by a rule that refuses such a character and names the field "
            "it stands in, so an answer still holding one would be read by a "
            "client that could not write it out again. The text is not "
            "repeated here. Send the request again with every text written as "
            "characters that can be written as UTF-8, and report this answer "
            "if the request you send carries none",
        ).response_for(None)
    )


def _half_a_character_anywhere_in(
    value: object,
) -> "tuple[str, UnicodeEncodeError] | None":
    """The first text anywhere inside a value that cannot be written as
    UTF-8, with the character that cannot be written, or `None`.

    The one walk over a value a request or an answer carries: keys,
    texts and the texts inside a list or an object alike. The answer
    about to be printed asks it for the position, and the reader of a
    field asks it for the text to name.
    """
    if isinstance(value, str):
        half_a_character = SubmittedText.half_a_character_in(value)
        return None if half_a_character is None else (value, half_a_character)
    if isinstance(value, dict):
        for key, held in value.items():
            for part in (key, held):
                found = _half_a_character_anywhere_in(part)
                if found is not None:
                    return found
        return None
    if isinstance(value, list):
        for held in value:
            found = _half_a_character_anywhere_in(held)
            if found is not None:
                return found
    return None


def tool_failure(failure: Exception) -> dict:
    """The one answer a run that failed inside this tool gives.

    It carries the status no answered request carries, and one refusal
    naming what broke. There is no claim, no result and no revision of a
    source in it: the tool stopped on a failure of its own, read no rule
    of the language over anything, and must not appear to report on a
    program.

    The operation is left unnamed. Reading the request is one of the
    things that can fail here, so the name would be read from the very
    thing that broke.
    """
    return {
        "operation": None,
        "status": TOOL_FAILURE,
        "diagnostics": [
            _diagnostic_dict(
                checker.Diagnostic(
                    TOOL_FAILURE,
                    "the tool failed while it was answering: "
                    f"{type(failure).__name__}: {failure}. This is a failure "
                    "of this tool itself, not a statement about any program: "
                    "nothing was read through and nothing here reports on the "
                    "source the request carried. Send the request again, and "
                    "report it with the failure named here if it fails a "
                    "second time",
                )
            )
        ],
    }


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

    @staticmethod
    def half_a_character_in(written: str) -> "UnicodeEncodeError | None":
        """The first character of `written` that cannot be written as
        UTF-8, or `None`.

        The one place this tool decides whether a text can be written.
        The fields of a request ask it through `read` below; the
        variables of the environment and the answer about to be printed
        ask it directly, because neither is a field of a request and
        neither is owed that sentence.
        """
        try:
            written.encode("utf-8")
        except UnicodeEncodeError as half_a_character:
            return half_a_character
        return None

    @classmethod
    def read(cls, field: str, written: str) -> "SubmittedText | MalformedRequest":
        half_a_character = cls.half_a_character_in(written)
        if half_a_character is not None:
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
class RequiredText:
    """One field of a request that must carry a text, and what that text
    is read as.

    The field is named once, in the manifest, and the refusal sends a
    caller to that name: the reader and the published shape cannot drift
    apart. The sentence that says what the text is for belongs to the
    field, so one object answers both what a caller must send and why.
    """

    field: object
    read_as: str
    what_to_send: str

    def read(self, written: object) -> "SubmittedText | MalformedRequest":
        """The text of this field, or the refusal naming it.

        It is handed the value the one reader of a submitted request
        pulled out for it: a field of a request is read in one place,
        and this says only what that field must be.
        """
        if isinstance(written, str):
            return SubmittedText.read(self.field.name, written)
        return MalformedRequest.about(
            self.field.name,
            f"the {self.field.name!r} field of the request carries "
            f"{type(written).__name__} and not {self.read_as}: "
            f"{self.what_to_send}",
        )


ENTRY_ASKED = RequiredText(
    manifest.ENTRY,
    "the text of a name",
    "this tool invokes the function the submitted program declares under "
    "that name, and a value of another kind names nothing to invoke; send "
    "the entry as one JSON string, and read the names a program declares by "
    "sending it to the 'check' operation first",
)
OUTPUT_FILE_ASKED = RequiredText(
    manifest.OUTPUT_FILE,
    "the text of a path",
    "this tool writes one artefact to the characters of that field, and a "
    "value of another kind has no characters to open; send the path as one "
    "JSON string naming a file inside a directory that already exists",
)


STATE_ASKED = RequiredText(
    manifest.STATE,
    "the text of a value",
    "this tool drives the machine from the value that text writes, and a "
    "value of another kind holds no characters to read; send the state as "
    'one JSON string, writing the value the way a program writes it, as '
    '"(Clock 12)"',
)


@dataclass(frozen=True)
class EventTexts:
    """The texts of the events a request asks a machine to be driven
    through, in the order they are to be driven.

    Every element is known to be a text that can be written as UTF-8
    before the first of them is read, and there is at least one: a
    request carrying none asks for no transition, and a state published
    beside it would read as a transition that happened.
    """

    texts: tuple[SubmittedText, ...]

    @classmethod
    def read(cls, submitted: object) -> "EventTexts | MalformedRequest":
        if not isinstance(submitted, list):
            return MalformedRequest.about(
                manifest.EVENTS.name,
                f"the {manifest.EVENTS.name!r} field of the request holds "
                f"{type(submitted).__name__}, not a list of the texts of "
                "events: this tool drives one event per text, in the order "
                "the list writes them, and a value of another kind holds no "
                "list to read; send the events as a JSON list of strings, one "
                "string per event, each writing a value of the type the "
                'descriptor names as its event, as "(Tick)"',
            )
        if not submitted:
            return MalformedRequest.about(
                manifest.EVENTS.name,
                f"the {manifest.EVENTS.name!r} field of the request holds an "
                "empty list, and this tool drives a machine one event at a "
                "time: a request carrying no event asks for no transition, "
                "and a state answered beside it would read as a transition "
                "that happened while nothing ran; send at least one event, "
                'each as one JSON string, as "(Tick)"',
            )
        unreadable: list[tuple[str, str]] = []
        texts: list[SubmittedText] = []
        for place, written in enumerate(submitted):
            named = f"{manifest.EVENTS.name}[{place}]"
            if not isinstance(written, str):
                unreadable.append(
                    (
                        named,
                        f"the event at place {place} of the request holds "
                        f"{type(written).__name__}, not the text of a value: "
                        "this tool reads one event from the characters of each "
                        "entry, and a value of another kind holds no "
                        "characters to read; send that event as one JSON "
                        'string, as "(Tick)"',
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
class StepAsked:
    """What a request asks a run to do: which descriptor to drive, from
    which state and through which events."""

    descriptor: "machine.Descriptor"
    state: SubmittedText
    events: EventTexts


@dataclass(frozen=True)
class BuildAsked:
    """What a request asks a build to do: which function the artefact
    invokes, and which file to write it to."""

    entry: SubmittedText
    output_file: SubmittedText


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

    def unwritable_operation(self) -> "MalformedRequest | None":
        """The refusal to answer a request whose operation field carries
        a text this tool cannot write, or `None`.

        Read before anything else about the request: the operation a
        request asks for is the one text of it that an answer carries
        back whatever happens, so a text that cannot be written must
        never get that far.
        """
        return _unwritable_text_in("operation", self.names_as_written())

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

    def machine_asked(self) -> "machine.Descriptor | MalformedRequest":
        """The descriptor the request submits, read field by field, or
        every field of it that could not be read.

        Read here, before the program: a request this tool cannot read
        is answered about the request, and no rule of core-0 is read over
        the source for it. The document itself is read by the module
        that owns its shape; this is where its refusals become the one
        refusal every unreadable field of a request gets.
        """
        read = machine.Descriptor.read(
            self.submitted.get(manifest.DESCRIPTOR.name), _unwritable_reason_for
        )
        if isinstance(read, machine.DescriptorDefects):
            return MalformedRequest(read.defects)
        return read

    def step_asked(self) -> "StepAsked | MalformedRequest":
        """Which machine the request asks to drive, from which state and
        through which events, or every field of the four that could not
        be read.

        All of them are read in one pass, as an evaluation's two fields
        are: they are independent, so a client that wrote several wrongly
        is told about all of them at once rather than repairing one and
        meeting the next.
        """
        defects: MalformedRequest | None = None
        descriptor = self.machine_asked()
        if isinstance(descriptor, MalformedRequest):
            defects = descriptor
        state = STATE_ASKED.read(self.submitted.get(manifest.STATE.name))
        if isinstance(state, MalformedRequest):
            defects = state if defects is None else defects.and_also(state)
        events = EventTexts.read(self.submitted.get(manifest.EVENTS.name))
        if isinstance(events, MalformedRequest):
            defects = events if defects is None else defects.and_also(events)
        if defects is not None:
            return defects
        return StepAsked(descriptor, state, events)

    def build_asked(self) -> "BuildAsked | MalformedRequest":
        """Which function the artefact is to invoke and which file to
        write it to, or every field of the two that could not be read.

        Both are read in one pass, as an evaluation's two fields are: a
        client that wrote both wrongly is told about both at once.
        """
        entry = ENTRY_ASKED.read(self.submitted.get(manifest.ENTRY.name))
        output_file = OUTPUT_FILE_ASKED.read(
            self.submitted.get(manifest.OUTPUT_FILE.name)
        )
        if not isinstance(output_file, MalformedRequest):
            unusable = building.Destination.unusable_text(output_file.characters)
            if unusable is not None:
                output_file = MalformedRequest.about(
                    manifest.OUTPUT_FILE.name, unusable
                )
        if isinstance(entry, MalformedRequest):
            if isinstance(output_file, MalformedRequest):
                return entry.and_also(output_file)
            return entry
        if isinstance(output_file, MalformedRequest):
            return output_file
        return BuildAsked(entry, output_file)

    def machine_asked_if_sent(self) -> "machine.Descriptor | MalformedRequest | None":
        """The descriptor the request submits, or nothing at all when it
        sends no descriptor field.

        The field is asked for by presence and not by what it holds: a
        request that sends nothing there is answered about its program
        alone, and a request that sends anything there has it read by
        the rule above -- so a field holding a value of another kind is
        refused by name rather than taken for a request that sent none.
        """
        if manifest.DESCRIPTOR.name not in self.submitted:
            return None
        return self.machine_asked()

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
        "stands_on": _stands_on(),
        "diagnostics": [],
        "result": {
            "profile": THE_PROFILE,
            "operations": availability,
            "statuses": dict(STATUSES),
            "diagnostic_categories": list(DIAGNOSTIC_CATEGORIES),
            "contract_report": checker.contract_report_published(
                CONTRACT_REPORT_OPERATIONS
            ),
            "tree_schema": tree.SCHEMA.published(),
            "machine_descriptor_schema": machine.published_schema(),
            "solver": provenance.the_solver_it_requires(),
            "encoding": {
                "version": encoding.VERSION,
                "primitives": encoding.published_primitives(),
                "documented_in": encoding.DOCUMENTED_IN,
                "fragment": (
                    "What the translation covers: quantifier-free reasoning "
                    "over the booleans, linear arithmetic over the unbounded "
                    "whole numbers of core-0, the non-recursive records and "
                    "unions it declares, and the expansion of calls, which "
                    "cannot be cyclic in this profile. Multiplication only "
                    "where one operand is written as a literal. An obligation "
                    "needing anything else -- a let binding, a pattern "
                    "carrying patterns of its own, the product of two unknown "
                    "numbers -- is answered 'unknown' with that reason and is "
                    "never translated. The meaning of every primitive above, "
                    "and why settling one of these claims settles the claim "
                    "the source makes, is written out in the document named "
                    "here."
                ),
            },
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
                "step": (
                    "What driving a machine answers, and what it does not. "
                    "The run drives one event at a time over one state: the "
                    f"{machine.INVARIANT!r} role is asked first, because a "
                    "machine is defined only from the states its invariant is "
                    "true at, and a state the request sent that it excludes is "
                    f"refused with '{checker.STATE_OUTSIDE_INVARIANT}' before "
                    "anything runs. The "
                    f"{machine.ADMISSIBLE!r} role is asked next: an event it "
                    f"refuses is published as '{runtime.BOUNDARY_REJECTION}', "
                    "nothing is run for it and the state stays as it was. An "
                    "event it admits is run through the "
                    f"{machine.STEP!r} role and published as "
                    f"'{runtime.TRANSITION}', with the outcome the step "
                    "answered beside the state the "
                    f"{machine.STATE_OF!r} role read off it. The business "
                    "result of that machine -- an acceptance flag of its own, "
                    "say -- stands inside that outcome, and no rule of this "
                    "tool reads it: a rejected request of the machine is a "
                    f"'{runtime.TRANSITION}' like any other, and it is not a "
                    f"'{runtime.BOUNDARY_REJECTION}'. A sequence stops at the "
                    "first event it does not drive, which is either of those "
                    "two cases -- the second being a state a transition "
                    "published and the invariant excludes, published as "
                    f"'{runtime.STATE_OUTSIDE_INVARIANT}' -- and 'stopped_at' "
                    "then names the position, the reason, the role that "
                    "decided it and how many events were never attempted. "
                    "A contract of a role's own function that refuses the "
                    "values the run calls it with stops the sequence too, "
                    f"under the reason '{runtime.CONTRACT_REFUSED}': the "
                    "answer carries the located "
                    f"'{runtime.PRECONDITION_VIOLATION}' or "
                    f"'{runtime.POSTCONDITION_VIOLATION}' refusal beside the "
                    "result, which publishes the transitions that ran before "
                    "that event and the state they left -- no entry stands "
                    "for the event itself, because nothing of the machine "
                    "was decided there. "
                    "Every event the request carries is read as a value of "
                    "the declared type before the first of them is driven, so "
                    "a request carrying one text this tool cannot read drives "
                    "nothing at all. The answer is about the values the named "
                    "functions answered for this state and these events, in "
                    "this revision of this program. It settles nothing about "
                    "a host that would carry the events, and nothing about "
                    "the machine over its other runs; 'what_this_says' in the "
                    "result says the same, and the assumptions the descriptor "
                    "states are carried as stated and checked by nothing."
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
                "request_nesting": (
                    f"This tool reads a request whose own JSON nests at most "
                    f"{REQUEST_NESTING.maximum} arrays and objects inside one "
                    "another, counting the request object itself. A deeper "
                    "request is answered 'invalid_input' with a "
                    "'malformed_request' refusal naming the request, before "
                    "any reader turns the text into fields, and no rule of "
                    f"core-0 is read over it. {REQUEST_NESTING.reason()}"
                ),
                "computed_integers": (
                    f"An integer a run of this tool computes is written into "
                    f"an answer up to {WRITTEN_DIGITS.maximum} digits long, "
                    "counted the way an integer literal of a source is "
                    "counted: every digit of the number, leading zeros and "
                    "all, with the sign left out, so a negative result of "
                    f"{WRITTEN_DIGITS.maximum} digits is written too. A "
                    "longer result is answered 'resource_exhausted' with a "
                    f"'{checker.WRITTEN_DIGITS_EXCEEDED}' refusal standing at "
                    "the function that computed it, carrying the limit beside "
                    "the digits the result reached and no result at all. The "
                    "limit is on the digits an answer writes and not on what a "
                    "program may mean: an integer under it is kept and "
                    "answered exactly, however far past 64 bits it stands. "
                    f"{WRITTEN_DIGITS.reason()}"
                ),
                "stands_on": (
                    "What an answer stands on, and when it stops standing on "
                    "it. A completed answer carries 'source_digest', the "
                    "SHA-256 of the exact characters the request sent, and "
                    "'stands_on.dependency_digest', the digest of this tool "
                    "and of the language it reads. The answer is about that "
                    "revision of that source, read by that tool, and about "
                    "nothing else: before using an answer you kept, compute "
                    "the SHA-256 of the source you hold now and read this "
                    "manifest again, and ask once more when either of the two "
                    "differs. One operation carries no such block: "
                    "'evaluate', which SPEC.md names in none of its operation "
                    "categories and which is this tool's own, answers with "
                    "its claim and its source revision alone."
                ),
                "verify": (
                    "A completed verify response is the inventory of the obligations "
                    "the program owes, each beside what became of it. Under 'result' "
                    "an entry stands as 'proved', 'disproved', 'unknown' or "
                    "'not_attempted'; under 'execution_status' it says what happened "
                    "to the attempt. The two are read apart: an entry nothing ran is "
                    "not an entry nothing is owed for. An entry proved says under "
                    "'discharged_by' whether a solver was asked or a rule of core-0 "
                    "settled it, an entry left unsettled carries the reason, and an "
                    "entry disproved carries an input that breaks it and that this "
                    "tool refuses when it runs the program over it. Nothing is "
                    "skipped: every obligation listed carries one of those words. The "
                    "answer carries 'trust' when a solver answered about at least "
                    "one obligation, and not otherwise. Three kinds of answer carry "
                    "none: one whose every obligation was settled by a rule of "
                    "core-0, one whose obligations were all left outside what this "
                    "tool translates, and one that needed a solver and could not "
                    "load it -- in that last case a solver was reached for and "
                    "answered nothing, so there is no word of its to disclose. All "
                    "three say what stood behind them under 'stands_on' instead. "
                    "Where it is carried, 'trust' says that a proved obligation "
                    "rests on the solver's word and that this tool does not check it "
                    "again; the solver and the translation it names are the ones under "
                    "'stands_on'. Beside the inventory the answer carries 'aggregate', "
                    "where the program as a whole stands. It says 'verified' when, and "
                    "only when, the inventory is not empty and every obligation of it "
                    "is 'proved', every "
                    "example the program declares was run here and passed, and the "
                    "static checks passed; anything else says 'not_verified' and names "
                    "what stopped it. The examples are run rather than read off the "
                    "obligations about them: no kind of evidence upgrades another. An "
                    "answer whose solver could not be loaded is 'not_verified' beside "
                    "an execution status of 'tool_failure', while the answer itself "
                    "stays 'completed': the inventory is still there to read, and a "
                    "failure of this tool is never a statement about the program. The "
                    "shape published under operation_schemas for 'verify' says the "
                    "same."
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


def _unwritable_reason_for(field: str, written: str) -> str | None:
    """Why `written` cannot be written as UTF-8 under the name `field`,
    or `None` when it can.

    The one sentence this tool gives for such a text, read from the one
    unit that decides it, so a text inside a descriptor is refused in the
    same words as a text sent as a field of the request itself.
    """
    read = SubmittedText.read(field, written)
    if isinstance(read, MalformedRequest):
        return read.defects[0][1]
    return None


def _unwritable_text_in(field: str, value: object) -> "MalformedRequest | None":
    """The refusal naming the first text inside `value` that cannot be
    written as UTF-8, or `None`.

    A field of a request carries a text, or a list or an object holding
    texts; all of them are copied into the answer that quotes the field
    back, so all of them are read by the one walk and refused by the one
    reader.
    """
    found = _half_a_character_anywhere_in(value)
    if found is None:
        return None
    written, _ = found
    read = SubmittedText.read(field, written)
    return read if isinstance(read, MalformedRequest) else None


@dataclass(frozen=True)
class RequestNesting:
    """How many arrays and objects a request may nest inside one
    another, and the name a caller reads that number under.

    One object holds the number, as the nesting limit of the reader
    does: the command asks it whether a request has passed it before
    any reader turns the text into fields, and the manifest documents
    the same object's number, so what a caller is promised and what the
    tool does cannot drift apart.
    """

    maximum: int
    name: str = "request_nesting"

    def reason(self) -> str:
        """Why the number is the number it is, for a caller whose
        generator writes the requests it sends."""
        return (
            f"the reader that turns the text of a request into fields calls "
            f"itself once per array and once per object, so {self.maximum} of "
            "them cost a small part of the 1000 frames Python allows by "
            "default: the refusal is reached with room to spare, and the "
            "interpreter's own limit is left where it stands. It is also far "
            "above every request this tool answers, the deepest of which -- an "
            "evaluate request carrying its arguments -- nests 2."
        )

    def deepest_of(self, text: str) -> int:
        """How many arrays and objects `text` nests inside one another,
        counted without reading it as JSON.

        Counting stops as soon as the limit is passed: a text written to
        exhaust a reader is refused by its first characters and not by
        all of them. Characters inside a quoted text are not brackets of
        the request, so they are stepped over here exactly as the JSON
        reader steps over them.
        """
        depth = 0
        deepest = 0
        inside_a_text = False
        escaped = False
        for character in text:
            if inside_a_text:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == '"':
                    inside_a_text = False
                continue
            if character == '"':
                inside_a_text = True
            elif character in "[{":
                depth += 1
                if depth > deepest:
                    deepest = depth
                    if deepest > self.maximum:
                        return deepest
            elif character in "]}":
                depth -= 1
        return deepest

    def refusal_for(self, text: str) -> "MalformedRequest | None":
        """The refusal to read a request nesting deeper than this tool
        reads, or `None`."""
        deepest = self.deepest_of(text)
        if deepest <= self.maximum:
            return None
        return MalformedRequest.about(
            "request",
            f"the text sent to this tool nests at least {deepest} arrays and "
            f"objects inside one another, and this tool reads a request that "
            f"nests {self.maximum}: {self.reason()}; the tool stopped counting "
            "there, so it never read which operation was asked for and says "
            f"nothing about any program. Send a request that nests at most "
            f"{self.maximum} arrays and objects, and read that number from "
            "what the 'discover' operation documents about the nesting of a "
            "request",
        )


# How deeply a request this tool answers may nest its own arrays and
# objects, counting the request object itself.
REQUEST_NESTING = RequestNesting(64)


def unwritable_budget_variable(environment) -> "MalformedRequest | None":
    """The refusal to read a budget variable whose name or whose value
    cannot be written as UTF-8, or `None`.

    Asked before the budgets are read, because the answer to a variable
    this tool cannot read names that variable and quotes what was
    written in it: a name or a value half of whose character has no
    bytes would reach a caller that could not write it out again. The
    text is never repeated; the caller is given the place to look.
    """
    for name in sorted(environment, key=lambda written: written.encode(
        "utf-8", "surrogatepass"
    )):
        if not name.startswith(LOWERED_WITH):
            continue
        half_a_character = SubmittedText.half_a_character_in(name)
        if half_a_character is not None:
            return MalformedRequest.about(
                LOWERED_WITH,
                "a variable of this process's environment whose name begins "
                f"{LOWERED_WITH} holds a character at position "
                f"{half_a_character.start} that cannot be written as UTF-8 "
                f"({half_a_character.reason}): this tool reads a budget from "
                "such a variable and names the one to repair in its answer, "
                "and a name half of whose character has no bytes cannot be "
                "named back -- so it is not repeated here. Unset the variable "
                "whose name is not UTF-8 text, and read the four names this "
                "tool reads from the 'lower_with' entry of each budget the "
                "'discover' operation states",
            )
        half_a_character = SubmittedText.half_a_character_in(environment[name])
        if half_a_character is not None:
            return MalformedRequest.about(
                name,
                f"the budget written in {name} holds a character at position "
                f"{half_a_character.start} that cannot be written as UTF-8 "
                f"({half_a_character.reason}): this tool reads one whole "
                "number written in the digits 0 to 9 from that variable, and "
                "half of a character is not one of them -- it is not repeated "
                "here, because a caller reading this answer could not write it "
                "out again. Write the budget as a whole number, or leave the "
                "variable unset to run under the number this tool declares",
            )
    return None


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


def _stands_on(standing: provenance.SolverStanding | None = None) -> dict:
    """What a completed answer stands on: the digest of this tool and of
    the language it reads, and the versions behind both.

    The one place an answer learns it, and the same place the manifest
    publishes it from, so the digest a client keeps beside an answer and
    the digest it reads from this tool later cannot drift apart.

    An answer that read no program through carries none of it: there is
    nothing it stands on, and a block there would say otherwise.
    """
    return provenance.Provenance.of(
        THE_PROFILE,
        manifest.the_language_published(),
        standing if standing is not None else provenance.NO_SOLVER_IN_THIS_ANSWER,
    ).published()


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


def _too_large_to_write(
    operation: str,
    source: SubmittedText,
    refusal: TooLargeToWrite,
    place: tuple[int, int],
) -> dict:
    """The one answer an operation gives when the integer it computed
    has more digits than this tool writes.

    It stands at the function that computed the number, carries the
    limit beside the digits reached, and carries no result: the one
    thing this answer could not do is write the value.
    """
    return {
        "operation": operation,
        "status": RESOURCE_EXHAUSTED,
        "diagnostics": [
            _diagnostic_dict(
                checker.Diagnostic(
                    checker.WRITTEN_DIGITS_EXCEEDED,
                    refusal.message,
                    place,
                    about=checker.AboutTwoCounts(
                        WRITTEN_DIGITS.name, refusal.limit, refusal.reached
                    ),
                ),
                SourceRevision.of(source),
            )
        ],
    }


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


@dataclass(frozen=True)
class Checked:
    """A program the checker accepted, beside what the checker said
    about it.

    What it said is nothing -- a program it said anything about is
    refused and never reaches here -- and that empty answer is carried
    rather than thrown away because an operation that has to show the
    static checks passed must rest on the checker's own answer and not
    on a claim of its own.
    """

    program: syntax.Program
    diagnostics: tuple


def _checked_program(source: SubmittedText, run: Run):
    """The program `source` declares, checked against every rule of
    core-0 and carrying the checker's answer -- or the `Refusal` to
    answer with instead.

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
    return Checked(program, tuple(diagnostics))


def _run_check(source: SubmittedText, run: Run) -> dict:
    checked = _checked_program(source, run)
    if isinstance(checked, Refusal):
        return checked.response_for("check")
    program = checked.program

    return {
        "operation": "check",
        "status": "completed",
        "claim": {"kind": "static_check", "scope": "this input"},
        "source_digest": _source_digest(source),
        "stands_on": _stands_on(),
        "diagnostics": [],
        "contract_report": checker.ContractReport.of(program).as_dict(),
    }


def _run_verify(
    source: SubmittedText, descriptor: "machine.Descriptor | None", run: Run
) -> dict:
    """The obligations the program owes, each beside what became of it.

    Reads nothing but `source`, writes nothing and keeps nothing: asking
    twice changes neither the answer nor anything else. Every obligation
    is put to the solver or settled by a rule of core-0, and one that
    could not be is unsettled with its reason -- none is skipped.

    The answer discloses the word it takes from the solver, because a
    reader told an obligation is proved and not told what that rests on
    would take a trusted result for one this tool established itself
    (SPEC.md lines 302-305).

    Beside the inventory it says where the program as a whole stands.
    That word rests on three things and is computed from them in one
    place: what became of every obligation, what the examples the
    program declares did when they were run here, and the checker's own
    answer about the program. The examples are run rather than read off
    the obligations that are about them: no kind of evidence silently
    upgrades another, and a solver's word about an example is not the
    example having been run.

    A request that sends a descriptor is answered about one more thing:
    the three obligations of that machine stand in the same inventory,
    settled by the same loop and counted by the same word. A descriptor
    whose roles do not resolve refuses the whole answer, because the
    three are stated over the functions its roles resolve to, and an
    inventory beside that refusal would read as a machine this tool
    reasoned about. A request that sends none is answered exactly as it
    was before those obligations existed: nothing below reads a
    descriptor that is not there.
    """
    checked = _checked_program(source, run)
    if isinstance(checked, Refusal):
        return checked.response_for("verify")
    read = None
    if descriptor is not None:
        run.stop_if_exhausted()
        resolved = descriptor.resolved_against(checked.program)
        if isinstance(resolved, machine.UnresolvedRoles):
            return Refusal(
                "invalid_input", resolved.refusals, SourceRevision.of(source)
            ).response_for("verify")
        read = resolved
    shown = _what_was_shown(checked, run, read)

    answer = {
        "operation": "verify",
        "status": "completed",
        "claim": {"kind": "obligation_inventory", "scope": "this input"},
        "source_digest": _source_digest(source),
        "stands_on": _stands_on(shown.standing),
        "diagnostics": [],
        "result": shown.inventory,
    }
    if shown.disclosure is not None:
        answer["trust"] = shown.disclosure
    answer["aggregate"] = shown.over.published()
    return answer


@dataclass(frozen=True)
class WhatWasShown:
    """Everything one verification of a program found: the inventory of
    its obligations, what stood behind the attempt, and the word over
    the whole of it.

    One owner, asked by the operation that reports it and by the
    operation that publishes an artefact only when the word is
    `verified`. Two paths that each ran the verification their own way
    could disagree about one program, and then the artefact and the
    answer the Owner read before it would stand on different evidence.
    """

    inventory: dict
    standing: object
    disclosure: object
    over: verdict.Verdict


def _what_was_shown(
    checked: "Checked", run: Run, of_a_machine: object = None
) -> WhatWasShown:
    """What was shown about one checked program, and about the machine a
    request named beside it when it named one.

    The machine's three obligations stand in the same inventory as the
    program's own, so one loop settles all of them, one rule reports them
    and the one word over the whole rests on all of them. A request that
    named no machine -- every build request, and a verify request that
    sent no descriptor -- is answered about the program alone, exactly as
    it was before those obligations existed.
    """
    owed = obligations.inventory_for(checked.program)
    if of_a_machine is not None:
        owed = owed.with_also(induction.the_obligations_of(of_a_machine))
    settled = discharge.Discharge(checked.program, solving.PinnedZ3(), run).settle(
        owed
    )
    ran = examples.run_declared(checked.program, run)
    reported = {"inventory": settled.inventory_of(owed)}
    if of_a_machine is not None:
        reported["machine"] = of_a_machine.published_beside_its_obligations()
    return WhatWasShown(
        reported,
        settled.standing,
        settled.disclosure(),
        verdict.Verdict.over(
            settled.findings,
            _how_the_examples_ran(ran),
            verdict.StaticChecksPassed.of(checked.diagnostics),
        ),
    )


def _the_configuration(run: Run) -> dict:
    """The configuration a verification of this tool stood inside, as an
    artefact records it: the profile it is for, the solver pinned behind
    the word `proved`, and the four budgets of this run.

    Read from the three owners that publish them, so what an artefact
    records and what the manifest states are the same numbers -- and
    read from the budgets of the run rather than from the numbers this
    tool declares, because a caller that lowered one verified the
    program inside the number it chose and the artefact must say so.
    """
    return {
        "profile": dict(THE_PROFILE),
        "solver": provenance.the_solver_it_requires(),
        "budgets": run.budgets.in_force(RESOURCE_EXHAUSTED),
    }


def _run_build(source: SubmittedText, asked: BuildAsked, run: Run) -> dict:
    """The one artefact of a program that was shown whole, written to
    the file the request names -- or the refusal, which writes nothing.

    The two things that can stand in the way are read together: the
    destination, and whether the whole of the program was shown. A
    request that is wrong in both ways is told about both at once, and
    nothing is written until both are accepted. SPEC.md line 290: a
    build fails closed while verification is incomplete.
    """
    checked = _checked_program(source, run)
    if isinstance(checked, Refusal):
        return checked.response_for("build")
    program = checked.program
    revision = SourceRevision.of(source)

    refused: list[checker.Diagnostic] = []
    entry = building.Entry.of(asked.entry.characters, program)
    if entry is None:
        refused.append(
            checker.Diagnostic(
                "unknown_function",
                f"this program declares no function named "
                f"{asked.entry.characters!r}, and the 'entry' field of the "
                "request names it as the one an artefact of it would invoke: "
                "it declares "
                f"{', '.join(repr(name) for name in sorted(program.functions))}. "
                "Nothing was written. Send an 'entry' naming one of those, "
                "which the 'check' operation also lists for the same source",
                about=checker.AboutASymbol(asked.entry.characters),
            )
        )
    destination = building.Destination.at(asked.output_file.characters)
    if isinstance(destination, building.Unwritable):
        refused.append(
            checker.Diagnostic(destination.category, destination.reason)
        )

    shown = _what_was_shown(checked, run)
    certified = building.Certified.shown(
        shown.over, program, source.characters, revision.rendered(), shown.inventory
    )
    if isinstance(certified, building.NotShownWhole):
        withheld = certified.refusal()
        refused.append(checker.Diagnostic(withheld.category, withheld.reason))

    if refused:
        return _build_refused(refused, revision, shown)

    artefact = building.Artefact.of(certified, entry, _the_configuration(run))
    if isinstance(artefact, building.Unwritable):
        return _build_refused(
            [checker.Diagnostic(artefact.category, artefact.reason)],
            revision,
            shown,
        )

    answer = {
        "operation": "build",
        "status": "completed",
        "claim": {"kind": "artefact", "scope": "this input"},
        "source_digest": revision.rendered(),
        "stands_on": _stands_on(shown.standing),
        "diagnostics": [],
        "result": {"artefact": artefact.published(destination)},
    }
    if shown.disclosure is not None:
        answer["trust"] = shown.disclosure

    # The whole answer is written out and measured against the budget of
    # this run before anything is published. An answer too large is
    # replaced whole by the refusal that says so, and an artefact
    # published beside that refusal would be a file the Owner was never
    # told about: complete, runnable, and standing at a path no answer
    # of this tool ever named.
    too_large = run.budgets.answer_exhausted_by(printable_answer(answer))
    if too_large is not None:
        return budget_response("build", too_large)

    unwritten = destination.publish(artefact.text)
    if unwritten is not None:
        return _build_refused(
            [checker.Diagnostic(unwritten.category, unwritten.reason)],
            revision,
            shown,
        )
    return answer


def _build_refused(
    refused: list, revision: SourceRevision, shown: WhatWasShown
) -> dict:
    """The one refusal a build answers with, carrying every reason it
    found and no artefact.

    The status says which kind of refusal it is: a program the whole of
    which was not shown is `not_verified`, a program this tool cannot
    write as a module the interpreter reads is `resource_exhausted`, as
    every other limit of this tool is, and anything else is a field of
    the request this tool could not use, which is `invalid_input`. A
    request that is wrong in several ways takes the first of those: the
    evidence is the thing that would still stop the build once the
    request is repaired.
    """
    categories = {diagnostic.category for diagnostic in refused}
    if checker.NOT_SHOWN_WHOLE in categories:
        status = verdict.NOT_VERIFIED
    elif checker.GENERATED_NESTING_EXCEEDED in categories:
        status = RESOURCE_EXHAUSTED
    else:
        status = "invalid_input"
    return {
        "operation": "build",
        "status": status,
        "diagnostics": [
            _diagnostic_dict(diagnostic, revision) for diagnostic in refused
        ],
    }


def _how_the_examples_ran(ran: examples.DeclaredExamples) -> verdict.ExamplesRun:
    """The run of the declared examples, as the word over the whole
    program reads it.

    A run a limit of this tool stopped is not a run in which the
    examples it never reached passed. It is handed over as the run it
    was, with the status that stopped it and the reason, so that the
    answer says the program was not shown and says why -- rather than
    refusing the whole request, which would take away the inventory the
    Owner asked for and which this answer still has.
    """
    if ran.stopped_by is None:
        return verdict.ExamplesRun.of(ran.published(), ran.declared)
    return verdict.ExamplesRun.stopped_at(
        ran.published(),
        ran.declared,
        RESOURCE_EXHAUSTED,
        ran.stopped_by.message,
    )


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
    program = checked.program

    return {
        "operation": "parse",
        "status": "completed",
        "claim": {"kind": "syntax_tree", "scope": "this input"},
        "source_digest": _source_digest(source),
        "stands_on": _stands_on(),
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
    program = checked.program

    return {
        "operation": "format",
        "status": "completed",
        "claim": {"kind": "canonical_text", "scope": "this input"},
        "source_digest": _source_digest(source),
        "stands_on": _stands_on(),
        "diagnostics": [],
        "result": {
            "text": formatter.canonical_text(
                program, read_source(source.characters).comments
            )
        },
    }


def _run_machine(
    source: SubmittedText, descriptor: machine.Descriptor, run: Run
) -> dict:
    """What the eight roles of `descriptor` resolve to in the program
    `source` declares.

    Reads the source through the rule every operation that reads one
    shares, so a source refused here is refused exactly as a check
    refuses it, and an answer that refuses carries no result at all: a
    result beside a refusal would read as a machine this tool confirmed.

    Reads nothing but the two fields of the request, writes nothing and
    keeps nothing: asking twice changes neither the answer nor anything
    else. The answer says that the roles resolve in this revision of this
    program and settles no claim about the machine over its runs.
    """
    checked = _checked_program(source, run)
    if isinstance(checked, Refusal):
        return checked.response_for("machine")
    program = checked.program

    run.stop_if_exhausted()
    resolved = descriptor.resolved_against(program)
    revision = SourceRevision.of(source)
    if isinstance(resolved, machine.UnresolvedRoles):
        return Refusal(
            "invalid_input", resolved.refusals, revision
        ).response_for("machine")

    return {
        "operation": "machine",
        "status": "completed",
        "claim": {"kind": "machine_roles_resolved", "scope": "this input"},
        "source_digest": _source_digest(source),
        "stands_on": _stands_on(),
        "diagnostics": [],
        "result": resolved.published(),
    }


@dataclass(frozen=True)
class ValueSent:
    """One text a request to drive a machine carries, read as a value of
    the type its role needs.

    One object per text, so the state and every event are read the same
    way and each of them is refused under the name a caller sent it
    under. It holds what a refusal about that text must say: the field
    to repair, which text of the request a place stands in, the type the
    value must have and the words that name it in a sentence.
    """

    field: str
    points_into: str
    text: SubmittedText
    type_name: str
    what_it_is: str

    def read(self, program: syntax.Program) -> "object | tuple":
        """The value this text writes, or the refusals it carries.

        Every refusal is answered before any transition runs: a request
        carrying one text the runtime cannot use drives nothing at all,
        so a machine is never left part way through a sequence the
        caller must now work out.
        """
        try:
            value = _parse_value_text(self.text)
        except TooDeeplyNested as too_deep:
            return (_too_deeply_nested_diagnostic(too_deep, self.points_into),)
        except (ReaderError, syntax.SyntaxError_) as error:
            return (
                checker.Diagnostic(
                    "malformed_value",
                    f"WHAT: {self.what_it_is} does not write one value this "
                    f"tool can read: {error.message}. WHY: a machine is "
                    "driven over values, and a text that writes none, or "
                    "writes more than one, holds nothing to drive it with. "
                    "HOW: write it as one value, the way a program writes "
                    f"one, as \"(Clock 12)\" or \"(Tick)\"; the "
                    f"{self.type_name!r} type of the submitted program says "
                    "which values there are, and the 'parse' operation lists "
                    "them",
                    (error.line, error.column),
                    about=checker.AboutASymbol(self.field),
                    points_into=self.points_into,
                ),
            )
        return self._checked(value, program)

    def _checked(self, value: object, program: syntax.Program) -> "object | tuple":
        try:
            evaluator.check_value_type(value, self.type_name, program, self.what_it_is)
        except evaluator.MalformedValue as error:
            return (
                checker.Diagnostic(
                    "malformed_value",
                    f"WHAT: {error.reason}. WHY: a value is driven as a value "
                    "of the type the descriptor names for its role, and a "
                    "constructor the submitted program does not declare names "
                    "no value of it. HOW: write the value out of the "
                    "constructors the program declares for "
                    f"{self.type_name!r}, which the 'check' and 'parse' "
                    "operations list for the same source",
                    self._where_the_type_is(program),
                    about=checker.AboutASymbol(self.type_name),
                    points_into="source",
                ),
            )
        except evaluator.IllTypedValue as error:
            return (
                checker.Diagnostic(
                    "ill_typed_value",
                    f"WHAT: {error.reason}. WHY: the roles of the descriptor "
                    "are written over the three types it names, so a value of "
                    "another type is one the role does not take. HOW: send a "
                    f"value of {self.type_name!r}, the type this descriptor "
                    "names for that role; the 'machine' operation reports what "
                    "each role of the descriptor resolved to",
                    self._where_the_type_is(program),
                    about=checker.AboutASymbol(self.type_name),
                ),
            )
        return value

    def _where_the_type_is(self, program: syntax.Program) -> tuple[int, int]:
        """Where the program declares the type this value must have.

        A refusal about a value the request carried stands at the
        declaration that says which values there are: the text the
        caller sent has one value in it and no line of its own to send
        them to.
        """
        declared = program.types[self.type_name]
        return (declared.line, declared.column)


def _the_values_driven(
    driving: "StepAsked",
    driver: runtime.MachineRuntime,
    program: syntax.Program,
    revision: SourceRevision,
) -> "tuple | Refusal":
    """The state and the events the request carried, read as values of
    the types the descriptor names -- or the refusal naming every text
    that could not be read.

    All of them are read before the first transition: a caller who wrote
    two of them wrongly is told about both, and a request with one text
    the runtime cannot use drives nothing.
    """
    sent = [
        ValueSent(
            manifest.STATE.name,
            manifest.STATE.name,
            driving.state,
            driver.type_of(machine.STATE),
            f"the {manifest.STATE.name!r} field of the request",
        )
    ] + [
        ValueSent(
            f"{manifest.EVENTS.name}[{place}]",
            machine.EVENT,
            text,
            driver.type_of(machine.EVENT),
            f"the event at place {place} of the request",
        )
        for place, text in enumerate(driving.events.texts)
    ]
    read = [one.read(program) for one in sent]
    refused = tuple(
        diagnostic
        for answer in read
        if isinstance(answer, tuple)
        for diagnostic in answer
    )
    if refused:
        return Refusal(_the_status_refusing(refused), refused, revision)
    return read[0], tuple(read[1:])


def _the_status_refusing(refused: tuple) -> str:
    """Which status a refusal about the texts of a request carries: a
    limit of this tool is `resource_exhausted`, as every other limit is,
    and a text this tool cannot use is a field of the request it could
    not read."""
    if any(
        diagnostic.category == checker.NESTING_LIMIT_EXCEEDED
        for diagnostic in refused
    ):
        return RESOURCE_EXHAUSTED
    return "invalid_input"


def _run_step(source: SubmittedText, driving: "StepAsked", run: Run) -> dict:
    """What driving the machine `driving` names published, event by
    event, over the state the request carried.

    Reads the source through the rule every operation that reads one
    shares, and the roles through the one resolution this tool does, so
    a descriptor refused here is refused exactly as the 'machine'
    operation refuses it.

    Reads nothing but the four fields of the request, writes nothing and
    keeps nothing: asking twice drives the same events over the same
    state and answers the same thing. The answer says what the named
    functions answered for the state and the events it was sent, and
    settles nothing about a host that would carry those events.
    """
    checked = _checked_program(source, run)
    if isinstance(checked, Refusal):
        return checked.response_for("step")
    program = checked.program
    revision = SourceRevision.of(source)

    run.stop_if_exhausted()
    resolved = driving.descriptor.resolved_against(program)
    if isinstance(resolved, machine.UnresolvedRoles):
        return Refusal(
            "invalid_input", resolved.refusals, revision
        ).response_for("step")

    driver = runtime.MachineRuntime.of(resolved, program)
    values = _the_values_driven(driving, driver, program, revision)
    if isinstance(values, Refusal):
        return values.response_for("step")
    state, events = values

    run.stop_if_exhausted()
    try:
        driven = driver.driven(state, events, run.stop_if_exhausted)
    except evaluator.EvaluationTooDeep as too_deep:
        return _too_deep_to_run("step", source, too_deep)

    if isinstance(driven, runtime.StateRefused):
        return Refusal(
            "invalid_input", (_state_outside_invariant(driven, program),), revision
        ).response_for("step")

    answer = {
        "operation": "step",
        "status": "completed",
        "claim": {"kind": "machine_run", "scope": "this input"},
        "source_digest": revision.rendered(),
        "stands_on": _stands_on(),
        "diagnostics": [],
    }
    if driven.refused is not None:
        answer["diagnostics"] = [
            _diagnostic_dict(_contract_refused(driven.refused, program), revision)
        ]
    try:
        answer["result"] = driven.published()
    except TooLargeToWrite as too_large:
        return _too_large_to_write(
            "step",
            source,
            too_large,
            _declared_place(program, resolved.named_for(machine.STEP)),
        )

    # The whole answer is written out and measured against the budget of
    # this run before it is given, as a build measures its own: a
    # sequence long enough to drive is also long enough to answer past
    # what a caller may be given, and the first part of an answer carries
    # no outcome to read.
    too_large = run.budgets.answer_exhausted_by(printable_answer(answer))
    if too_large is not None:
        return budget_response("step", too_large)
    return answer


def _state_outside_invariant(
    refused: runtime.StateRefused, program: syntax.Program
) -> checker.Diagnostic:
    """The one refusal a state the invariant role excludes carries.

    It stands at the declaration of the function the role names, which
    is the condition that excluded the state: the state itself came in a
    field of the request and has no line to open.
    """
    return checker.Diagnostic(
        checker.STATE_OUTSIDE_INVARIANT,
        f"WHAT: the {manifest.STATE.name!r} field of the request writes a "
        f"state the {refused.role!r} role of the descriptor excludes: "
        f"{refused.named!r} answered false for it, and nothing was driven. "
        "WHY: a machine is defined from the states its invariant holds at "
        "(SPEC.md lines 395-400), so a transition from any other state is "
        "one the machine does not define, and this tool will not answer for "
        f"it. HOW: send a state {refused.named!r} holds at, or name a role "
        "that holds at this one; the 'evaluate' operation runs "
        f"{refused.named!r} over a state and answers what it says",
        _declared_place(program, refused.named),
        about=checker.AboutARole(refused.role, refused.named),
    )


def _contract_refused(
    refused: runtime.ContractRefused, program: syntax.Program
) -> checker.Diagnostic:
    """The refusal a run carries when one role's own contract was broken
    while the run was asking it.

    Answered as the 'evaluate' operation answers the same two refusals,
    in the same categories and standing at the same place: the run did
    happen, and what it met is the program's own contract refusing.
    """
    return checker.Diagnostic(
        refused.category,
        f"WHAT: driving the event at position {refused.position} reached "
        f"{refused.function_name!r}, whose {refused.category.split('_')[0]} "
        "the values it was called with do not satisfy. WHY: every call this "
        "tool makes has the contracts of the function it calls checked, and a "
        "run that went past a refused contract would publish a state the "
        "program itself does not stand behind. HOW: read "
        f"{refused.function_name!r} against the state and the event at that "
        "position; the 'verify' operation lists the obligations the program "
        "owes, and the 'evaluate' operation runs the function over those "
        "values on its own",
        _declared_place(program, refused.function_name),
        about=checker.AboutASymbol(refused.function_name),
    )


def _run_examples(source: SubmittedText, run: Run) -> dict:
    checked = _checked_program(source, run)
    if isinstance(checked, Refusal):
        return checked.response_for("examples")
    program = checked.program

    ran = examples.run_declared(program, run)
    stopped = _if_the_run_was_stopped("examples", source, program, ran)
    if stopped is not None:
        return stopped

    return {
        "operation": "examples",
        "status": "completed",
        "claim": {"kind": "examples", "scope": "declared examples"},
        "source_digest": _source_digest(source),
        "stands_on": _stands_on(),
        "diagnostics": [],
        "result": {"examples": ran.published()},
    }


def _if_the_run_was_stopped(
    operation: str,
    source: SubmittedText,
    program: syntax.Program,
    ran: examples.DeclaredExamples,
) -> dict | None:
    """The refusal to answer `operation` with, when running the declared
    examples met a limit of this tool, or nothing at all.

    The two limits are the two this tool declares about running a
    program: how deep a run may nest, and how many digits an answer
    writes. Each is answered exactly as it was before the run had an
    owner of its own, so an operation that refuses for one of them
    refuses with the same words and in the same place.
    """
    if ran.stopped_by is None:
        return None
    if isinstance(ran.stopped_by, evaluator.EvaluationTooDeep):
        return _too_deep_to_run(operation, source, ran.stopped_by)
    return _too_large_to_write(
        operation,
        source,
        ran.stopped_by,
        _declared_place(program, ran.stopped_at),
    )


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
    program = checked.program
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

    try:
        written = render(result)
    except TooLargeToWrite as too_large:
        return _too_large_to_write("evaluate", source, too_large, place)

    return {
        "operation": "evaluate",
        "status": "completed",
        "claim": {"kind": "evaluation", "scope": "this input"},
        "source_digest": _source_digest(source),
        "diagnostics": [],
        "result": {"value": written},
    }
