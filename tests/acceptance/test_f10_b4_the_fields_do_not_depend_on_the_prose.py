"""F10.B4 -- the category and the fields belong to the defect, not to
the sentence that describes it.

The same defect answered by three operations, and the same defect in a
source whose other text changed, carries the same category and the same
fields. A client that stores them keeps them across a reworded message.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the tool reported nothing but a category, which is
trivially equal across operations. Each comparison is against a pinned
field set, so a missing symbol, expectation or place is seen; and the
last test requires two different defects to differ, so a tool answering
one fixed entry for everything is seen.
"""

from __future__ import annotations

from _f10_diagnostic_fixtures import (
    TYPE_ERRORS,
    WELL_FORMED,
    check,
    diagnostics,
    examples,
    revision_of,
    structured,
    the_one_refusal,
    verify,
)

WHY = "a body that does not have the declared return type"
CASE = TYPE_ERRORS[WHY]

# Everything a client acts on for this defect, prose excluded.
FIELDS = {
    "category": "type_mismatch",
    "source_revision": revision_of(CASE.source),
    "symbol": "fare",
    "expected": "Bool",
    "actual": "Int",
    "location": {"line": 4, "column": 3},
}

# A function the defective program does not call, appended after it so
# no line of the defect moves.
UNRELATED_TAIL = """\
(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (examples (example (doubled 2) => 4))
  (* n 2))
"""


def test_three_operations_answer_the_same_defect_with_the_same_fields():
    """Given one program whose body does not have its declared return
    type, when it is checked, when its examples are run and when it is
    verified, then all 3 answers carry the identical 6 fields."""
    answers = {
        "check": check(CASE.source),
        "examples": examples(CASE.source),
        "verify": verify(CASE.source),
    }
    for operation, response in answers.items():
        entry = the_one_refusal(response, f"{WHY} answered by {operation}")
        assert structured(entry) == FIELDS, (
            f"the {operation} answer carries {structured(entry)}, expected "
            f"{FIELDS}: {entry}. One defect is one category with one set of "
            "fields, whichever operation met it."
        )


def test_other_text_in_the_source_does_not_change_the_fields():
    """Given the same defect in a source that declares one more
    function after it, when it is checked, then the category, the symbol
    and both types are unchanged and only the revision differs."""
    grown = CASE.source + UNRELATED_TAIL
    entry = the_one_refusal(check(grown), f"{WHY} in a longer source")

    assert structured(entry) == {**FIELDS, "source_revision": revision_of(grown)}, (
        f"adding an unrelated declaration changed the fields of the refusal: "
        f"{entry}. The fields come from the defect, so unrelated text leaves "
        "them alone."
    )


def test_two_different_defects_do_not_carry_the_same_fields():
    """Control: given the 3 different type errors, when each is checked,
    then the 3 refusals carry 3 different field sets."""
    seen = {
        why: tuple(sorted(structured(the_one_refusal(check(case.source), why)).items(), key=str))
        for why, case in TYPE_ERRORS.items()
    }
    assert len(set(seen.values())) == 3, (
        f"different defects came back with the same fields: {seen}. A client "
        "tells them apart by the fields alone."
    )
    assert not diagnostics(check(WELL_FORMED)), check(WELL_FORMED)
