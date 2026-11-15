"""Laws the published manifest obeys for any request, not only the ones
F11's acceptance tests send.

LAW1 a field the manifest publishes for an operation, sent as a value of
     any kind the published shape does not name, is always refused as
     invalid input, and the refusal names that field.
LAW2 every field an answer carries is one the manifest publishes for that
     operation; every field published as always present is in every
     answer; every field published as present when completed is in
     exactly the completed answers.
LAW3 the signature the manifest publishes for an operator is the one the
     tool keeps: a program applying the operator to operands of the
     published argument types is checked, and the same program with one
     operand of another type is refused with a type mismatch.

Drives the `prova` command over its JSON stdin/stdout surface, as the
other property tests here do. No imports from src/prova. The manifest is
read once per process: it is a constant of the shipped tool, and each
case then sends its own request.

Derandomised with a bounded example count so the verdict does not depend
on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

import json
import subprocess

from hypothesis import given, settings
from hypothesis import strategies as st

# The operations this tool advertises as available. Written here rather
# than read at import time, so a manifest that is missing a part fails a
# case with a sentence instead of breaking collection. Every law below
# checks this list against the one the manifest carries.
THE_OPERATIONS_AN_AGENT_MAY_CALL = (
    "check",
    "examples",
    "evaluate",
    "discover",
    "verify",
)

# SPEC.md lines 178-189: the eleven operators of core-0, and the operand
# each type of argument is written with in the programs below.
THE_OPERATORS = (
    "+", "-", "*", "<", "<=", ">", ">=", "=", "and", "or", "not",
)
OPERAND_OF = {"Int": "cents", "Bool": "flag"}
A_VALUE_OF = {"Int": "4", "Bool": "false"}

A_PROGRAM = """\
(defn twice
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (ensures (= result (* n 2)))
  (examples (example (twice 2) => 4))
  (* n 2))
