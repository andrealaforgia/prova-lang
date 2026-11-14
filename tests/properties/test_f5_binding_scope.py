"""Property tests for feature F5's two laws about local bindings.

LAW1 is a universal claim over binder names: a `let` binding or a
pattern variable is accepted exactly when its name is not already
visible where it is introduced (a parameter, a declared function, a
builtin operator) and is not the reserved word `result`. Hand-picked
examples cannot carry it: a rule that only compared a binder with the
parameters, or that only looked at `let`, would pass them.

LAW2 is a universal claim over clause counts: a pattern variable is
visible only inside its own clause, so one spelling may be bound by any
number of disjoint clauses, however many there are.

Both domains are finite and swept exhaustively, one parametrized case
each, so no verdict depends on a seed.

Exercises the published `check` operation of the tool's request
interface, with the categories it answers with, and no internal symbol
of the checker.
"""

from __future__ import annotations

import pytest

from prova import service

SHADOWED_BINDING_CATEGORY = "shadowed_binding"
RESERVED_NAME_CATEGORY = "reserved_name"

# The name of the parameter each program below declares, and the name of
# the other function it declares: what a binder inside the body would
# hide.
THE_LET_PARAMETER = "cents"
THE_MATCHED_PARAMETER = "b"
THE_OTHER_FUNCTION = "offset"
A_BUILTIN_OPERATOR = "not"
THE_RESERVED_WORD = "result"
FREE_NAMES = ("raised", "amount")

ANOTHER_FUNCTION = (
    "(defn offset\n"
    "  (sig () -> Int ! pure)\n"
    "  (examples (example (offset) => 1))\n"
    "  1)\n"
)

A_RECORD = "(deftype Box (record (held Int)))\n"


def _check(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "check", "source": source})


def _categories(response: dict) -> list[str]:
    return [d.get("category", "") for d in response.get("diagnostics") or []]


def _let_binding(name: str) -> str:
    return (
        ANOTHER_FUNCTION
        + "(defn probe\n"
        + f"  (sig (({THE_LET_PARAMETER} Int)) -> Int ! pure)\n"
        + "  (examples (example (probe 4) => 9))\n"
        + f"  (let (({name} (+ {THE_LET_PARAMETER} 5))) {name}))\n"
    )


def _pattern_variable(name: str) -> str:
    return (
        A_RECORD
        + ANOTHER_FUNCTION
        + "(defn probe\n"
        + f"  (sig (({THE_MATCHED_PARAMETER} Box)) -> Int ! pure)\n"
        + "  (examples (example (probe (Box 5)) => 5))\n"
        + f"  (match {THE_MATCHED_PARAMETER} ((Box {name}) {name})))\n"
    )


def _binder_cases() -> list:
    cases = []
    for shape, program, parameter in (
        ("let", _let_binding, THE_LET_PARAMETER),
        ("pattern", _pattern_variable, THE_MATCHED_PARAMETER),
    ):
        hidden = (
            (parameter, SHADOWED_BINDING_CATEGORY),
            (THE_OTHER_FUNCTION, SHADOWED_BINDING_CATEGORY),
            (A_BUILTIN_OPERATOR, SHADOWED_BINDING_CATEGORY),
            (THE_RESERVED_WORD, RESERVED_NAME_CATEGORY),
        )
        for name, category in hidden:
            cases.append(pytest.param(program(name), name, category, id=f"{shape}-{name}"))
        for name in FREE_NAMES:
            cases.append(pytest.param(program(name), name, None, id=f"{shape}-{name}"))
    return cases


@pytest.mark.parametrize("source,name,refusal", _binder_cases())
def test_a_binder_is_refused_exactly_when_its_name_is_taken(
    source: str, name: str, refusal: str | None
):
    """For every binder name: the program is invalid, with the refusal
    the taken name earns, exactly when the name is already visible or is
    the reserved word; otherwise it is accepted with no diagnostic."""
    response = _check(source)

    if refusal is None:
        assert response["status"] == "completed", (
            f"a binding named {name!r}, which hides nothing and is not reserved, was "
            f"not accepted: {response}. Only a taken name may be refused."
        )
        assert response.get("diagnostics") in (None, []), (
            f"a binding named {name!r} was accepted with diagnostics {response}. A "
            "program that breaks no rule carries no diagnostic."
        )
        return

    assert response["status"] == "invalid_program", (
        f"a binding named {name!r}, which is already taken, was not refused: "
        f"{response}. A binder may not take a name that is already visible, and may "
        "never be `result`."
    )
    assert _categories(response).count(refusal) == 1, (
        f"a binding named {name!r} was answered with {_categories(response)} instead "
        f"of exactly one {refusal!r}: {response}. One offending binder is one defect "
        "with one repair; report it once, under the category that names the rule."
    )
    assert name in response["diagnostics"][0].get("reason", ""), (
        f"the refusal does not name the binder {name!r}: {response}. Name the binder "
        "the reader must rename."
    )


