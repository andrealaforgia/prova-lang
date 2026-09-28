"""Operation dispatch, manifest, response construction and diagnostics.

The only place that knows operation names.
"""

from __future__ import annotations

import hashlib

from prova import checker, evaluator, syntax
from prova.reader import ReaderError, read_program
from prova.values import render


def handle(request: dict) -> dict:
    operation = request.get("operation")
    if operation == "examples":
        return _run_examples(request.get("source", ""))
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


def _source_digest(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


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
                {"category": d.category, "reason": d.reason} for d in diagnostics
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
