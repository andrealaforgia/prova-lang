"""Operation dispatch, manifest, response construction and diagnostics.

The only place that knows operation names.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from prova import checker, evaluator, obligations, syntax
from prova.reader import ReaderError, end_of, read_program
from prova.values import render

AVAILABLE_OPERATIONS = ("check", "examples", "evaluate", "discover", "verify")

# The operations that read a program from the `source` field of the
# request. Each of them is answered about a text, so each of them refuses
# a request whose `source` is not one.
SOURCE_READING_OPERATIONS = ("check", "examples", "evaluate", "verify")
UNAVAILABLE_OPERATIONS = frozenset({"parse", "format", "build"})

# What the tool answers when the source is not a program it can check.
# `invalid_program` means the source is a core-0 program that breaks a
# rule of core-0; `unsupported` means it is not a program of this profile
# at all (SPEC.md lines 51-54, 191-196).
UNSUPPORTED_STATUS = "unsupported"
UNSUPPORTED_CONSTRUCT = "unsupported_construct"

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
def handle(request: dict) -> dict:
    operation = request.get("operation")
    if operation in SOURCE_READING_OPERATIONS:
        source = request.get("source", "")
        if not isinstance(source, str):
            return _unreadable_source(operation, source)
    if operation == "check":
        return _run_check(request.get("source", ""))
    if operation == "examples":
        return _run_examples(request.get("source", ""))
    if operation == "evaluate":
        return _run_evaluate(
            request.get("source", ""),
            request.get("function"),
            request.get("arguments", []),
        )
    if operation == "verify":
        return _run_verify(request.get("source", ""))
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
        "operation": operation,
        "status": "unavailable",
        "diagnostics": [
            {
                "category": "unknown_operation",
                "reason": f"operation {operation!r} is not recognized",
            }
        ],
    }


def _unreadable_source(operation: str, source: object) -> dict:
    """The answer to a request whose `source` is not the text of a
    program.

    Read before anything else about the request, because every later
    answer is about a text: the revision an answer carries is the
    revision of those characters, and a value of another kind has none.
    """
    return {
        "operation": operation,
        "status": "invalid_input",
        "diagnostics": [
            _diagnostic_dict(
                checker.Diagnostic(
                    "malformed_request",
                    f"the 'source' field of the request holds "
                    f"{type(source).__name__}, not the text of a program: this "
                    "tool reads a program from the characters of that field, "
                    "and a value of another kind holds no characters to read; "
                    "send the program as one JSON string, writing a line break "
                    "as \\n",
                    about=checker.AboutASymbol("source"),
                )
            )
        ],
    }


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
                    "Every status an answered request carries. A request this "
                    "service cannot read as a request at all is not answered "
                    "here: the command answers it with the status "
                    "'tool_failure' and exits 1, and 'tool_failure' is "
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
                "verify": (
                    "A completed verify response is an inventory only: it lists the "
                    "obligations the program owes and attempts none of them, so every "
                    "entry's result is not_attempted. This tool has no solver."
                ),
            },
            "resource_limits": {
                "enforced": False,
                "reason": "no resource limits are enforced in I1",
            },
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
    """

    digest: str

    @classmethod
    def of(cls, source: str) -> "SourceRevision":
        return cls(hashlib.sha256(source.encode("utf-8")).hexdigest())

    def rendered(self) -> str:
        return self.digest


def _source_digest(source: str) -> str:
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


def _checked_program(source: str):
    """The program `source` declares, checked against every rule of
    core-0 -- or the `Refusal` to answer with instead.

    Every operation that reads source asks here, so a source refused for
    one of them is refused the same way for all of them, and a caller
    moving between operations never meets two answers for one source.
    """
    revision = SourceRevision.of(source)
    try:
        program = syntax.parse_program(read_program(source))
    except syntax.UnsupportedConstruct as outside:
        return Refusal(
            UNSUPPORTED_STATUS, (_out_of_profile_diagnostic(outside),), revision
        )
    except (ReaderError, syntax.SyntaxError_) as error:
        return Refusal("invalid_program", (_syntax_diagnostic(error),), revision)

    diagnostics = checker.check_program(program)
    if diagnostics:
        return Refusal("invalid_program", tuple(diagnostics), revision)
    return program


def _run_check(source: str) -> dict:
    checked = _checked_program(source)
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


def _run_verify(source: str) -> dict:
    """The obligations the program owes, every one of them not attempted.

    Reads nothing but `source`, writes nothing and keeps nothing: asking
    twice changes neither the answer nor anything else.
    """
    checked = _checked_program(source)
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


def _run_examples(source: str) -> dict:
    checked = _checked_program(source)
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
            try:
                actual = evaluator.call_function(function, example.args, program)
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


def _parse_value_text(text: str) -> object:
    """The one value `text` writes, or the reader's refusal to read one.

    A refusal stands where the reader stopped in that text: at the value
    after the first when there are several, and at the end of the text
    when there is none.
    """
    forms = read_program(text)
    if len(forms) != 1:
        extra = forms[1] if len(forms) > 1 else None
        line, column = (
            (extra.line, extra.column) if extra is not None else end_of(text)
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


def _run_evaluate(source: str, function_name: object, argument_texts: list) -> dict:
    checked = _checked_program(source)
    if isinstance(checked, Refusal):
        return checked.response_for("evaluate")
    program = checked
    revision = SourceRevision.of(source)

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
                        about=checker.AboutASymbol(str(function_name)),
                    ),
                    revision,
                )
            ],
        }

    place = _declared_place(program, function.name)
    try:
        args = tuple(_parse_value_text(text) for text in argument_texts)
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
        for arg, (param_name, param_type) in zip(args, params):
            evaluator.check_value_type(arg, param_type, program, f"argument {param_name!r}")
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

    try:
        result = evaluator.call_function(function, args, program)
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
