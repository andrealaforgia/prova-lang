"""How many digits an atom writes, counted for the digit limit.

The count decides whether a literal is read or refused, so it is asked
here about the texts that sit at the edges of it: a sign, no sign, and
the empty text no tokenizer writes today but any later caller of the
reader could.

still passes if: the count were off by one for every text alike. The
cases below pin three different texts to three different counts.
"""

from __future__ import annotations

from prova.reader import Atom


def _atom(text: str) -> Atom:
    return Atom(text, 1, 1)


def test_a_run_of_digits_counts_every_one_of_them():
    assert _atom("1234").digits_written == 4
    assert _atom("0" * 1000).digits_written == 1000


def test_a_sign_is_not_a_digit():
    assert _atom("-1234").digits_written == 4
    assert _atom("+1234").digits_written == 4


def test_a_text_with_no_characters_writes_no_digits():
    """An atom holding nothing writes 0 digits, not -1: a count below
    zero would read as a literal shorter than the empty one and would
    let any limit built on it answer about a text that was never there.
    """
    assert _atom("").digits_written == 0
