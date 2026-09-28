"""I1.S4.P5 (documented response semantics): a correct value alone does not
establish that a successful `evaluate` response represents postcondition-
checked evaluation, so the operation's own documentation, read from the
public `discover` response, must say so: a `completed` evaluate response
means the function's postconditions were checked and held for the supplied
input, and that this is evidence about that input only.

`states_checked_success` is the wording contract for that statement: one
sentence must tie a completed response to the postconditions having been
checked and held for the supplied input, without hedge or disclaimer. It is
exercised against texts that lack, negate, hedge, overstate or scatter the
statement, so it is capable of failing. The live test then applies it to the
descriptive text about `evaluate` in the real `discover` response.
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


_HEDGES = (r"\b(ignored|ignore|skipped|skip|disregarded|unchecked|may|might|can be|could|unless|only|elsewhere|"
           r"other operation|separate operation|not|never|without|no)\b")


def _sentence_states_checked_success(t: str) -> bool:
    """One sentence binds a completed response to postconditions that were
    checked and then held, for the supplied input, with no hedge or disclaimer."""
    if not re.search(r"\bcompleted\b|\bsuccessful\b", t):
        return False
    if re.search(_HEDGES, t):
        return False
    if not re.search(r"\b(supplied|given|provided)\b|this input|these arguments", t):
        return False
    return bool(re.search(r"postconditions?\b[^.;]*\bchecked\b[^.;]*\b(held|hold|holds|satisfied)\b", t))


def states_checked_success(text: str) -> bool:
    """True when a single sentence of `text` says a successful evaluation had
    its postconditions checked and held for the supplied input, and no
    sentence overstates that as a proof for all inputs."""
    t = text.lower()
    overstated = re.search(r"\b(proved|proven|verified for all|for all inputs|universal)\b", t) and not re.search(
        r"\b(not|no|never|without)\b[^.]*\b(proof|proved|proven|universal|all inputs)\b", t)
    if overstated:
        return False
    return any(_sentence_states_checked_success(sentence) for sentence in re.split(r"[.;!?]", t))


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
        "Postconditions are described elsewhere; completed responses use the given schema.",
        "A completed evaluate returns the computed value for the supplied arguments. Postconditions are ignored.",
        "A completed evaluate returns the value for the supplied arguments. Postconditions are checked only by "
        "the check operation.",
        "Postconditions may be skipped; a completed evaluate returns the supplied arguments result.",
        "A completed evaluate means postconditions may be checked and held for the supplied input.",
        "",
    ):
        assert not states_checked_success(text), text


def test_discover_documents_that_successful_evaluate_passed_postconditions_for_the_supplied_input():
    returncode, response, stdout, stderr = run_prova({"prova": "i1", "operation": "discover"})
    assert returncode == 0 and response is not None, (stdout, stderr)
    assert response["status"] == "completed"
    texts = [(p, s) for p, s in _strings(response.get("result")) if re.search(r"evaluate", p + " " + s, re.I) and " " in s.strip()]
    assert texts, "the manifest carries no descriptive text about evaluate"
    assert any(states_checked_success(s) for _, s in texts), texts
