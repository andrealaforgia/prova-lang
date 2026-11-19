"""Laws the answer about a machine descriptor obeys for any descriptor,
not only the ones F25's acceptance tests send.

LAW1 what a role resolves to is decided by the shape of the function it
     names and by nothing else: renaming a role's function everywhere in
     the program and in the descriptor leaves the descriptor accepted,
     with the new name reported for that role.
LAW2 a part of the descriptor that does not resolve is always named: for
     any one of the eight parts, a descriptor naming something absent or
     of another shape is refused, and a refusal carries that part's name.
LAW3 an answer about a machine claims the resolution of the roles and
     nothing further: no text of any answer says a machine was verified,
     proved or built, and a refused descriptor carries neither a claim
     nor a result.
LAW4 what an answer carries is published before it is answered: every
     role it reports, every refusal category it carries and the status it
     answers are read from the manifest.

Drives the `prova` command over its JSON stdin/stdout surface, as the
other property tests here do. No imports from src/prova. The manifest is
read once per process: it is a constant of the shipped tool.

Derandomised with a bounded example count, so the verdict does not
depend on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

import copy
import json
import pathlib
import re
import subprocess

from hypothesis import assume, given, settings
from hypothesis import strategies as st

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"

THE_SCHEMA_VERSION = "machine-descriptor/1"
THE_TYPE_ROLES = ("state", "event", "outcome")
THE_FUNCTION_ROLES = ("init", "step", "admissible", "invariant", "state-of")
THE_ROLES = THE_TYPE_ROLES + THE_FUNCTION_ROLES

# Spoken of a machine, these words would claim something this operation
# does not establish: it confirms that the roles resolve to checked
# functions of the right shapes, and says nothing about the machine's
# behaviour over its runs.
A_CLAIM_THIS_OPERATION_DOES_NOT_MAKE = re.compile(
    r"\b(verifie[sd]|verification|prove[nd]?|proves|proof|built)\b", re.IGNORECASE
)

# A name no program in this repository declares, and a type name none
# declares either.
NOTHING_DECLARES_THIS = "no-such-function"
NOTHING_DECLARES_THIS_TYPE = "NoSuchType"

# Read off the hour clock's machine program: for each role, a name it
# does declare whose arguments or result are not the ones the role needs.
OF_ANOTHER_SHAPE = {
    "init": "valid-state",
    "step": "state-of",
    "state-of": "initial",
    "admissible": "step",
    "invariant": "state-of",
}

# The names the hour clock's machine program declares, and the words
# core-0 keeps for itself: a generated name must be neither.
NAMES_THE_CLOCK_DECLARES = frozenset(
    {"valid-state", "initial", "step", "state-of", "admissible"}
)
WORDS_CORE_0_KEEPS = frozenset(
    {
        "deftype", "record", "union", "defn", "sig", "pure", "requires",
        "ensures", "examples", "example", "true", "false", "let", "if",
        "match", "and", "or", "not", "result",
    }
)

A_FRESH_NAME = st.from_regex(r"[a-z][a-z0-9]{2,8}", fullmatch=True)


def _source() -> str:
    return (EXAMPLES / "hour-clock.machine.prova").read_text(encoding="utf-8")


def _descriptor() -> dict:
    return json.loads((EXAMPLES / "hour-clock.machine.json").read_text(encoding="utf-8"))


def _run(request: dict) -> dict:
    proc = subprocess.run(
        ["prova"], input=json.dumps(request), capture_output=True, text=True, timeout=20.0
    )
    assert proc.returncode == 0, f"the tool exited {proc.returncode}: {proc.stderr!r}"
    return json.loads(proc.stdout)


def _ask(source: str, descriptor: object) -> dict:
    return _run({"operation": "machine", "source": source, "descriptor": descriptor})


def _group_of(role: str) -> str:
    return "types" if role in THE_TYPE_ROLES else "roles"


def _naming(descriptor: dict, role: str, named: str) -> dict:
    changed = copy.deepcopy(descriptor)
    changed[_group_of(role)][role] = named
    return changed


def _rename_everywhere(source: str, old: str, new: str) -> str:
    """`source` with every mention of the function name `old` written as
    `new`, counting a name by the characters core-0 writes one with."""
    return re.sub(rf"(?<![a-z0-9-]){re.escape(old)}(?![a-z0-9-])", new, source)


def _texts_in(value) -> list[str]:
    found: list[str] = []

    def walk(node):
        if isinstance(node, str):
            found.append(node)
        elif isinstance(node, dict):
            for key, child in node.items():
                found.append(key)
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(value)
    return found


def _the_manifest() -> dict:
    """What the tool publishes, read once per process: it is a constant of
    the shipped tool, and each case then sends its own request."""
    if not _PUBLISHED:
        _PUBLISHED.append(_run({"operation": "discover"}).get("result") or {})
    return _PUBLISHED[0]


_PUBLISHED: list[dict] = []


@given(role=st.sampled_from(THE_FUNCTION_ROLES), fresh=A_FRESH_NAME)
@settings(max_examples=10, deadline=None, derandomize=True)
def test_renaming_a_roles_function_everywhere_keeps_the_descriptor_accepted(role, fresh):
    """LAW1 -- a role is resolved by the shape of the function it names,
    not by the name itself."""
    assume(fresh not in NAMES_THE_CLOCK_DECLARES and fresh not in WORDS_CORE_0_KEEPS)
    descriptor = _descriptor()
    was_called = descriptor["roles"][role]
    renamed = _rename_everywhere(_source(), was_called, fresh)

    answer = _ask(renamed, _naming(descriptor, role, fresh))

    assert answer.get("status") == "completed", (
        f"WHAT: the hour clock with {was_called!r} renamed to {fresh!r} "
        f"everywhere was answered {answer.get('status')!r}: {answer}. "
        "WHY: a role resolves by the shape of the function it names; a name "
        "the Owner chose differently is the same machine. "
        "HOW: resolve the name the descriptor gives the role."
    )
    reported = ((answer.get("result") or {}).get("roles") or {}).get(role) or {}
    assert reported.get("named") == fresh, (
        f"WHAT: the answer reports {reported!r} for the {role!r} role, and "
        f"the descriptor names {fresh!r}. "
        "WHY: the Owner reads the answer against the descriptor written. "
        "HOW: report the name the descriptor gave the role."
    )


@given(
    role=st.sampled_from(THE_ROLES),
    how=st.sampled_from(("absent", "another-shape")),
)
@settings(max_examples=16, deadline=None, derandomize=True)
def test_a_part_of_the_descriptor_that_does_not_resolve_is_named(role, how):
    """LAW2 -- whichever of the eight parts does not resolve, a refusal
    carries its name."""
    descriptor = _descriptor()
    if role in THE_TYPE_ROLES:
        named = NOTHING_DECLARES_THIS_TYPE if how == "absent" else "Int"
    else:
        named = NOTHING_DECLARES_THIS if how == "absent" else OF_ANOTHER_SHAPE[role]

    answer = _ask(_source(), _naming(descriptor, role, named))

    assert answer.get("status") != "completed", (
        f"WHAT: a descriptor whose {role!r} part names {named!r} was "
        f"accepted: {answer}. "
        "WHY: a part that names something absent, or something of another "
        "shape, resolves to nothing. HOW: resolve it against the program."
    )
    named_roles = [d.get("role") for d in (answer.get("diagnostics") or [])]
    assert role in named_roles, (
        f"WHAT: the refusal names {named_roles}, not {role!r}: {answer}. "
        "WHY: the Owner must be sent to the part of the descriptor to "
        "repair. HOW: carry the part's name in the refusal."
    )


@given(
    role=st.sampled_from(THE_ROLES),
    how=st.sampled_from(("as-shipped", "absent", "another-shape")),
)
@settings(max_examples=12, deadline=None, derandomize=True)
def test_no_answer_about_a_machine_claims_more_than_the_roles_resolving(role, how):
    """LAW3 -- an answer about a machine claims the resolution of the
    roles and nothing further."""
    descriptor = _descriptor()
    if how == "absent":
        descriptor = _naming(
            descriptor,
            role,
            NOTHING_DECLARES_THIS_TYPE if role in THE_TYPE_ROLES else NOTHING_DECLARES_THIS,
        )
    elif how == "another-shape":
        descriptor = _naming(
            descriptor, role, "Int" if role in THE_TYPE_ROLES else OF_ANOTHER_SHAPE[role]
        )

    answer = _ask(_source(), descriptor)

    assert answer.get("status") == ("completed" if how == "as-shipped" else "invalid_input"), (
        f"WHAT: the descriptor with its {role!r} part {how} was answered "
        f"{answer.get('status')!r}: {answer}. "
        "WHY: the tool answers about a descriptor it is handed: 'completed' "
        "where every part resolves, and 'invalid_input' where a part names "
        "something the program does not declare. "
        "HOW: read the answer above."
    )
    overclaimed = [
        text
        for text in _texts_in(answer)
        if A_CLAIM_THIS_OPERATION_DOES_NOT_MAKE.search(text)
    ]
    assert overclaimed == [], (
        f"WHAT: the answer carries {overclaimed}. "
        "WHY: this operation confirms that the roles resolve to checked "
        "functions of the right shapes; it establishes nothing about the "
        "machine over its runs, and a caller refuses an answer whose text "
        "claims it did. HOW: write the answer in the words of resolution."
    )
    if answer.get("status") == "completed":
        assert (answer.get("claim") or {}).get("scope") == "this input", (
            f"WHAT: the accepted answer claims {answer.get('claim')!r}. "
            "WHY: the answer is about the one program and descriptor it was "
            "sent. HOW: say so in the claim."
        )
        assert (answer.get("result") or {}).get("schema") == THE_SCHEMA_VERSION
    else:
        assert answer.get("result") is None and answer.get("claim") is None, (
            f"WHAT: a refused descriptor carries a claim or a result: {answer}. "
            "WHY: nothing was confirmed, so there is nothing to claim. "
            "HOW: answer the refusals alone."
        )


@given(
    role=st.sampled_from(THE_ROLES),
    how=st.sampled_from(("as-shipped", "absent", "a-number")),
)
@settings(max_examples=12, deadline=None, derandomize=True)
def test_every_part_of_an_answer_about_a_machine_is_published_first(role, how):
    """LAW4 -- every role an answer reports, every refusal category it
    carries and the status it answers are published by the manifest."""
    descriptor = _descriptor()
    if how == "absent":
        descriptor = _naming(
            descriptor,
            role,
            NOTHING_DECLARES_THIS_TYPE if role in THE_TYPE_ROLES else NOTHING_DECLARES_THIS,
        )
    elif how == "a-number":
        descriptor = _naming(descriptor, role, 12)

    answer = _ask(_source(), descriptor)

    published_roles = set(
        ((_the_manifest().get("machine_descriptor_schema") or {}).get("roles") or {})
    )
    assert len(published_roles) == len(THE_ROLES), (
        f"WHAT: the manifest publishes the roles {sorted(published_roles)}, "
        f"not the {len(THE_ROLES)} parts a descriptor names. "
        "WHY: a manifest publishing nothing would agree with every answer "
        "and say nothing at all. HOW: publish every part of the descriptor."
    )
    reported = set(((answer.get("result") or {}).get("roles") or {}))
    if how == "as-shipped":
        assert reported == published_roles, (
            f"WHAT: the answer reports {sorted(reported)} and the manifest "
            f"publishes {sorted(published_roles)}. "
            "WHY: a published role no answer carries is a promise nothing "
            "checks. HOW: publish and report from the one table."
        )
    assert reported <= published_roles, (
        f"WHAT: the answer reports the roles {sorted(reported - published_roles)}, "
        "which the manifest does not publish. "
        "WHY: a role an agent meets but cannot look up is an undocumented "
        "API. HOW: publish and report from the one table."
    )
    published_categories = set(_the_manifest().get("diagnostic_categories") or [])
    answered = {d.get("category") for d in (answer.get("diagnostics") or [])}
    assert answered <= published_categories, (
        f"WHAT: the answer carries the categories "
        f"{sorted(answered - published_categories)}, which the manifest does "
        "not publish. WHY: a category an agent cannot look up is an "
        "undocumented API. HOW: publish every category."
    )
    assert answer.get("status") in set(_the_manifest().get("statuses") or {}), (
        f"WHAT: the answer carries the status {answer.get('status')!r}, which "
        f"the manifest does not list: {sorted(_the_manifest().get('statuses') or {})}. "
        "WHY: a caller reads the statuses from the tool. "
        "HOW: answer one of them."
    )
