"""Property tests for feature F5's three laws about local bindings.

Each law is a universal claim, checked with generated input through the
published `check` operation:

- LAW1: a binding is refused exactly when its name is already visible
  where it stands (a parameter, an enclosing `let` binding, a declared
  function, a builtin operator) or is the reserved word `result`. The
  generator draws one of the five taken names, one of the two binder
  shapes, and, for the accepted half, a fresh lower-case name of 1 to 8
  letters that neither the program nor the language already uses.
- LAW2: a pattern variable is visible only inside its own clause, for
  any clause count the generator draws between 2 and 6.
- LAW3: `let` forms nest without hiding, for any depth the generator
  draws between 2 and 8, while rebinding an enclosing name is refused.

Generated checks are evidence, not proof: they sample these claims over
the bounds above and over no larger program.

Exercises the published `check` operation of the tool's request
interface, with the categories it answers with, and no internal symbol
of the checker.
"""

from __future__ import annotations

from hypothesis import given, strategies as st

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


SHAPES = {"let": (THE_LET_PARAMETER,), "pattern": (THE_MATCHED_PARAMETER,)}

# What each taken name earns, read by the law below. The parameter of
# the shape under test is added to it when the program is built.
TAKEN_NAMES = (
    (THE_OTHER_FUNCTION, SHADOWED_BINDING_CATEGORY),
    (A_BUILTIN_OPERATOR, SHADOWED_BINDING_CATEGORY),
    (THE_RESERVED_WORD, RESERVED_NAME_CATEGORY),
    ("the parameter of this shape", SHADOWED_BINDING_CATEGORY),
)

# A free name is one the program does not already use and the language
# does not already mean: the two boolean literals are values, not names,
# and `probe` is the function these programs declare. The generator
# found both edges, so they are named here rather than hidden.
NOT_FREE = frozenset(
    {
        THE_LET_PARAMETER,
        THE_MATCHED_PARAMETER,
        THE_OTHER_FUNCTION,
        A_BUILTIN_OPERATOR,
        THE_RESERVED_WORD,
        "probe",
        "true",
        "false",
    }
)

_free_names = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=8
).filter(lambda name: name not in NOT_FREE)


def _program_of(shape: str, name: str) -> str:
    return _let_binding(name) if shape == "let" else _pattern_variable(name)


def _parameter_of(shape: str) -> str:
    return THE_LET_PARAMETER if shape == "let" else THE_MATCHED_PARAMETER


@given(
    shape=st.sampled_from(sorted(SHAPES)),
    taken=st.sampled_from(TAKEN_NAMES),
    free=_free_names,
)
def test_a_binder_is_refused_exactly_when_its_name_is_taken(
    shape: str, taken: tuple[str, str], free: str
):
    """For every drawn binder name: the program is invalid, with the
    refusal the taken name earns, exactly when the name is already
    visible or is the reserved word; a freshly drawn name that the
    program does not bind is accepted with no diagnostic."""
    name, refusal = taken
    if name == "the parameter of this shape":
        name = _parameter_of(shape)

    response = _check(_program_of(shape, name))

    assert response["status"] == "invalid_program", (
        f"a {shape} binding named {name!r}, which is already taken, was not refused: "
        f"{response}. A binder may not take a name that is already visible, and may "
        "never be `result`."
    )
    assert _categories(response).count(refusal) == 1, (
        f"a {shape} binding named {name!r} was answered with "
        f"{_categories(response)} instead of exactly one {refusal!r}: {response}. One "
        "offending binder is one defect with one repair; report it once, under the "
        "category that names the rule."
    )
    assert name in response["diagnostics"][0].get("reason", ""), (
        f"the refusal does not name the binder {name!r}: {response}. Name the binder "
        "the reader must rename."
    )

    accepted = _check(_program_of(shape, free))

    assert accepted["status"] == "completed", (
        f"a {shape} binding named {free!r}, which hides nothing and is not reserved, "
        f"was not accepted: {accepted}. Only a taken name may be refused."
    )
    assert accepted.get("diagnostics") in (None, []), (
        f"a {shape} binding named {free!r} was accepted with diagnostics: {accepted}. "
        "A program that breaks no rule carries no diagnostic."
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


@given(clause_count=st.integers(min_value=2, max_value=6))
def test_one_spelling_is_free_in_every_disjoint_clause(clause_count: int):
    """For any drawn number of clauses: all of them may bind the spelling
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


@given(depth=st.integers(min_value=2, max_value=8))
def test_a_nested_let_may_not_rebind_an_enclosing_binding(depth: int):
    """For any drawn nesting depth: `let` forms that each bind a name of their
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
