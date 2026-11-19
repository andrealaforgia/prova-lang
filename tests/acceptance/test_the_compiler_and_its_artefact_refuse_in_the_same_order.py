"""The compiler and the artefact it builds read every argument before
they type any of them, so the two refuse one pair of arguments the same
way.

The rule is already written down for text that carries no value at all
(F23.B8). A constructor the program does not declare, or one given the
wrong number of fields, is the same kind of fact -- the value cannot be
read out of this program's own declarations -- and the artefact
refused it as malformed wherever it stood, while the compiler typed the
arguments one by one and reported the first wrong type it met, ahead of
an argument it could not read at all. `["true", "(Unknown)"]` was
`ill_typed_value` from the compiler and MALFORMED from the artefact.

The twenty pairs below are driven through both: the real command, and
the built artefact run by a plain interpreter. The point is not which
word each pair gets but that the two agree on all of them, so pairs
that must be answered, pairs that are ill typed and pairs that are
malformed all stand in the table.
"""

from __future__ import annotations

import pathlib

import pytest

from _f22_fixtures import ANSWERED, ILL_TYPED, MALFORMED, evaluate, run_artefact
from _f23_fixtures import an_artefact_of, first_line_word

A = "=>"

ADDITION = f"""(deftype Pair (record (x Int) (y Int)))

(defn add
  (sig ((a Int) (b Int)) -> Int ! pure)
  (examples (example (add 1 2) {A} 3))
  (+ a b))
"""

# What one run was answered with, in words both sides are read into: the
# artefact's exit status and the compiler's refusal category say the
# same three things.
AN_ANSWER = "an answer"
ILL_TYPED_VALUE = "ill typed"
MALFORMED_VALUE = "malformed"

# Five texts the entry's two Int parameters can be given, each a kind of
# its own, and the twenty ordered pairs of them that are not two plain
# numbers.
A_NUMBER = "1"
OF_ANOTHER_TYPE = "true"
A_RECORD_OF_ANOTHER_TYPE = "(Pair 1 2)"
AN_UNDECLARED_CONSTRUCTOR = "(Unknown)"
A_DECLARED_ONE_SHORT_OF_ITS_FIELDS = "(Pair 1)"

THE_TEXTS = (
    A_NUMBER,
    OF_ANOTHER_TYPE,
    A_RECORD_OF_ANOTHER_TYPE,
    AN_UNDECLARED_CONSTRUCTOR,
    A_DECLARED_ONE_SHORT_OF_ITS_FIELDS,
)

THE_PAIRS = tuple(
    (first, second)
    for first in THE_TEXTS
    for second in THE_TEXTS
    if (first, second) != (A_NUMBER, A_NUMBER)
)


@pytest.fixture(scope="module")
def the_built_addition(tmp_path_factory) -> pathlib.Path:
    return an_artefact_of(ADDITION, "add", tmp_path_factory.mktemp("addition"))


def _what_the_compiler_said(arguments: list) -> str:
    answer = evaluate(ADDITION, "add", list(arguments))
    if answer["status"] == "completed" and not answer.get("diagnostics"):
        return AN_ANSWER
    categories = [d["category"] for d in answer.get("diagnostics") or []]
    assert len(categories) == 1, (arguments, answer)
    if categories[0] == "ill_typed_value":
        return ILL_TYPED_VALUE
    if categories[0] == "malformed_value":
        return MALFORMED_VALUE
    raise AssertionError((arguments, answer))


def _what_the_artefact_said(artefact: pathlib.Path, arguments: list) -> str:
    ran = run_artefact(artefact, list(arguments))
    assert "Traceback" not in ran.stderr, ran.stderr[-400:]
    if ran.returncode == ANSWERED:
        return AN_ANSWER
    if ran.returncode == ILL_TYPED:
        assert first_line_word(ran) == "ILL-TYPED", ran.stderr[:200]
        return ILL_TYPED_VALUE
    if ran.returncode == MALFORMED:
        assert first_line_word(ran) == "MALFORMED", ran.stderr[:200]
        return MALFORMED_VALUE
    raise AssertionError((arguments, ran.returncode, ran.stderr[-300:]))


def test_the_two_agree_on_every_one_of_the_twenty_pairs(the_built_addition):
    disagreed = []
    for arguments in THE_PAIRS:
        compiler = _what_the_compiler_said(list(arguments))
        artefact = _what_the_artefact_said(the_built_addition, list(arguments))
        if compiler != artefact:
            disagreed.append((arguments, compiler, artefact))

    assert disagreed == [], (
        "the compiler and the artefact it built answered the same arguments "
        f"differently: {disagreed}. Both read every argument out of the "
        "program's own declarations before either types one, so a value "
        "naming a constructor the program does not declare is refused "
        "wherever it stands, ahead of a readable value of the wrong type."
    )


def test_a_value_the_program_cannot_name_beats_one_of_the_wrong_type(
    the_built_addition,
):
    """The ordering itself, in the one pair the review reported: the
    second argument names no constructor of this program, the first is
    of the wrong type, and both sides refuse the pair as malformed."""
    arguments = [OF_ANOTHER_TYPE, AN_UNDECLARED_CONSTRUCTOR]

    assert _what_the_compiler_said(arguments) == MALFORMED_VALUE
    assert _what_the_artefact_said(the_built_addition, arguments) == MALFORMED_VALUE


def test_the_same_holds_when_the_unreadable_one_stands_first(the_built_addition):
    arguments = [AN_UNDECLARED_CONSTRUCTOR, OF_ANOTHER_TYPE]

    assert _what_the_compiler_said(arguments) == MALFORMED_VALUE
    assert _what_the_artefact_said(the_built_addition, arguments) == MALFORMED_VALUE


def test_two_readable_values_of_the_wrong_type_are_still_ill_typed(
    the_built_addition,
):
    """The rule is about values the program cannot name, not about
    refusing everything one way."""
    arguments = [OF_ANOTHER_TYPE, A_RECORD_OF_ANOTHER_TYPE]

    assert _what_the_compiler_said(arguments) == ILL_TYPED_VALUE
    assert _what_the_artefact_said(the_built_addition, arguments) == ILL_TYPED_VALUE


def test_two_numbers_are_still_added(the_built_addition):
    assert _what_the_compiler_said(["1", "2"]) == AN_ANSWER
    assert _what_the_artefact_said(the_built_addition, ["1", "2"]) == AN_ANSWER
