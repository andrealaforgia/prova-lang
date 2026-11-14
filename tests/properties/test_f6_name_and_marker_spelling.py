"""Property tests for feature F6's design laws, over domains no table of
examples can carry.

LAW1 -- a declared function name is accepted exactly when it matches the
value-name shape `[a-z][a-z0-9-]*[?!]?` and is not a word the language
reserves.

LAW2 -- a signature is accepted exactly when its arrow is `->` and its
effect marker and effect are `! pure`.

LAW3 -- a declared example is accepted exactly when its arrow is `=>`.

The expected verdict is computed here from the shape SPEC.md states
(lines 65-74, 92, 99-106) and from the reserved-word list written out by
hand, never from the tool's own answer, and the generated spelling is
substituted into one otherwise well spelled program so that nothing else
can decide the verdict.

Derandomized with a bounded example count so the verdict does not depend
on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

import re

from hypothesis import given, settings
from hypothesis import strategies as st

from prova import service

SYNTAX_CATEGORY = "syntax"

# The shape SPEC.md gives a value or function name, and the words it
# reserves. Written from the specification, not read from the tool.
VALUE_NAME_SHAPE = re.compile(r"[a-z][a-z0-9-]*[?!]?$")
RESERVED_WORDS = frozenset(
    {
        "deftype", "record", "union", "defn", "sig", "pure", "requires",
        "ensures", "examples", "example", "let", "if", "match", "true",
        "false", "result",
        "+", "-", "*", "<", "<=", ">", ">=", "=", "and", "or", "not",
    }
)

NAME_CHARACTERS = "abz-?!01AZ"
MARKER_CHARACTERS = "-=>!?*"


def _program(name: str = "add-one", arrow: str = "->", effect_marker: str = "!",
             effect: str = "pure", example_arrow: str = "=>") -> str:
    return (
        f"(defn {name}\n"
        f"  (sig ((n Int)) {arrow} Int {effect_marker} {effect})\n"
        f"  (examples (example ({name} 41) {example_arrow} 42))\n"
        "  (+ n 1))\n"
    )


def _check(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "check", "source": source})


def _accepted(response: dict) -> bool:
    return response.get("status") == "completed" and not response.get("diagnostics")


def _refused_for_spelling(response: dict) -> bool:
    return response.get("status") == "invalid_program" and any(
        diagnostic.get("category") == SYNTAX_CATEGORY
        for diagnostic in response.get("diagnostics") or []
    )


def _assert_verdict(response: dict, *, should_be_accepted: bool, what: str) -> None:
    if should_be_accepted:
        assert _accepted(response), (
            f"{what} is spelled as the language defines it but was not accepted: "
            f"{response}. Only a spelling the language does not define may be "
            "refused; accept every other program."
        )
        return
    assert _refused_for_spelling(response), (
        f"{what} is not spelled as the language defines it but was not refused as "
        f"an invalid program with a {SYNTAX_CATEGORY!r} diagnostic: {response}. A "
        "program the language does not define must be invalid, and say so in that "
        "category."
    )


@settings(max_examples=60, derandomize=True, deadline=None)
@given(st.text(alphabet=NAME_CHARACTERS, min_size=1, max_size=4))
def test_a_function_name_is_accepted_exactly_when_it_has_the_defined_shape(name):
    """LAW1: a declared function name is accepted exactly when it matches
    the value-name shape and is not reserved."""
    well_spelled = bool(VALUE_NAME_SHAPE.match(name)) and name not in RESERVED_WORDS

    _assert_verdict(
        _check(_program(name=name)),
        should_be_accepted=well_spelled,
        what=f"the function name {name!r}",
    )


@settings(max_examples=40, derandomize=True, deadline=None)
@given(
    st.text(alphabet=MARKER_CHARACTERS, min_size=1, max_size=2),
    st.text(alphabet=MARKER_CHARACTERS, min_size=1, max_size=2),
    st.sampled_from(["pure", "impure", "io", "Pure"]),
)
def test_a_signature_is_accepted_exactly_when_its_markers_are_the_defined_ones(
    arrow, effect_marker, effect
):
    """LAW2: a signature is accepted exactly when it is written
    `-> type ! pure`."""
    well_spelled = (arrow, effect_marker, effect) == ("->", "!", "pure")

    _assert_verdict(
        _check(_program(arrow=arrow, effect_marker=effect_marker, effect=effect)),
        should_be_accepted=well_spelled,
        what=f"the signature markers {arrow!r} and {effect_marker!r} {effect!r}",
    )


@settings(max_examples=30, derandomize=True, deadline=None)
@given(st.text(alphabet=MARKER_CHARACTERS, min_size=1, max_size=2))
def test_an_example_is_accepted_exactly_when_its_arrow_is_the_defined_one(arrow):
    """LAW3: a declared example is accepted exactly when its arrow is
    `=>`."""
    _assert_verdict(
        _check(_program(example_arrow=arrow)),
        should_be_accepted=(arrow == "=>"),
        what=f"the example arrow {arrow!r}",
    )
