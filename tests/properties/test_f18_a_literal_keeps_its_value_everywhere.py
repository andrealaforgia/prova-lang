"""Every value a literal can take, in every place the encoder reads one.

Three review rounds each found one more place where a literal's sign or
magnitude could be mangled without any test noticing. This file closes
the family by construction instead of one shape at a time: the literal
is a dimension here, crossed with the position it sits in, and every
cell is a program whose promise sits exactly at the boundary the literal
sets -- so a literal read with the wrong sign, truncated to a machine
word, or rounded, makes the tool and the evaluator disagree.

Each cell asks the one public entry what the program owes and then runs
the program over the boundary input through the same entry, which is the
differential check: whatever came back proved must never be refused for
the promise it was proved to keep.

The real entry is called in process rather than as a command, which the
test mandates allow for a driving port: 288 cells as subprocesses would
cost minutes, and the whole file runs in a few seconds this way. The
acceptance tests beside it drive the command itself.

Deterministic: the cells are a fixed grid, not a sample, so the verdict
never depends on which cases a generator happened to draw.
"""

from __future__ import annotations

import json

import pytest

from prova import service

A = "=>"

# Every value a literal is read at: nothing, one either way, two either
# way, the edges of a 32-bit and a 64-bit word from both sides, past an
# unsigned 64-bit word, and 30 digits either way, which no machine word
# holds.
THE_VALUES = (
    0,
    1,
    -1,
    2,
    -2,
    2**31 - 1,
    2**31 + 1,
    -(2**31),
    2**63 - 1,
    2**63,
    -(2**63),
    -(2**63) - 1,
    2**64,
    -(2**64),
    10**29,
    -(10**29),
)


def _function(name, parameter, returns, requires, ensures, examples, body):
    lines = [f"(defn {name}", f"  (sig (({parameter} {returns[0]})) -> {returns[1]} ! pure)"]
    if requires:
        lines.append(f"  (requires {requires})")
    if ensures:
        lines.append(f"  (ensures {ensures})")
    lines.append("  (examples " + " ".join(examples) + ")")
    lines.append(f"  {body})")
    return "\n".join(lines) + "\n"


def _over_x(requires, ensures, examples, body, returns="Int", before=""):
    return before + _function(
        "f", "x", ("Int", returns), requires, ensures, examples, body
    )


# One builder per place the encoder reads a literal. Each answers the
# source and the input to replay at: the boundary the literal sets.
def _greater_on_the_right(v):
    return _over_x(
        f"(> x {v})",
        f"(>= result {v + 1})",
        [f"(example (f {v + 1}) {A} {v + 1})"],
        "x",
    ), v + 1


def _less_on_the_left(v):
    return _over_x(
        f"(< {v} x)",
        f"(>= result {v + 1})",
        [f"(example (f {v + 1}) {A} {v + 1})"],
        "x",
    ), v + 1


def _at_least_on_the_right(v):
    return _over_x(
        f"(>= x {v})",
        f"(> result {v - 1})",
        [f"(example (f {v}) {A} {v})"],
        "x",
    ), v


def _at_most_on_the_left(v):
    return _over_x(
        f"(<= {v} x)",
        f"(> result {v - 1})",
        [f"(example (f {v}) {A} {v})"],
        "x",
    ), v


def _greater_on_the_left(v):
    return _over_x(
        f"(> {v} x)",
        f"(< result {v})",
        [f"(example (f {v - 1}) {A} {v - 1})"],
        "x",
    ), v - 1


def _at_most_on_the_right(v):
    return _over_x(
        f"(<= x {v})",
        f"(< result {v + 1})",
        [f"(example (f {v}) {A} {v})"],
        "x",
    ), v


def _equality(v):
    return _over_x(
        f"(or (= x {v}) (> x {v + 1}))",
        f"(>= result {v})",
        [f"(example (f {v}) {A} {v})"],
        "x",
    ), v


def _inside_a_promise(v):
    return _over_x(
        f"(> x {v})",
        f"(and (>= result {v + 1}) (or (> result {v}) (= result {v + 1})))",
        [f"(example (f {v + 1}) {A} {v + 1})"],
        "x",
    ), v + 1


def _the_left_factor(v):
    return _over_x(
        "(> x 0)", _what_a_factor_promises(v), [f"(example (f 1) {A} {v})"], f"(* {v} x)"
    ), 1


def _the_right_factor(v):
    return _over_x(
        "(> x 0)", _what_a_factor_promises(v), [f"(example (f 1) {A} {v})"], f"(* x {v})"
    ), 1


def _what_a_factor_promises(v):
    if v > 0:
        return f"(>= result {v})"
    if v < 0:
        return f"(<= result {v})"
    return "(= result 0)"


def _added(v):
    return _over_x(
        "(> x 0)",
        f"(> result {v})",
        [f"(example (f 1) {A} {v + 1})"],
        f"(+ x {v})",
    ), 1


def _taken_from(v):
    return _over_x(
        "(> x 0)",
        f"(< result {v})",
        [f"(example (f 1) {A} {v - 1})"],
        f"(- {v} x)",
    ), 1


def _taken_away(v):
    return _over_x(
        f"(> x {v})",
        "(> result 0)",
        [f"(example (f {v + 1}) {A} 1)"],
        f"(- x {v})",
    ), v + 1


def _the_first_clause(v):
    return _over_x(
        None,
        f"(= result (if (= x {v}) 1 2))",
        [f"(example (f {v}) {A} 1)", f"(example (f {v + 1}) {A} 2)"],
        f"(match x ({v} 1) (_ 2))",
    ), v


