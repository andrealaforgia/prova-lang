"""I1.S4.P5 (documented response semantics): a correct value alone does not
establish that a successful `evaluate` response represents postcondition-
checked evaluation, so the operation's own documentation, read from the
public `discover` response, must say so: a `completed` evaluate response
means the function's postconditions were checked and held for the supplied
input, and that this is evidence about that input only.

The statement is located wherever the manifest puts it (any string under the
manifest that names `evaluate`), because the schema is not fixed by the plan.
`states_checked_success` is itself exercised against texts that lack, negate
or overstate the statement, so the check is capable of failing.
"""

from __future__ import annotations

import re

from _prova_client import run_prova


def _strings(node, path=""):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from _strings(value, f"{path}/{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _strings(value, f"{path}[{i}]")


def states_checked_success(text: str) -> bool:
    """True when `text` says a successful evaluation passed its postconditions
    for the supplied input, without negating or overstating that."""
    t = text.lower()
    if not re.search(r"postcondition|ensures", t):
        return False
    if not re.search(r"success|completed|returned result|result is returned", t):
        return False
    if not re.search(r"supplied|given|this input|these arguments|provided", t):
        return False
    if re.search(r"(not|never|without|no)\s+(been\s+)?(checked|check|verif|evaluat)", t):
        return False
    if re.search(r"\b(proved|proven|verified for all|for all inputs|universal)\b", t) and not re.search(
            r"\b(not|no|never|without)\b[^.]*\b(proof|proved|proven|universal|all inputs)\b", t):
        return False
    return True


def test_documentation_check_accepts_the_required_statement():
    assert states_checked_success(
        "A completed evaluate response means the function's postconditions were checked and held "
        "for the supplied input; it is not a proof for all inputs.")


def test_documentation_check_rejects_texts_that_lack_or_overstate_the_statement():
    for text in (
        "evaluate runs one named function on argument values and returns one result.",
        "A completed evaluate returns the computed value for the given arguments.",
        "Postconditions are not checked by evaluate; a completed response returns the given result.",
        "A completed evaluate proves the postconditions for all inputs.",
        "",
    ):
        assert not states_checked_success(text), text


def test_discover_documents_that_successful_evaluate_passed_postconditions_for_the_supplied_input():
    returncode, response, stdout, stderr = run_prova({"prova": "i1", "operation": "discover"})
    assert returncode == 0 and response is not None, (stdout, stderr)
    assert response["status"] == "completed"
    result = response.get("result")
    texts = [(p, s) for p, s in _strings(result) if re.search(r"evaluate", p + " " + s, re.I) and " " in s.strip()]
    assert texts, "the manifest carries no descriptive text about evaluate"
    assert any(states_checked_success(s) for _, s in texts), texts