def _colour_union(clause_count: int) -> str:
    variants = " ".join(f"(V{index} (shade Int))" for index in range(clause_count))
    return f"(deftype Colour (union {variants}))\n"


def _clauses_binding(spellings: list[str]) -> str:
    return " ".join(
        f"((V{index} {spelling}) {spelling})"
        for index, spelling in enumerate(spellings)
    )


def _matching_colours(spellings: list[str]) -> str:
    return (
        _colour_union(len(spellings))
        + "(defn probe\n"
        + "  (sig ((c Colour)) -> Int ! pure)\n"
        + "  (examples (example (probe (V0 1)) => 1))\n"
        + f"  (match c {_clauses_binding(spellings)}))\n"
    )


@pytest.mark.parametrize("clause_count", [2, 3, 4, 5])
def test_one_spelling_is_free_in_every_disjoint_clause(clause_count: int):
    """For any number of clauses: all of them may bind the spelling
    `tone`, because a clause variable is visible only in its own clause;
    but a clause that binds the parameter's name `c` is refused, so the
    acceptance is about disjoint clauses and not about accepting
    everything."""
    accepted = _check(_matching_colours(["tone"] * clause_count))

    assert accepted["status"] == "completed", (
        f"{clause_count} disjoint clauses that each bind `tone` were not accepted: "
        f"{accepted}. A pattern variable is scoped to its clause, so disjoint clauses "
        "may share a spelling."
    )

    hiding = ["c"] + ["tone"] * (clause_count - 1)
    refused = _check(_matching_colours(hiding))

    assert refused["status"] == "invalid_program", (
        f"a clause that binds the parameter's name `c` among {clause_count} clauses "
        f"was not refused: {refused}. A clause variable may share a spelling with a "
        "sibling clause, never with a visible binding."
    )
    assert _categories(refused).count(SHADOWED_BINDING_CATEGORY) == 1, (
        f"one clause hiding the parameter was answered with {_categories(refused)}: "
        f"{refused}. Report the one offending clause variable once."
    )


def _nested_lets(names: list[str]) -> str:
    """A body that opens one `let` inside another, binding `names` from
    the outside in, and reads the innermost one."""
    body = names[-1]
    for name in reversed(names):
        body = f"(let (({name} 1)) {body})"
    return (
        "(defn probe\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        "  (examples (example (probe 4) => 1))\n"
        f"  {body})\n"
    )


@pytest.mark.parametrize("depth", [2, 8, 40])
def test_a_nested_let_may_not_rebind_an_enclosing_binding(depth: int):
    """For any nesting depth: `let` forms that each bind a name of their
    own are accepted however deeply they nest, and the innermost one
    rebinding the outermost binding's name is refused, naming it."""
    distinct = [f"step-{index}" for index in range(depth)]
    accepted = _check(_nested_lets(distinct))

    assert accepted["status"] == "completed", (
        f"{depth} nested let forms, each binding a name of its own, were not "
        f"accepted: {accepted}. Nesting is not hiding."
    )

    rebinding = distinct[:-1] + [distinct[0]]
    refused = _check(_nested_lets(rebinding))

    assert refused["status"] == "invalid_program", (
        f"the innermost of {depth} nested let forms rebound the outermost binding "
        f"{distinct[0]!r} and was not refused: {refused}. An enclosing let binding is "
        "a visible value binding, which a binding may not shadow."
    )
    assert _categories(refused).count(SHADOWED_BINDING_CATEGORY) == 1, (
        f"the rebinding was answered with {_categories(refused)}: {refused}. Report "
        "the one offending binding once."
    )
