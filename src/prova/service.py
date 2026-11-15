"""Operation dispatch, manifest, response construction and diagnostics.

The only place that knows operation names.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from prova import checker, evaluator, obligations, syntax
from prova.reader import ReaderError, read_program
from prova.values import render

AVAILABLE_OPERATIONS = ("check", "examples", "evaluate", "discover", "verify")
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

DIAGNOSTIC_CATEGORIES = (
    "syntax",
    UNSUPPORTED_CONSTRUCT,
    "unbound_type",
    "unbound_constructor",
    "unbound_name",
    "unbound_field",
    "type_mismatch",
    "arity_mismatch",
    "non_exhaustive_match",
    checker.CYCLIC_DEPENDENCY,
    checker.DUPLICATE_DECLARATION,
    checker.RECURSIVE_TYPE,
    checker.SHADOWED_BINDING,
    checker.RESERVED_NAME,
    checker.UNRELATED_EXAMPLE,
    "unknown_function",
    "malformed_value",
    "ill_typed_value",
    "precondition_violation",
    "postcondition_violation",
    "operation_unavailable",
    "unknown_operation",
)


def handle(request: dict) -> dict:
    operation = request.get("operation")
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


def _source_digest(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _diagnostic_dict(diagnostic: checker.Diagnostic) -> dict:
    entry = {"category": diagnostic.category, "reason": diagnostic.reason}
    if diagnostic.location is not None:
        line, column = diagnostic.location
        entry["location"] = {"line": line, "column": column}
    if diagnostic.cycle is not None:
        entry["cycle"] = list(diagnostic.cycle.names())
    return entry


def _syntax_diagnostic(error: ReaderError | syntax.SyntaxError_) -> dict:
    """The one diagnostic a source the tool cannot read as a core-0
    program carries.

    Every operation that reads source answers through this builder, so a
    source refused by the reader comes back the same way whichever
    operation met it, carrying the place the refusal stands at so a
    reader is sent to the line to repair.
    """
    entry = {"category": "syntax", "reason": error.message}
    if error.line:
        entry["location"] = {"line": error.line, "column": error.column}
    return entry


def _out_of_profile_diagnostic(refusal: syntax.UnsupportedConstruct) -> dict:
    """The one diagnostic a source using a construct core-0 does not have
    carries: the construct named, why core-0 cannot give it a meaning,
    how to write the intent instead, and the place it stands at.

    `construct` is the stable word the profile gives that kind of
    construct, carried beside the sentence so a caller can tell the
    kinds apart without reading the prose.
    """
    return {
        "category": UNSUPPORTED_CONSTRUCT,
        "reason": refusal.message,
        "construct": refusal.construct.name,
        "location": {"line": refusal.line, "column": refusal.column},
    }


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

    def response_for(self, operation: str) -> dict:
        return {
            "operation": operation,
            "status": self.status,
            "diagnostics": [dict(diagnostic) for diagnostic in self.diagnostics],
        }


def _checked_program(source: str):
    """The program `source` declares, checked against every rule of
    core-0 -- or the `Refusal` to answer with instead.

    Every operation that reads source asks here, so a source refused for
    one of them is refused the same way for all of them, and a caller
    moving between operations never meets two answers for one source.
    """
    try:
        program = syntax.parse_program(read_program(source))
    except syntax.UnsupportedConstruct as outside:
        return Refusal(UNSUPPORTED_STATUS, (_out_of_profile_diagnostic(outside),))
    except (ReaderError, syntax.SyntaxError_) as error:
        return Refusal("invalid_program", (_syntax_diagnostic(error),))

    diagnostics = checker.check_program(program)
    if diagnostics:
        return Refusal(
            "invalid_program",
            tuple(_diagnostic_dict(diagnostic) for diagnostic in diagnostics),
        )
    return program


def _run_check(source: str) -> dict:
    checked = _checked_program(source)
    if isinstance(checked, Refusal):
        return checked.response_for("check")

    return {
        "operation": "check",
        "status": "completed",
        "claim": {"kind": "static_check", "scope": "this input"},
        "source_digest": _source_digest(source),
        "diagnostics": [],
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
    forms = read_program(text)
    if len(forms) != 1:
        raise ReaderError(f"expected exactly one value, got {len(forms)}", 0, 0)
    return syntax.parse_value(forms[0])


def _run_evaluate(source: str, function_name: object, argument_texts: list) -> dict:
    checked = _checked_program(source)
    if isinstance(checked, Refusal):
        return checked.response_for("evaluate")
    program = checked

    function = program.functions.get(function_name)
    if function is None:
        return {
            "operation": "evaluate",
            "status": "invalid_input",
            "diagnostics": [
                {
                    "category": "unknown_function",
                    "reason": f"no function named {function_name!r}",
                }
            ],
        }

    try:
        args = tuple(_parse_value_text(text) for text in argument_texts)
    except (ReaderError, syntax.SyntaxError_) as error:
        return {
            "operation": "evaluate",
            "status": "invalid_input",
            "diagnostics": [{"category": "malformed_value", "reason": error.message}],
        }

    params = function.signature.params
    if len(args) != len(params):
        return {
            "operation": "evaluate",
            "status": "invalid_input",
            "diagnostics": [
                {
                    "category": "arity_mismatch",
                    "reason": (
                        f"function {function_name!r} expects {len(params)} argument(s), "
                        f"got {len(args)}"
                    ),
                }
            ],
        }

    try:
        for arg, (param_name, param_type) in zip(args, params):
            evaluator.check_value_type(arg, param_type, program, f"argument {param_name!r}")
    except evaluator.MalformedValue as error:
        return {
            "operation": "evaluate",
            "status": "invalid_input",
            "diagnostics": [{"category": "malformed_value", "reason": error.reason}],
        }
    except evaluator.IllTypedValue as error:
        return {
            "operation": "evaluate",
            "status": "invalid_input",
            "diagnostics": [{"category": "ill_typed_value", "reason": error.reason}],
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
                {"category": "precondition_violation", "reason": str(violation)}
            ],
        }
    except evaluator.PostconditionViolation as violation:
        return {
            "operation": "evaluate",
            "status": "completed",
            "claim": {"kind": "evaluation", "scope": "this input"},
            "source_digest": _source_digest(source),
            "diagnostics": [
                {"category": "postcondition_violation", "reason": str(violation)}
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
