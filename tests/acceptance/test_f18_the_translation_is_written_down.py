"""F18.6 -- the change ships the document that says what the tool writes
for the solver and why an obligation settled there is the claim the
source makes.

SPEC.md lines 263-266: the encoder must specify every emitted logical
primitive's meaning, and the implementation must document its translation
and justify that a discharged obligation establishes the corresponding
source claim.

The document is found the way a reader finds it: the manifest says where
it is. Every primitive the tool says it writes must have its own entry
there, so a primitive added later without a word about its meaning is
caught here rather than by a reader who meets it in an answer.

Drives the `prova` command's real JSON stdin/stdout surface and reads the
shipped document the manifest points at. No imports from src/prova.

still passes if: the document existed and said nothing about the
primitives. The last test requires one entry per primitive the tool
publishes, and the first requires that published list not to be empty.
"""

from __future__ import annotations

import re

from _f18_fixtures import REPO_ROOT, the_manifest

# How the document writes the entry for one primitive: a list item
# opening with the primitive's own name in backticks. One line per
# primitive, so a reader looking one up finds it where its name stands.
ENTRY = re.compile(r"^- `([^`]+)`", re.MULTILINE)


def _encoding() -> dict:
    return ((the_manifest().get("result") or {}).get("encoding")) or {}


def _document_text() -> str:
    where = _encoding().get("documented_in")
    assert isinstance(where, str) and where, (
        f"WHAT: the manifest says {where!r} about where the translation is "
        "written down. "
        "WHY: a reader asked to trust a proved obligation has to be able to "
        "find what was written for the solver and why it settles the claim "
        "the source makes. "
        f"HOW: publish the path of the document: {_encoding()}"
    )
    path = REPO_ROOT.joinpath(*where.split("/"))
    assert path.is_file(), (
        f"WHAT: the manifest points at {where!r} and this repository ships no "
        "such file. "
        "WHY: a reader following the answer would find nothing. "
        f"HOW: ship the document at {where!r}, or publish where it really is."
    )
    return path.read_text(encoding="utf-8")


def test_the_tool_publishes_the_primitives_it_writes_for_the_solver():
    """Given the manifest, when the Owner reads what the tool writes for
    the solver, then it names the translation's own version and every
    logical primitive that translation emits."""
    encoding = _encoding()

    assert any(character.isdigit() for character in str(encoding.get("version"))), (
        f"WHAT: the manifest says {encoding.get('version')!r} about the "
        "version of the translation. "
        "WHY: two answers written by two translations would read the same, "
        "and evidence kept from one would be read as evidence from the other. "
        f"HOW: name the version: {encoding}"
    )
    primitives = encoding.get("primitives") or {}
    assert len(primitives) >= 5, (
        f"WHAT: the manifest publishes {sorted(primitives)} as the primitives "
        "written for the solver. "
        "WHY: the two shipped examples alone need whole numbers, their order, "
        "equality, the connectives and the shapes of their records, so a list "
        "shorter than that is one that does not say what the tool writes. "
        f"HOW: publish one entry per primitive: {encoding}"
    )
    unexplained = sorted(
        name for name, meaning in primitives.items() if not str(meaning).strip()
    )
    assert not unexplained, (
        f"WHAT: {unexplained} are published with nothing said about what they "
        "mean. "
        "WHY: SPEC.md asks the encoder to specify every emitted logical "
        "primitive's meaning; a name alone specifies none. "
        f"HOW: say what each one means: {encoding}"
    )


def test_the_shipped_document_explains_every_primitive_the_tool_writes():
    """Given the document the manifest points at, when the Owner reads
    it, then it has an entry for every primitive the tool publishes."""
    published = set((_encoding().get("primitives") or {}))
    explained = set(ENTRY.findall(_document_text()))

    missing = sorted(published - explained)
    assert not missing, (
        f"WHAT: the document explains {sorted(explained)} and the tool writes "
        f"{sorted(published)}; {missing} are written for the solver and "
        "explained nowhere. "
        "WHY: a reader meeting one of them in an answer would have to guess "
        "what the tool meant by it. "
        "HOW: add a line opening with the primitive's name in backticks, "
        "beside the others."
    )
