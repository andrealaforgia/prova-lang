"""I1.S4.P5 (documented response semantics): a correct value alone does not
establish that a successful `evaluate` response represents postcondition-
checked evaluation, so the operation's own documentation, read from the
public `discover` response, must say so: a `completed` evaluate response
means the function's postconditions were checked and held for the supplied
input, and that this is evidence about that input only.

`states_checked_success` is the wording contract for that statement: one
sentence must tie a completed response to the postconditions having been
checked and held for the supplied input. It is exercised against texts that
lack, negate, overstate or scatter the statement, so it is capable of failing.

The check that reads the statement out of the live `discover` response is not
part of this file until the manifest documentation lands with its
implementation.
"""

from __future__ import annotations

import re


def _sentence_states_checked_success(t: str) -> bool:
    if not re.search(r"postcondition|ensures", t):
        return False
    if not re.search(r"success|completed|returned result|result is returned", t):
        return False
    if not re.search(r"supplied|given|this input|these arguments|provided", t):
        return False
    if not re.search(r"\b(checked|held|holds|passed|satisfied)\b", t):
        return False
    return not re.search(r"(not|never|without|no)\s+(been\s+)?(checked|check|verif|evaluat)", t)


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
        "",
    ):
        assert not states_checked_success(text), text