"""
EVERY_KIND_OF_SOURCE = (
    A_PROGRAM,
    "",
    "(defn",
    "(defn f (sig ((n Int)) -> Int ! pure) (+ n true))",
    "(deftype T (record (f T)))",
)
_MANIFEST: list = []


def _ask(request: dict) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=20.0,
    )
    assert proc.returncode == 0, (
        f"the tool exited {proc.returncode} for {request!r} instead of "
        f"answering: {proc.stderr[-500:]!r}"
    )
    return json.loads(proc.stdout)


def _manifest() -> dict:
    if not _MANIFEST:
        answer = _ask({"operation": "discover"})
        result = answer.get("result")
        assert isinstance(result, dict), f"`discover` carried no manifest: {answer}"
        _MANIFEST.append(result)
    return _MANIFEST[0]


def _shape_of(operation: str) -> dict:
    shapes = _manifest().get("operation_schemas")
    assert isinstance(shapes, dict), (
        f"the manifest publishes no request and answer shapes: "
        f"{sorted(_manifest())}. An agent cannot write a request for "
        f"{operation!r} without them."
    )
    assert operation in shapes, (
        f"the manifest publishes shapes for {sorted(shapes)} and none for "
        f"{operation!r}, which it advertises as available."
    )
    return shapes[operation]


def _request_for(operation: str, shape: dict) -> dict:
    request = {"operation": operation}
    for field, described in shape["request"]["fields"].items():
        if field == "source":
            request[field] = A_PROGRAM
        elif field == "function":
            request[field] = "twice"
        elif "list" in described["kind"]:
            request[field] = ["3"]
        else:
            request[field] = "3"
    return request


def _values_that_are_not(kind: str):
    if "list" in kind:
        return st.sampled_from([7, "a text", {}, None, True, [7], ["3", 7]])
    return st.sampled_from([7, 3.5, None, True, [], {}, ["3"]])


def _program_applying(operator: str, operands: tuple[str, ...], answer_type: str) -> str:
    call = f"({operator} {' '.join(operands)})"
    return (
        "(defn probe\n"
        f"  (sig ((cents Int) (flag Bool)) -> {answer_type} ! pure)\n"
        f"  (examples (example (probe 2 true) => {A_VALUE_OF[answer_type]}))\n"
        f"  {call})\n"
    )


@given(operation=st.sampled_from(THE_OPERATIONS_AN_AGENT_MAY_CALL), data=st.data())
@settings(max_examples=15, deadline=None)
def test_a_published_field_of_another_kind_is_always_refused_by_name(operation, data):
    """LAW1: a published request field sent as another kind of value is
    refused as invalid input, naming the field."""
    shape = _shape_of(operation)
    fields = sorted(shape["request"]["fields"])
    if not fields:
        return
    field = data.draw(st.sampled_from(fields))
    kind = shape["request"]["fields"][field]["kind"]
    request = _request_for(operation, shape)
    request[field] = data.draw(_values_that_are_not(kind))

    answer = _ask(request)

    assert answer["status"] == "invalid_input", (
        f"{operation!r} answered {answer['status']!r} to a request whose "
        f"{field!r} carries {request[field]!r}, while its published shape "
        f"names that field a {kind!r}: {answer}. A published shape the tool "
        "does not keep sends a client to repair the wrong thing."
    )
    named = " ".join(str(d.get("symbol", "")) for d in answer.get("diagnostics", []))
    assert field in named, (
        f"the refusal of {operation!r} names {named!r}, and the field at "
        f"fault is {field!r}: a client repairing its request has to be told "
        "which field to look at."
    )


@given(
    operation=st.sampled_from(THE_OPERATIONS_AN_AGENT_MAY_CALL),
    source=st.sampled_from(EVERY_KIND_OF_SOURCE),
    function=st.sampled_from(["twice", "absent", ""]),
    arguments=st.sampled_from([["3"], [], ["(Clock 12)"], ["3", "4"]]),
)
@settings(max_examples=15, deadline=None)
def test_every_answer_carries_the_fields_the_manifest_publishes(
    operation, source, function, arguments
):
    """LAW2: an answer carries no field the manifest leaves out, and
    carries every field the manifest promises."""
    shape = _shape_of(operation)
    request = _request_for(operation, shape)
    supplied = {"source": source, "function": function, "arguments": arguments}
    for field in list(request):
        if field in supplied:
            request[field] = supplied[field]

    answer = _ask(request)
    published = shape["response"]["fields"]

    assert set(answer) <= set(published), (
        f"the answer of {operation!r} carries "
        f"{sorted(set(answer) - set(published))}, which the manifest does "
        f"not publish: {sorted(published)}. A field a client cannot look up "
        "tells it nothing."
    )
    for field, described in published.items():
        if described["presence"] == "always":
            assert field in answer, (
                f"the answer of {operation!r} carries no {field!r} and the "
                f"manifest promises it in every answer: {answer}."
            )
        elif described["presence"] == "when completed":
            assert (field in answer) == (answer["status"] == "completed"), (
                f"the answer of {operation!r} has status "
                f"{answer['status']!r} and "
                f"{'carries' if field in answer else 'carries no'} "
                f"{field!r}, while the manifest publishes it as 'when "
                "completed'."
            )


@given(operator=st.sampled_from(THE_OPERATORS))
@settings(max_examples=11, deadline=None)
def test_the_published_signature_of_an_operator_is_the_one_the_tool_keeps(operator):
    """LAW3: a program applying an operator to operands of its published
    argument types is checked, and the same program with one operand of
    another type is refused with a type mismatch."""
    operators = (_manifest().get("language") or {}).get("operators")
    assert isinstance(operators, dict) and operator in operators, (
        f"the manifest publishes the operators {sorted(operators or {})} and "
        f"nothing about {operator!r}, which core-0 has (SPEC.md lines "
        "178-189). An agent writing a program has to guess it."
    )
    published = operators[operator]
    argument_types = list(published["arguments"])
    answer_type = published["result"]
    assert answer_type in A_VALUE_OF, (
        f"the manifest says {operator!r} answers {answer_type!r}, which is "
        "not a type a program can declare a function to answer."
    )
    # A type name that is not one of core-0's own stands for any core
    # type: the program is written with whole numbers in those places.
    fixed = [t if t in OPERAND_OF else "Int" for t in argument_types]
    operands = tuple(OPERAND_OF[t] for t in fixed)
    other = "flag" if operands[0] == "cents" else "cents"

    checked = _ask(
        {
            "operation": "check",
            "source": _program_applying(operator, operands, answer_type),
        }
    )
    assert checked["status"] == "completed", (
        f"a program applying {operator!r} to operands of the published "
        f"types {argument_types} was answered {checked['status']!r}: "
        f"{checked}. A signature an agent cannot write a program from is "
        "worse than none."
    )

    twisted = _ask(
        {
            "operation": "check",
            "source": _program_applying(
                operator, (other,) + operands[1:], answer_type
            ),
        }
    )
    categories = [d.get("category") for d in twisted.get("diagnostics", [])]
    assert twisted["status"] == "invalid_program" and "type_mismatch" in categories, (
        f"a program applying {operator!r} to an operand of another type was "
        f"answered {twisted['status']!r} with {categories}: {twisted}. A "
        "published signature the tool does not keep lets an agent write a "
        "program the tool will not take."
    )
