"""Property tests for feature F8's law about whose example an example is.

The law is a universal claim, checked with generated input through the
published `check` operation:

- LAW1: a program is accepted exactly when every declared example calls
  the function that declares it, with the number of arguments that
  function takes; otherwise it is refused, with the published word for
  an example about another function when the example calls another name,
  and with the published word for a wrong number of arguments when it
  calls its own function with another count.
- LAW2: a refusal of an example about another function names both the
  function left without an example and the function the example calls,
  for any pair of names the generator draws.

The generator draws the case first - the example is about its own
function, about another declared function, about a name the program
never declares, or about its own function with one argument too many or
too few - and then builds a program that is in that case by
construction, so every branch of the claim is reached without filtering.

SPEC.md lines 228-234 are where the law comes from: "Every function
needs an example directly calling that same function. Arguments and
expected outputs must be closed values of the declared types... An
unrelated expression cannot stand in for an example of the function."

Generated checks are evidence, not proof: they sample this claim over
programs of at most 3 functions of at most 2 parameters, and over no
larger program.

Exercises the published `check` operation of the tool's request
interface, with the categories it answers with, and no internal symbol
of the checker.
"""

from __future__ import annotations

from hypothesis import given, strategies as st

from prova import service

UNRELATED_EXAMPLE_CATEGORY = "unrelated_example"
ARITY_MISMATCH_CATEGORY = "arity_mismatch"

# The name no generated program ever declares.
A_NAME_THE_PROGRAM_NEVER_DECLARES = "absent-probe"

# How large a generated program gets: functions, and parameters each.
THE_MOST_FUNCTIONS = 3
THE_MOST_PARAMETERS = 2

# The cases a declared example can be in. The first is the only one the
# language accepts; the others are the ways SPEC.md lines 228-234 say an
# example is not an example of the function that declares it.
ABOUT_ITS_OWN_FUNCTION = "about its own function"
ABOUT_ANOTHER_DECLARED_FUNCTION = "about another declared function"
ABOUT_A_NAME_NEVER_DECLARED = "about a name never declared"
ONE_ARGUMENT_TOO_MANY = "one argument too many"
ONE_ARGUMENT_TOO_FEW = "one argument too few"

THE_CASES_A_WRONG_NAME_MAKES = (
    ABOUT_ANOTHER_DECLARED_FUNCTION,
    ABOUT_A_NAME_NEVER_DECLARED,
)
THE_CASES_A_WRONG_COUNT_MAKES = (ONE_ARGUMENT_TOO_MANY, ONE_ARGUMENT_TOO_FEW)


def _check(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "check", "source": source})


def _categories(response: dict) -> list[str]:
    return [d.get("category", "") for d in response.get("diagnostics") or []]


def _accepted(response: dict) -> bool:
    return response.get("status") == "completed" and not response.get("diagnostics")


def _name(ordinal: int) -> str:
    return f"probe-{ordinal}"


def _function(name: str, parameters: int, example_call: str) -> str:
    params = " ".join(f"(p{i} Int)" for i in range(parameters))
    return (
        f"(defn {name}\n"
        f"  (sig ({params}) -> Int ! pure)\n"
        f"  (examples (example ({example_call}) => 1))\n"
        f"  1)\n"
    )


def _call(name: str, arguments: int) -> str:
    return " ".join([name] + ["1"] * arguments)


THE_CASES = (
    ABOUT_ITS_OWN_FUNCTION,
    ABOUT_ANOTHER_DECLARED_FUNCTION,
    ABOUT_A_NAME_NEVER_DECLARED,
    ONE_ARGUMENT_TOO_MANY,
    ONE_ARGUMENT_TOO_FEW,
)


