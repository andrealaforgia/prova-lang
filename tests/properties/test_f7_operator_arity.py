"""Property tests for feature F7's two laws about how many arguments a
builtin operator takes.

Each law is a universal claim, checked with generated input through the
published `check` operation:

- LAW1: a program is accepted exactly when every operator in it is
  written with the number of arguments SPEC.md gives that operator, and
  refused with the published word for a wrong number of arguments
  otherwise. The generator draws one of the eleven operators and a count
  between 0 and 6, so both halves of the claim are reached by
  construction: the drawn count either is the operator's own number or
  is not.
- LAW2: a refusal of a wrong number of arguments states both counts -
  the number the operator takes and the number the program gave - for
  any operator and any wrong count in those bounds.

The table of operators and their numbers of arguments below is read from
SPEC.md lines 178-189, not from the tool under test.

Generated checks are evidence, not proof: they sample these claims over
the bounds above and over no larger program.

Exercises the published `check` operation of the tool's request
interface, with the categories it answers with, and no internal symbol
of the checker.
"""

from __future__ import annotations

from hypothesis import given, strategies as st

from prova import service

ARITY_MISMATCH_CATEGORY = "arity_mismatch"

# SPEC.md lines 178-189: every builtin operator and the number of
# arguments it takes.
THE_OPERATORS_AND_THEIR_ARITIES = {
    "+": 2,
    "-": 2,
    "*": 2,
    "<": 2,
    "<=": 2,
    ">": 2,
    ">=": 2,
    "=": 2,
    "and": 2,
    "or": 2,
    "not": 1,
}

# Which operators read true/false operands, and which answer a number.
BOOLEAN_OPERATORS = ("and", "or", "not")
OPERATORS_ANSWERING_A_NUMBER = ("+", "-", "*")

# The widest count the generator writes. Wide enough to cover both one
# too few and several too many for every operator.
THE_WIDEST_COUNT = 6


def _check(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "check", "source": source})


def _categories(response: dict) -> list[str]:
    return [d.get("category", "") for d in response.get("diagnostics") or []]


def _accepted(response: dict) -> bool:
    return response.get("status") == "completed" and not response.get("diagnostics")


def _program_applying(operator: str, argument_count: int) -> str:
    """A program whose one function applies `operator` to
    `argument_count` operands of the type that operator reads.

    Everything else about the program is valid, so the number of
    arguments is the only thing a reader can hold against it.
    """
    operand = "flag" if operator in BOOLEAN_OPERATORS else "cents"
    answer = "Int" if operator in OPERATORS_ANSWERING_A_NUMBER else "Bool"
    placeholder = "4" if answer == "Int" else "false"
    operands = " ".join([operand] * argument_count)
    call = f"({operator} {operands})" if operands else f"({operator})"
    return (
        "(defn probe\n"
        f"  (sig ((cents Int) (flag Bool)) -> {answer} ! pure)\n"
        f"  (examples (example (probe 2 true) => {placeholder}))\n"
        f"  {call})\n"
    )


@given(
    operator=st.sampled_from(sorted(THE_OPERATORS_AND_THEIR_ARITIES)),
    argument_count=st.integers(min_value=0, max_value=THE_WIDEST_COUNT),
)
def test_an_operator_is_accepted_exactly_when_it_has_its_own_number_of_arguments(
    operator: str, argument_count: int
):
    """LAW1: a program applying an operator is accepted when the number
    of arguments is the one the language gives that operator, and
    refused as a wrong number of arguments for every other count."""
    takes = THE_OPERATORS_AND_THEIR_ARITIES[operator]

    response = _check(_program_applying(operator, argument_count))

    if argument_count == takes:
        assert _accepted(response), (
            f"a program applying {operator!r} to the {takes} argument(s) the "
            f"language gives it was not accepted: {response}. Only a different "
            "number of arguments may be refused by this rule."
        )
    else:
        assert _categories(response) == [ARITY_MISMATCH_CATEGORY], (
            f"a program applying {operator!r} to {argument_count} argument(s) "
            f"instead of {takes} was answered with {_categories(response)}: "
            f"{response}. An operator has no variable arity: refuse the call, and "
            "hold nothing else against operands of the right type."
        )
        assert response.get("status") == "invalid_program", (
            f"a program applying {operator!r} to {argument_count} argument(s) was "
            f"not reported as an invalid program: {response}."
        )


@given(
    operator=st.sampled_from(sorted(THE_OPERATORS_AND_THEIR_ARITIES)),
    offset=st.integers(min_value=1, max_value=THE_WIDEST_COUNT),
    fewer=st.booleans(),
)
def test_a_refusal_states_the_number_taken_and_the_number_given(
    operator: str, offset: int, fewer: bool
):
    """LAW2: for any operator and any wrong number of arguments, the
    refusal states the number the operator takes and the number the
    program gave, so a reader repairs the call without counting
    anything again."""
    takes = THE_OPERATORS_AND_THEIR_ARITIES[operator]
    # Every operator takes at least one argument, so a count below its
    # own, floored at none at all, is always a wrong count.
    given_count = max(takes - offset, 0) if fewer else takes + offset

    response = _check(_program_applying(operator, given_count))

    refusals = [
        d
        for d in response.get("diagnostics") or []
        if d.get("category") == ARITY_MISMATCH_CATEGORY
    ]
    assert len(refusals) == 1, (
        f"a program applying {operator!r} to {given_count} argument(s) instead of "
        f"{takes} drew {len(refusals)} refusal(s) about the number of arguments: "
        f"{response}. One wrong call is one defect with one repair."
    )
    reason = refusals[0].get("reason", "")
    assert f"takes exactly {takes}" in reason, (
        f"the refusal does not say {operator!r} takes exactly {takes} argument(s), "
        f"so a reader does not learn how many to write: {reason!r}."
    )
    assert f"got {given_count}" in reason, (
        f"the refusal does not say the program gave {given_count} argument(s), so "
        f"a reader cannot see what is wrong with the call as written: {reason!r}."
    )
    location = refusals[0].get("location") or {}
    assert (location.get("line"), location.get("column")) == (4, 3), (
        f"the refusal points at {location}, but the {operator!r} call stands at "
        f"line 4 column 3: {refusals[0]}. Report the place of the call that has "
        "the wrong number of arguments."
    )