def _a_middle_clause(v):
    return _over_x(
        None,
        f"(= result (if (= x {v + 1}) 0 (if (= x {v}) 1 2)))",
        [f"(example (f {v}) {A} 1)", f"(example (f {v + 1}) {A} 0)"],
        f"(match x ({v + 1} 0) ({v} 1) (_ 2))",
    ), v


def _a_record_field(v):
    """The field is pinned against the same number written another way,
    so a value read with the wrong sign or magnitude cannot satisfy it."""
    return _over_x(
        None,
        f"(= (.amount result) (+ {v - 1} 1))",
        [f"(example (f 1) {A} (Box {v}))"],
        f"(Box {v})",
        returns="Box",
        before="(deftype Box (record (amount Int)))\n\n",
    ), 1


def _a_call_argument(v):
    callee = _function(
        "g", "y", ("Int", "Int"), f"(> y {v})", f"(> result {v})",
        [f"(example (g {v + 1}) {A} {v + 1})"], "y",
    )
    return _over_x(
        "(> x 0)",
        f"(> result {v})",
        [f"(example (f 1) {A} {v + 1})"],
        f"(g (+ x {v}))",
        before=callee + "\n",
    ), 1


def _an_example_expected_value(v):
    return _over_x(
        None,
        "(= result (+ x 1))",
        [f"(example (f {v}) {A} {v + 1})"],
        "(+ x 1)",
    ), v


def _a_boolean_clause(v):
    return _over_x(
        None,
        f"(= result (if (> x {v}) 1 2))",
        [f"(example (f {v + 1}) {A} 1)", f"(example (f {v}) {A} 2)"],
        f"(match (> x {v}) (true 1) (false 2))",
    ), v + 1


def _a_literal_call_argument(v):
    """The argument is the literal itself, and what comes back is pinned
    against the same number written another way."""
    callee = _function(
        "g", "y", ("Int", "Int"), f"(>= y {v - 1})", "(= result y)",
        [f"(example (g {v}) {A} {v})"], "y",
    )
    return _over_x(
        None,
        f"(= result (+ {v - 1} 1))",
        [f"(example (f 1) {A} {v})"],
        f"(g {v})",
        before=callee + "\n",
    ), 1


THE_POSITIONS = (
    ("a literal as the argument of a call", _a_literal_call_argument),
    ("the pattern of a boolean clause", _a_boolean_clause),
    ("greater, literal on the right", _greater_on_the_right),
    ("less, literal on the left", _less_on_the_left),
    ("at least, literal on the right", _at_least_on_the_right),
    ("at most, literal on the left", _at_most_on_the_left),
    ("greater, literal on the left", _greater_on_the_left),
    ("at most, literal on the right", _at_most_on_the_right),
    ("either side of an equality", _equality),
    ("an and or an or inside a promise", _inside_a_promise),
    ("the left factor of a product", _the_left_factor),
    ("the right factor of a product", _the_right_factor),
    ("the right operand of a sum", _added),
    ("the left operand of a difference", _taken_from),
    ("the right operand of a difference", _taken_away),
    ("the pattern of a first clause", _the_first_clause),
    ("the pattern of a middle clause", _a_middle_clause),
    ("the value of a record field", _a_record_field),
    ("the argument of a call", _a_call_argument),
    ("the expected value of an example", _an_example_expected_value),
)

THE_CELLS = [
    pytest.param(value, name, build, id=f"{name.replace(' ', '-')}-at-{value}")
    for name, build in THE_POSITIONS
    for value in THE_VALUES
]


def _answer(request: dict) -> dict:
    return json.loads(service.answer_text(request))


@pytest.mark.parametrize("value,where,build", THE_CELLS)
def test_a_literal_keeps_its_value_wherever_the_encoder_reads_one(
    value, where, build
):
    """Given a program whose promise sits exactly at the boundary a
    literal sets, when the Owner asks what it owes and then runs it over
    the boundary input, then every obligation comes back proved and the
    run is not refused for the promise that was proved."""
    source, boundary = build(value)

    owed = _answer({"operation": "verify", "source": source})
    assert owed["status"] == "completed", (
        f"WHAT: a program with {value} as {where} is answered "
        f"{owed['status']!r}. "
        "WHY: it is a core-0 program of this fragment; a refusal here means "
        "this cell says nothing about the literal it is for. "
        f"HOW: the program was:\n{source}\n{owed}"
    )
    unsettled = [
        (entry["id"], entry["result"], entry.get("reason", "")[:120])
        for entry in owed["result"]["inventory"]["obligations"]
        if entry["result"] != "proved"
    ]
    assert not unsettled, (
        f"WHAT: with {value} as {where}, {unsettled} did not come back "
        "proved. "
        "WHY: the promise of this program is exactly the boundary the "
        "literal sets, so it holds if and only if the literal is read at the "
        "value it is written at. "
        f"HOW: the program was:\n{source}"
    )

    ran = _answer(
        {
            "operation": "evaluate",
            "source": source,
            "function": "f",
            "arguments": [str(boundary)],
        }
    )
    refusals = {d.get("category") for d in (ran.get("diagnostics") or [])}
    assert "postcondition_violation" not in refusals, (
        f"WHAT: with {value} as {where}, every obligation came back proved "
        f"and running the program over {boundary} is refused for the promise "
        "that was proved. "
        "WHY: the solver and the evaluator read one language; the two "
        "disagreeing means one of them is wrong, and a reader was told the "
        f"promise holds. HOW: the program was:\n{source}\n{ran}"
    )
    assert "precondition_violation" not in refusals, (
        f"WHAT: {boundary} does not meet what the program asks of its input, "
        f"with {value} as {where}. "
        "WHY: this cell replays at the boundary the literal sets, and a "
        "boundary outside the accepted domain would make the check above "
        f"vacuous. HOW: the program was:\n{source}\n{ran}"
    )