@st.composite
def a_program_and_its_case(draw, cases=THE_CASES):
    """One program whose declared examples are all about their own
    functions except, when the drawn case says so, the example of one
    chosen function.

    Returns the program's source, the case it is in, the name of the
    function whose example was changed and the name its example calls.
    """
    case = draw(st.sampled_from(cases))
    fewest_functions = 2 if case == ABOUT_ANOTHER_DECLARED_FUNCTION else 1
    count = draw(st.integers(fewest_functions, THE_MOST_FUNCTIONS))
    parameters = draw(
        st.lists(
            st.integers(0, THE_MOST_PARAMETERS), min_size=count, max_size=count
        )
    )
    chosen = draw(st.integers(0, count - 1))
    if case == ONE_ARGUMENT_TOO_FEW:
        # Writing one argument fewer than none is not a program a reader
        # can write, so the chosen function takes at least one.
        parameters[chosen] = draw(st.integers(1, THE_MOST_PARAMETERS))
    others = [ordinal for ordinal in range(count) if ordinal != chosen]
    other = (
        draw(st.sampled_from(others))
        if case == ABOUT_ANOTHER_DECLARED_FUNCTION
        else None
    )

    if case == ABOUT_ITS_OWN_FUNCTION:
        called, arguments = _name(chosen), parameters[chosen]
    elif case == ABOUT_ANOTHER_DECLARED_FUNCTION:
        called, arguments = _name(other), parameters[other]
    elif case == ABOUT_A_NAME_NEVER_DECLARED:
        called, arguments = A_NAME_THE_PROGRAM_NEVER_DECLARES, parameters[chosen]
    elif case == ONE_ARGUMENT_TOO_MANY:
        called, arguments = _name(chosen), parameters[chosen] + 1
    else:
        called, arguments = _name(chosen), parameters[chosen] - 1

    blocks = [
        _function(
            _name(ordinal),
            parameters[ordinal],
            _call(called, arguments)
            if ordinal == chosen
            else _call(_name(ordinal), parameters[ordinal]),
        )
        for ordinal in range(count)
    ]
    return "\n".join(blocks), case, _name(chosen), called


@given(a_program_and_its_case())
def test_a_program_is_accepted_exactly_when_every_example_is_about_its_own_function(
    drawn,
):
    """LAW1: the tool accepts a program when each example calls the
    function declaring it with the number of arguments that function
    takes, and refuses it with the published word for the defect
    otherwise."""
    source, case, owner, called = drawn

    response = _check(source)

    if case == ABOUT_ITS_OWN_FUNCTION:
        assert _accepted(response), (
            f"a program whose every example calls its own function with the number "
            f"of arguments that function takes was refused with "
            f"{_categories(response)}: {response}. Source:\n{source}\nOnly an "
            "example about another function, or with another number of arguments, "
            "may be refused for this rule."
        )
        return

    expected = (
        UNRELATED_EXAMPLE_CATEGORY
        if case in THE_CASES_A_WRONG_NAME_MAKES
        else ARITY_MISMATCH_CATEGORY
    )
    assert _categories(response) == [expected], (
        f"a program whose example of {owner!r} is {case} was answered with "
        f"{_categories(response)}, expected exactly [{expected!r}]: {response}. "
        f"Source:\n{source}\nOne example that is not about its own function is one "
        "defect with one repair; report it once, with the word its defect carries."
    )


@given(a_program_and_its_case(cases=THE_CASES_A_WRONG_NAME_MAKES))
def test_a_refusal_names_the_function_left_without_an_example_and_the_one_called(
    drawn,
):
    """LAW2: the refusal of an example about another function names both
    functions, so a reader sees which two names the repair stands
    between."""
    source, _case, owner, called = drawn

    reason = (_check(source).get("diagnostics") or [{}])[0].get("reason", "")

    assert repr(owner) in reason and repr(called) in reason, (
        f"the refusal {reason!r} does not name both {owner!r}, the function left "
        f"without an example of its own, and {called!r}, the function its example "
        f"calls. Source:\n{source}\nName both, so a reader can repair the example "
        "without searching the program."
    )
