"""Shared helpers for I1.S6 property tests: large-integer arithmetic on the
separate add-one program, and the reservation source/contract's continued
preservation once large-integer support lands.

Not a test module (no `test_` prefix); pytest will not collect it.
"""

from __future__ import annotations

import pathlib
import subprocess

from _prova_client import (  # noqa: F401  (re-exported for the test modules)
    REPO_ROOT,
    SPEC_ORACLE_SHA,
    load_reservation_source,
    parse_value,
    protected_region,
    run_prova,
)

ADD_ONE_PATH = REPO_ROOT / "conformance" / "add-one.prova"


def load_add_one_source() -> str:
    return ADD_ONE_PATH.read_text(encoding="utf-8")


def evaluate_add_one(n: int, source: str | None = None) -> tuple[int, dict | None, str, str]:
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": source if source is not None else load_add_one_source(),
        "function": "add-one",
        "arguments": [str(n)],
    }
    return run_prova(request)


def independent_add_one(n: int) -> int:
    # Exact-integer oracle: Python's int is arbitrary precision, and this
    # module never imports anything from src/prova.
    return n + 1


def _walk_leaves(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from _walk_leaves(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_leaves(value)
    else:
        yield node


def assert_no_float_leaves(response: dict) -> None:
    for leaf in _walk_leaves(response):
        assert not isinstance(leaf, float), (
            "response carries a JSON float leaf, which cannot losslessly "
            f"represent an arbitrary-precision integer: {response}"
        )


def assert_add_one_result(returncode, response, stdout, stderr, *, n: int) -> None:
    assert returncode == 0, f"tool failure evaluating add-one({n}): stderr={stderr!r}"
    assert response is not None, f"non-JSON response for add-one({n}): {stdout!r}"
    assert response.get("status") == "completed", (
        f"expected successful evaluation of add-one({n}), got: {response}"
    )
    result = response.get("result") or {}
    value_text = result.get("value")
    assert value_text is not None, f"no successful result value for add-one({n}): {response}"
    expected = independent_add_one(n)
    assert parse_value(value_text) == expected, (
        f"add-one({n}): expected {expected}, got value text {value_text!r} in {response}"
    )
    assert_no_float_leaves(response)


# Fault models a corrupted implementation could exhibit. Used only to check
# (analytically, without a live tool) that comparing against
# `independent_add_one` would actually catch each one -- not run against
# the real tool.
def fault_echo(n: int) -> int:
    return n


def fault_constant_result(n: int) -> int:
    return 42


def fault_binary64_rounding(n: int) -> int:
    return int(float(n + 1))


def fault_signed_64_wrap(n: int) -> int:
    wrapped = (n + 1 + 2**63) % 2**64 - 2**63
    return wrapped


FAULT_MODELS = {
    "echo": fault_echo,
    "constant-result": fault_constant_result,
    "binary64-rounding": fault_binary64_rounding,
    "signed-64-wrap": fault_signed_64_wrap,
}


def spec_text_at(sha: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{sha}:SPEC.md"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def working_tree_spec_text() -> str:
    return (pathlib.Path(REPO_ROOT) / "SPEC.md").read_text(encoding="utf-8")


def normalize_formatting(text: str) -> str:
    return " ".join(text.split())
