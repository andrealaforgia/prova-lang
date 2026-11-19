"""F11.B4 -- the published request shape is the one the tool keeps: a
request that matches it is answered, and one that carries a published
field as a value of another kind is refused as invalid input, by name.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the tool refused everything. The first test sends the
matching request for every available operation and reads a real answer
back, so a tool that refused a request it published the shape of fails
too.
"""

from __future__ import annotations

from _f11_manifest_fixtures import (
    a_value_matching,
    A_PROGRAM,
    a_program_for,
    ask,
    published_operation_shapes,
    wrong_kind_for,
)

A_REFUSED_REQUEST = "invalid_input"
THE_CATEGORY_A_MISREAD_FIELD_CARRIES = "malformed_request"


def _matching_request(operation: str, shape: dict) -> dict:
    request = {"operation": operation}
    for field, described in shape["request"]["fields"].items():
        request[field] = a_value_matching(operation, field, described)
    return request


def test_an_operation_advertised_as_available_answers_a_matching_request():
    """Given the published shape of each available operation, when a
    request carrying exactly those fields is sent, then the operation
    answers it and never calls it invalid input."""
    for operation, shape in published_operation_shapes().items():
        answer = ask(_matching_request(operation, shape))

        assert answer["status"] == "completed", (
            f"{operation!r} answered {answer['status']!r} to the request its "
            f"own published shape describes: {answer}. An operation "
            "advertised as available answers the requests it publishes."
        )


def test_a_published_field_sent_as_another_kind_of_value_is_refused_by_name():
    """Given the published shape of `evaluate`, whose 'function' field
    is a text, when a request sends 7 there instead, then the answer is
    'invalid_input' and the refusal names the field."""
    shapes = published_operation_shapes()

    for operation, shape in shapes.items():
        fields = shape["request"]["fields"]
        for field, described in fields.items():
            request = _matching_request(operation, shape)
            request[field] = wrong_kind_for(described["kind"])
            answer = ask(request)

            assert answer["status"] == A_REFUSED_REQUEST, (
                f"{operation!r} answered {answer['status']!r} to a request "
                f"whose {field!r} carries {request[field]!r}, and its "
                f"published shape names that field a {described['kind']!r}: "
                f"{answer}. A shape the tool does not keep is a shape an "
                "agent cannot rely on."
            )
            categories = [d.get("category") for d in answer.get("diagnostics", [])]
            assert THE_CATEGORY_A_MISREAD_FIELD_CARRIES in categories, (
                f"the refusal of {operation!r} for the field {field!r} "
                f"carries {categories}, and a field of the request the tool "
                f"could not read is {THE_CATEGORY_A_MISREAD_FIELD_CARRIES!r}."
            )
            named = " ".join(
                str(d.get("symbol", "")) for d in answer.get("diagnostics", [])
            )
            assert field in named, (
                f"the refusal names {named!r} and the field at fault is "
                f"{field!r}: a client repairing its request has to be told "
                "which field to look at."
            )
