"""F11.B2 -- an agent reads from `discover` which fields each operation
it may call takes, and which fields the answer carries, so it never has
to guess an undocumented API (SPEC.md line 475).

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the tool published a request shape and an answer shape
nobody honours. The second and third tests build a request out of the
published request shape and read five real answers back against the
published answer shape, so a published field that is never answered, and
an answered field that was never published, both fail.
"""

from __future__ import annotations

from _f11_manifest_fixtures import (
    a_value_matching,
    A_PROGRAM,
    a_program_for,
    ask,
    manifest,
    availability_of_each_operation,
    published_operation_shapes,
)

FIELD_PARTS = {"kind", "presence", "what"}
# What a request field may say about itself: a client either must send it
# or may leave it out.
PRESENCE_OF_A_REQUEST_FIELD = ("required", "optional")
# What an answer field may say about itself: it is always there, it is
# there exactly when the request was answered as completed, or it is
# there under a condition the shape states in its own words.
ALWAYS = "always"
WHEN_COMPLETED = "when completed"


def _available_operations() -> list:
    return [
        name
        for name, availability in availability_of_each_operation().items()
        if availability == "available"
    ]


def _a_request_matching(operation: str, shape: dict) -> dict:
    """A request for `operation` built only out of its published request
    shape: each field the shape names, carrying a value of the kind it
    names, and nothing else.

    The values are the ones the program the request carries takes: the
    program in the fixtures, which declares one function `twice` of one
    whole-number argument, or -- for the operation whose other field
    names what its program declares -- the machine program and the
    descriptor that names its eight parts.
    """
    request = {"operation": operation}
    for field, described in shape["request"]["fields"].items():
        request[field] = a_value_matching(operation, field, described)
    return request


def test_every_operation_an_agent_may_call_publishes_both_of_its_shapes():
    """Given the manifest, then each of the available operations carries
    the fields its request takes and the fields its answer carries, and
    each field says its kind, whether it is there and what it is for --
    beside the diagnostic schema, the profile and the limits it already
    carries."""
    shapes = published_operation_shapes()
    carried_already = manifest()

    for part in ("profile", "diagnostic_schemas", "resource_limits"):
        assert part in carried_already, (
            f"the manifest no longer carries {part!r}: "
            f"{sorted(carried_already)}. `discover` is one answer and the "
            "parts an agent reads today stay in it."
        )

    assert set(shapes) == set(_available_operations()), (
        f"the manifest publishes shapes for {sorted(shapes)} and advertises "
        f"{sorted(_available_operations())} as available. An operation an "
        "agent is invited to call and cannot read the shape of leaves it "
        "guessing; a shape for an operation it cannot call describes "
        "nothing it can do."
    )
    for operation, shape in shapes.items():
        for side in ("request", "response"):
            fields = (shape.get(side) or {}).get("fields")
            assert isinstance(fields, dict), (
                f"{operation!r} publishes no {side} fields: {shape}."
            )
            for field, described in fields.items():
                assert set(described) == FIELD_PARTS, (
                    f"the {side} field {field!r} of {operation!r} says "
                    f"{sorted(described)}, and a client needs "
                    f"{sorted(FIELD_PARTS)}."
                )
                assert described["what"].strip(), (
                    f"the {side} field {field!r} of {operation!r} says "
                    "nothing about what it is for."
                )
            if side == "request":
                for field, described in fields.items():
                    assert described["presence"] in PRESENCE_OF_A_REQUEST_FIELD, (
                        f"the request field {field!r} of {operation!r} is "
                        f"{described['presence']!r}, which tells a client "
                        f"neither of {PRESENCE_OF_A_REQUEST_FIELD}."
                    )
        assert any(
            described["presence"] == ALWAYS
            for described in shape["response"]["fields"].values()
        ), (
            f"the answer shape of {operation!r} promises no field at all: "
            f"{shape['response']['fields']}. A client needs at least the "
            "status in every answer."
        )


def test_a_request_built_only_from_the_published_shape_is_answered():
    """Given a request carrying each of the fields the published shape
    names, with a value of the kind it names, when it is sent for each
    of the 5 available operations, then each one answers rather than
    refusing the request."""
    shapes = published_operation_shapes()

    for operation, shape in shapes.items():
        answer = ask(_a_request_matching(operation, shape))
        assert answer["status"] == "completed", (
            f"{operation!r} answered {answer['status']!r} to a request "
            f"built out of its own published shape: {answer}. A shape an "
            "agent cannot write a working request from is worse than none."
        )


def test_every_field_an_answer_carries_is_one_the_shape_publishes():
    """Given 4 requests per operation, when each is answered, then every
    field of the answer is published, every field published as 'always'
    is there, and every field published as 'when completed' is there for
    exactly the completed answers."""
    shapes = published_operation_shapes()
    sources = (A_PROGRAM, "", "(defn", "(defn f (sig ((n Int)) -> Int ! pure) (+ n true))")

    for operation, shape in shapes.items():
        published = shape["response"]["fields"]
        for source in sources:
            request = dict(_a_request_matching(operation, shape))
            if "source" in request:
                request["source"] = source
            answer = ask(request)
            assert set(answer) <= set(published), (
                f"the answer of {operation!r} carries "
                f"{sorted(set(answer) - set(published))}, which the "
                f"manifest does not publish: {sorted(published)}. A field a "
                "client cannot look up tells it nothing."
            )
            for field, described in published.items():
                if described["presence"] == ALWAYS:
                    assert field in answer, (
                        f"the answer of {operation!r} carries no {field!r} "
                        "and the manifest promises it in every answer: "
                        f"{answer}."
                    )
                elif described["presence"] == WHEN_COMPLETED:
                    assert (field in answer) == (answer["status"] == "completed"), (
                        f"the answer of {operation!r} has status "
                        f"{answer['status']!r} and "
                        f"{'carries' if field in answer else 'carries no'} "
                        f"{field!r}, while the manifest publishes it as "
                        f"{WHEN_COMPLETED!r}."
                    )
