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


def _outside_the_one_reader(module: ast.Module) -> list[ast.AST]:
    """Every node of the module that does not stand inside the one
    object allowed to read a submitted request."""
    inside = set()
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == THE_ONE_READER:
            inside.update(id(within) for within in ast.walk(node))
    return [node for node in ast.walk(module) if id(node) not in inside]


def _handed_in(step: ast.AST) -> set[str]:
    """The names a step was handed: everything in its parameter list.

    What a step builds for itself is its own, and reaching into that is
    not the act this law is about; what it was handed came from outside
    and may hold anything.
    """
    arguments = step.args
    given = list(arguments.posonlyargs) + list(arguments.args) + list(arguments.kwonlyargs)
    for extra in (arguments.vararg, arguments.kwarg):
        if extra is not None:
            given.append(extra)
    return {argument.arg for argument in given}


def _looked_up_by_bare_name(module: ast.Module) -> list[tuple[int, str, str]]:
    """Every place a step reaches into something it was handed, by
    `get` or by naming the key, outside the one object allowed to do it.

    Both spellings are the same act, and the one by key is the worse of
    the two: it raises rather than answering when the field is not
    there, which is how a client's bad request became a broken tool.
    """
    found = []
    for step in _outside_the_one_reader(module):
        if not isinstance(step, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        given = _handed_in(step)
        for node in ast.walk(step):
            if isinstance(node, ast.Call):
                called = node.func
                if (
                    isinstance(called, ast.Attribute)
                    and called.attr == "get"
                    and isinstance(called.value, ast.Name)
                    and called.value.id in given
                ):
                    found.append((node.lineno, called.value.id, "get"))
            elif (
                isinstance(node, ast.Subscript)
                and isinstance(node.value, ast.Name)
                and node.value.id in given
                and isinstance(node.ctx, ast.Load)
                and _names_a_field(node.slice)
            ):
                found.append((node.lineno, node.value.id, "by key"))
    return found


def _names_a_field(key: ast.AST) -> bool:
    """Whether a subscript names a field rather than counts a place.

    A step that takes the first of a list it was handed is reading a
    sequence, not reaching into a mapping for a field nobody checked.
    Only a written-out name is the act this law is about.
    """
    return isinstance(key, ast.Constant) and isinstance(key.value, str)


def test_no_step_of_the_service_pulls_a_field_out_of_a_bare_mapping():
    """Given the whole service module, when every place that reads a
    value out of a mapping by name is collected, then there is none: the
    only object allowed to do it reaches the request through itself.
    """
    module = ast.parse(SERVICE.read_text(encoding="utf-8"))

    found = _looked_up_by_bare_name(module)

    assert not found, (
        f"{len(found)} place(s) in {SERVICE.name} pull a value out of a bare "
        f"name, by 'get' or by naming the key: {found}. A field read where it "
        "is used is a field nobody checked, and a value of the wrong kind then "
        f"decides what happens by raising. Read it through {THE_ONE_READER}, "
        "which answers with the value or with the refusal naming the field."
    )


def test_the_check_sees_a_field_read_by_its_key_and_not_only_by_get():
    """Given a step written into the service module that reaches into
    what it was handed by naming the key, when the module is checked,
    then that step is found: the two spellings of the same act are both
    the act.

    Without this, a step could read a field by key and the check above
    would report the module clean.
    """
    sneaked = SERVICE.read_text(encoding="utf-8") + (
        "\n\ndef _sneaky(submitted):\n    return submitted['source']\n"
    )

    found = _looked_up_by_bare_name(ast.parse(sneaked))

    assert [(name, how) for _, name, how in found] == [("submitted", "by key")], (
        f"a step reading a field by its key was not found: {found}. The check "
        "above would then call the module clean while a field went unread by "
        "the one reader, which is the defect it exists to catch."
    )


def test_a_step_taking_the_first_of_a_list_it_was_handed_is_left_alone():
    """Given a step written into the service module that takes the
    first of a list it was handed, when the module is checked, then it
    is not reported: counting a place in a sequence is not reaching
    into a mapping for a field nobody checked.

    Without this control the law would grow until it forbade ordinary
    code, and the next person would answer it by weakening the law
    rather than by repairing what it catches.
    """
    ordinary = SERVICE.read_text(encoding="utf-8") + (
        "\n\ndef _first_defect(defects):\n    return defects[0]\n"
    )

    found = _looked_up_by_bare_name(ast.parse(ordinary))

    assert found == [], (
        f"taking the first of a list was reported as reading an unchecked "
        f"field: {found}. The law is about a field named in a mapping; a step "
        "that counts a place in a sequence it was handed is doing something "
        "else, and flagging it would push the next person to weaken the law."
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
