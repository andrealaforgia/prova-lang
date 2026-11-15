"""F18.5 -- the answer names the solver and the translation behind it,
and says plainly that the solver's word is taken and not checked again.

SPEC.md lines 302-305: the initial implementation may trust a selected
solver's validity result, disclosing that trust. A reader who is not told
would take a proved obligation for one this tool established itself, and
would not know that a defect in the solver reaches them.

What `discover` publishes about the verify answer must name every field
that answer carries, so the disclosure is something a client can look up
before it ever sends a request, and not something it has to find by
reading an answer.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool wrote any sentence at all beside the result.
The disclosure is read here as the three facts a reader acts on -- what
was trusted, which solver, and whether this tool checked the result again
-- and the solver named must be the one the answer says it stands on.
"""

from __future__ import annotations

from _f18_fixtures import completed, the_manifest, verify

A_PROGRAM = """(defn twice
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (ensures (= result (* n 2)))
  (examples (example (twice 2) => 4))
  (* n 2))
"""
LABEL = "a program whose promise a solver settles"
DOES_NOT_APPLY = "not applicable:"


def _versions() -> dict:
    return (completed(verify(A_PROGRAM), LABEL).get("stands_on") or {}).get(
        "versions"
    ) or {}


def test_the_answer_names_the_solver_and_the_translation_it_used():
    """Given a program a solver settles, when the Owner reads what the
    answer stands on, then the solver and the translation each name
    themselves with a version, and neither says it does not apply."""
    named = _versions()

    for behind in ("solver", "encoding"):
        said = named.get(behind, "")
        assert not said.startswith(DOES_NOT_APPLY), (
            f"WHAT: the answer says the {behind} does not apply: {said!r}. "
            "WHY: a solver was asked and a translation was written for it, so "
            "a reader told there is none cannot reproduce this answer or tell "
            "which versions produced it. "
            f"HOW: name it with its version: {named}"
        )
        assert any(character.isdigit() for character in said), (
            f"WHAT: the answer says {said!r} about the {behind} and no digit "
            "stands in it. "
            "WHY: two answers from two versions would read the same, and a "
            "defect fixed between them could not be told from one that was "
            "not. "
            f"HOW: name the version: {named}"
        )

    assert "z3" in named["solver"].lower(), (
        f"WHAT: the answer says {named['solver']!r} about the solver and does "
        "not name it. "
        "WHY: the Owner has to know which solver's word stands behind a "
        "proved obligation to judge what that word is worth. "
        f"HOW: name the solver beside its version: {named}"
    )


def test_the_answer_says_the_solver_is_trusted_and_not_checked_again():
    """Given the same program, when the Owner reads the answer, then it
    says what was trusted, names the same solver it stands on, and says
    this tool did not check that result again."""
    answer = completed(verify(A_PROGRAM), LABEL)
    disclosed = (answer.get("result") or {}).get("trust") or {}

    assert disclosed.get("trusted_from") == "solver", (
        f"WHAT: the answer discloses {disclosed} about what it trusts. "
        "WHY: SPEC.md lines 302-305 allow this tool to trust a solver's "
        "validity result only while it discloses that trust; a reader not "
        "told takes a proved obligation for one this tool established. "
        f"HOW: inspect the answer: {answer}"
    )
    assert disclosed.get("rechecked_by_this_tool") is False, (
        f"WHAT: the answer says {disclosed.get('rechecked_by_this_tool')!r} "
        "about checking the solver's result again. "
        "WHY: this tool keeps no proof certificate and runs no checking "
        "kernel, so saying otherwise would claim assurance nobody built. "
        f"HOW: inspect the answer: {answer}"
    )
    assert disclosed.get("solver") == _versions().get("solver"), (
        f"WHAT: the answer trusts {disclosed.get('solver')!r} and stands on "
        f"{_versions().get('solver')!r}. "
        "WHY: two names for one solver leave the reader unable to say which "
        "one was asked. "
        f"HOW: write the one name in both places: {answer}"
    )


def test_the_manifest_names_every_field_the_verify_answer_carries():
    """Given the manifest, when it is read beside a verify answer, then
    every field of that answer is one the manifest describes."""
    published = (
        ((the_manifest().get("result") or {}).get("operation_schemas") or {})
        .get("verify", {})
        .get("response", {})
        .get("fields")
    ) or {}
    carried = set(completed(verify(A_PROGRAM), LABEL))

    assert "trust" in published, (
        f"WHAT: the manifest describes {sorted(published)} as the fields of a "
        "verify answer and names none for the trust it discloses. "
        "WHY: an agent reads what an operation answers before it sends a "
        "request; a disclosure it can only find by reading an answer is one "
        "it cannot plan for. "
        "HOW: describe the field in manifest.py beside the others."
    )
    unpublished = sorted(carried - set(published))
    assert not unpublished, (
        f"WHAT: a verify answer carries {unpublished}, which the manifest "
        f"does not describe; it describes {sorted(published)}. "
        "WHY: an agent reads what an operation answers from the manifest "
        "before it sends a request; a field it cannot look up is one it must "
        "guess at. "
        "HOW: describe the field in manifest.py beside the others."
    )
