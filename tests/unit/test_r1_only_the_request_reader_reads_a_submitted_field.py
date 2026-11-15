"""R1 architectural check: no step of the service reads a field of a
submitted request for itself.

A field read by whichever step happens to reach for it first is a field
nobody checked. Every crash this delivery repairs was one of those. The
law is kept where it can be seen: one object reads a submitted request,
and it is the only thing that pulls a value out of a bare mapping by
name.

The check governs the whole module, not a list of steps, so a step added
later is covered without anyone remembering to add it here.

still passes if: the module were empty. The second test requires the
reader that is allowed to do it to still be there and still be doing it.
"""

from __future__ import annotations

import ast
import pathlib

SERVICE = pathlib.Path(__file__).resolve().parents[2] / "src" / "prova" / "service.py"

# The object that is allowed to read a submitted request, and the field
# it keeps it in. It reaches the mapping through itself, never through a
# bare name, which is what makes the law below checkable at all.
THE_ONE_READER = "Request"


def _looked_up_by_bare_name(module: ast.Module) -> list[tuple[int, str]]:
    """Every place a value is pulled out of a bare name by `get`."""
    found = []
    for node in ast.walk(module):
        if not isinstance(node, ast.Call):
            continue
        called = node.func
        if not isinstance(called, ast.Attribute) or called.attr != "get":
            continue
        if isinstance(called.value, ast.Name):
            found.append((node.lineno, called.value.id))
    return found


def test_no_step_of_the_service_pulls_a_field_out_of_a_bare_mapping():
    """Given the whole service module, when every place that reads a
    value out of a mapping by name is collected, then there is none: the
    only object allowed to do it reaches the request through itself.
    """
    module = ast.parse(SERVICE.read_text(encoding="utf-8"))

    found = _looked_up_by_bare_name(module)

    assert not found, (
        f"{len(found)} place(s) in {SERVICE.name} pull a value out of a bare "
        f"name by 'get': {found}. A field read where it is used is a field "
        f"nobody checked, and a value of the wrong kind then decides what "
        f"happens by raising. Read it through {THE_ONE_READER}, which answers "
        "with the value or with the refusal naming the field."
    )


def test_the_one_reader_of_a_request_is_still_there_and_still_reads_it():
    """Given the service module, when the object allowed to read a
    submitted request is looked for, then it is defined and it does read
    fields out of what it was given, so the check above is a law being
    kept rather than a module with nothing in it.
    """
    module = ast.parse(SERVICE.read_text(encoding="utf-8"))
    readers = [
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == THE_ONE_READER
    ]

    assert len(readers) == 1, (
        f"{SERVICE.name} defines {len(readers)} object(s) named "
        f"{THE_ONE_READER!r}, expected exactly 1. The law above says every "
        "field is read in one place; that place has to exist."
    )
    reads = [
        node
        for node in ast.walk(readers[0])
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
    ]
    assert len(reads) >= 3, (
        f"{THE_ONE_READER} reads {len(reads)} field(s) out of the request it "
        "was given, expected at least 3 (the operation, the source and what "
        "an evaluation asks for). A reader that reads nothing would satisfy "
        "the law above while every step went on reading for itself."
    )
