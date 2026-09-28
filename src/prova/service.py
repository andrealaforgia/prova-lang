"""Operation dispatch, manifest, response construction and diagnostics.

The only place that knows operation names.
"""

from __future__ import annotations

import hashlib

from prova import checker, evaluator, syntax
from prova.reader import ReaderError, read_program
from prova.values import render

UNAVAILABLE_OPERATIONS = frozenset({"parse", "format", "verify", "build"})


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


def _source_digest(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _diagnostic_dict(diagnostic: checker.Diagnostic) -> dict:
    entry = {"category": diagnostic.category, "reason": diagnostic.reason}
    if diagnostic.location is not None:
        line, column = diagnostic.location
        entry["location"] = {"line": line, "column": column}
    return entry


def _run_check(source: str) -> dict:
    try:
        forms = read_program(source)
        program = syntax.parse_program(forms)
    except (ReaderError, syntax.SyntaxError_) as error:
        return {
            "operation": "check",
            "status": "invalid_program",
            "diagnostics": [{"category": "syntax", "reason": error.message}],
        }

    diagnostics = checker.check_program(program)
    if diagnostics:
        return {
            "operation": "check",
            "status": "invalid_program",
            "diagnostics": [_diagnostic_dict(d) for d in diagnostics],
        }

    return {
        "operation": "check",
        "status": "completed",
        "claim": {"kind": "static_check", "scope": "this input"},
        "source_digest": _source_digest(source),
        "diagnostics": [],
    }


def _run_examples(source: str) -> dict:
    try:
        forms = read_program(source)
        program = syntax.parse_program(forms)
    except (ReaderError, syntax.SyntaxError_) as error:
        return {
            "operation": "examples",
            "status": "invalid_program",
            "diagnostics": [{"category": "syntax", "reason": error.message}],
        }

    diagnostics = checker.check_program(program)
    if diagnostics:
        return {
            "operation": "examples",
            "status": "invalid_program",
            "diagnostics": [
                _diagnostic_dict(d) for d in diagnostics
            ],
        }

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
    try:
        forms = read_program(source)
        program = syntax.parse_program(forms)
    except (ReaderError, syntax.SyntaxError_) as error:
        return {
            "operation": "evaluate",
            "status": "invalid_program",
            "diagnostics": [{"category": "syntax", "reason": error.message}],
        }

    diagnostics = checker.check_program(program)
    if diagnostics:
        return {
            "operation": "evaluate",
            "status": "invalid_program",
            "diagnostics": [
                _diagnostic_dict(d) for d in diagnostics
            ],
        }

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
