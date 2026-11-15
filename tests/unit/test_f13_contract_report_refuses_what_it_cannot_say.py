"""The two things a contract report refuses to be, and the report it does
build.

Both refusals can only be reached by building a report by hand, past the
reader and the checker: a strength the tool does not publish, and one
function recorded twice. A reader of an answer must be able to look up
every word in it and to count each function once, so neither can be built
at all.

A unit test of the module's own contract, as the other tests in this
directory are.
"""

from __future__ import annotations

import pytest

from prova import checker


def _strength(name: str):
    kind = getattr(checker, "ContractStrength", None)
    assert kind is not None, (
        "the checker has no value standing for how much a contract block "
        "promises, so a report cannot say that a block is omitted, trivial "
        "or stated."
    )
    return kind


def _report():
    kind = getattr(checker, "ContractReport", None)
    assert kind is not None, (
        "the checker has no value holding the contract report, so nothing "
        "can say which functions promise nothing."
    )
    return kind


def _contracts_of(name: str, precondition: str, postcondition: str):
    kind = getattr(checker, "FunctionContracts", None)
    assert kind is not None, (
        "the checker has no value holding what one function's two contract "
        "blocks say."
    )
    strength = _strength("")
    return kind(name, strength.named(precondition), strength.named(postcondition))


def test_a_strength_the_tool_does_not_publish_is_refused():
    """Given the word 'meaningful', when a strength is built from it, then
    it is refused with what failed, why it matters and how to repair it."""
    with pytest.raises(ValueError) as refusal:
        _strength("")("meaningful", "the contract says something worth having")

    message = str(refusal.value)
    assert "meaningful" in message, message
    for part in ("WHAT:", "WHY:", "HOW:"):
        assert part in message, (
            f"the refusal does not say {part} {message!r}. A refusal names "
            "what failed, why it matters and how to repair it."
        )


def test_one_function_recorded_twice_in_one_report_is_refused():
    """Given two entries both naming 'twice', when a report is built from
    them, then it is refused rather than counting one function twice."""
    entry = _contracts_of("twice", "omitted", "stated")

    with pytest.raises(ValueError) as refusal:
        _report()((entry, entry))

    message = str(refusal.value)
    assert "twice" in message, message
    for part in ("WHAT:", "WHY:", "HOW:"):
        assert part in message, (
            f"the refusal does not say {part} {message!r}."
        )


def test_a_report_about_two_functions_reads_back_both_of_them():
    """Given one function with an omitted precondition and one with a
    stated postcondition, when a report holds both, then it lists the 2
    entries and says the program states a contract."""
    report = _report()(
        (
            _contracts_of("twice", "omitted", "trivial"),
            _contracts_of("thrice", "stated", "stated"),
        )
    )

    answer = report.as_dict()

    assert [entry["function"] for entry in answer["functions"]] == ["twice", "thrice"]
    assert answer["totals"] == {
        "functions": 2,
        "contracts": 4,
        "omitted": 1,
        "trivial": 1,
        "stated": 2,
    }
    assert answer["states_a_contract"] is True
