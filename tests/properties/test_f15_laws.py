"""The four laws of F15, over programs a reader might have written.

Each law is checked over generated programs rather than a table of
examples, because each is stated for every accepted program and not for
a chosen few. The generator in `_f15_written_programs` builds only
programs the tool accepts, varying what a reader chooses and the
language does not: the declarations, the whole numbers, how each number
is spelled, how each declaration is laid out and where the comments
stand.

Hypothesis shrinks a failing case to a small program and prints the seed
that replays it; run a failure again with `--hypothesis-seed=<seed>`.

still passes if: the tool had answered the submitted text unchanged.
LAW2 and LAW3 would hold for an echo, but the generated sources are
written with non-canonical numbers and scattered layout, and LAW1
compares the two texts the tool itself answers, so the acceptance tests
of F15.B1 and F15.B7 are what refuse an echo; these laws state what must
hold for every program, not only for the ones written out by hand.
"""

from __future__ import annotations

from hypothesis import given, settings

from _f15_written_programs import (
    ask,
    canonical_text,
    comments_of,
    meaning_of,
    written_programs,
)

# 40 programs per law: each case reads, checks and writes out a whole
# program several times, and the suite's budget is a few seconds for the
# four laws together.
A_FEW_PROGRAMS = settings(max_examples=40, deadline=None)


def _written_out(source: str) -> str:
    answered = ask("format", source)
    assert answered["status"] == "completed", (
        f"a generated program was answered {answered['status']!r}: "
        f"{answered}\n{source}\nThe generator writes only programs the tool "
        "accepts, so a refusal here is either a defect of the tool or of the "
        "generator; read the diagnostic to tell which"
    )
    text = canonical_text(answered)
    assert isinstance(text, str) and text, (
        f"a completed answer carried no text: {answered}\n{source}"
    )
    return text


@A_FEW_PROGRAMS
@given(written_programs())
def test_writing_any_program_out_twice_answers_the_same_text(program):
    """LAW1 -- the canonical text of a program is already canonical."""
    once = _written_out(program.text)
    twice = _written_out(once)

    assert twice == once, (
        f"writing out the canonical text answered different characters.\n"
        f"source:\n{program.text}\nfirst:\n{once}\nsecond:\n{twice}\n"
        "SPEC.md line 82 says formatting is idempotent; make the layout a "
        "function of the tree and of nothing else"
    )


@A_FEW_PROGRAMS
@given(written_programs())
def test_writing_any_program_out_keeps_the_program_it_declares(program):
    """LAW2 -- the canonical text declares the same program as the
    source, apart from where its parts stand."""
    canonical = _written_out(program.text)

    before = ask("parse", program.text)
    after = ask("parse", canonical)

    assert after["status"] == "completed", (
        f"the canonical text of an accepted program was refused "
        f"{after['status']!r}: {after}\n{canonical}\nSPEC.md line 84 says "
        "formatting must not alter language validity"
    )
    assert meaning_of(after["result"]["tree"]) == meaning_of(
        before["result"]["tree"]
    ), (
        f"the canonical text declares a different program.\nsource:\n"
        f"{program.text}\ncanonical:\n{canonical}\nThe layout may move a "
        "part of a program; it may not add, drop or change one"
    )


@A_FEW_PROGRAMS
@given(written_programs())
def test_writing_any_program_out_keeps_every_comment_once_and_in_order(program):
    """LAW3 -- every comment stands once in the canonical text, in the
    order it was written."""
    canonical = _written_out(program.text)

    standing = comments_of(ask("parse", canonical)["result"]["tree"])

    assert standing == list(program.comments), (
        f"the canonical text carries the comments {standing} and the reader "
        f"wrote {list(program.comments)}.\nsource:\n{program.text}\n"
        f"canonical:\n{canonical}\nSPEC.md lines 62-63 say a formatter "
        "preserves the text and the order of comments; a lost comment drops "
        "what a reader said and a repeated one invents it"
    )


@A_FEW_PROGRAMS
@given(written_programs())
def test_writing_any_program_out_keeps_what_its_examples_answer(program):
    """LAW4 -- the canonical text is accepted and its examples answer
    what the source's examples answered."""
    canonical = _written_out(program.text)

    checked_before = ask("check", program.text)
    checked_after = ask("check", canonical)
    assert checked_after["status"] == checked_before["status"] == "completed", (
        f"checking answered {checked_before['status']!r} for the source and "
        f"{checked_after['status']!r} for its canonical text.\n{canonical}"
    )

    ran_before = ask("examples", program.text)
    ran_after = ask("examples", canonical)
    assert ran_after["result"] == ran_before["result"], (
        f"the examples answered\n{ran_before['result']}\nfor the source and\n"
        f"{ran_after['result']}\nfor its canonical text.\nsource:\n"
        f"{program.text}\ncanonical:\n{canonical}\nSPEC.md line 82 says "
        "formatting preserves meaning, so every example answers what it "
        "answered before"
    )
