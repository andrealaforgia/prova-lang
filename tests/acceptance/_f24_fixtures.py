"""Shared helpers for F24: how the Owner names an authorised destination
for a build, and what the files under it look like afterwards.

Not a test module (no `test_` prefix); pytest will not collect it.
Drives only the `prova` command's real JSON stdin/stdout surface and the
files it writes. No imports from src/prova.
"""

from __future__ import annotations

import hashlib
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from _f22_fixtures import ask, hour_clock  # noqa: E402,F401

# The word every answer of a refused request carries, and the words the
# three answers about a destination carry under 'category'.
REFUSED = "invalid_input"
OUTSIDE_AUTHORITY = "output_outside_authority"
NAME_IS_A_LINK = "output_name_is_a_link"
NOT_WRITABLE = "output_not_writable"
FILE_EXISTS = "output_file_exists"

# The start of the name of the file a build writes before it publishes
# anything. A directory holding one of these after an answer was given
# is a build that left its working file behind.
WORKING_FILE = ".prova-build-"

A = "=>"


def build_into(
    directory,
    name,
    *,
    source: str | None = None,
    entry: str = "step",
    replace=None,
    lowered: dict | None = None,
    **extra,
) -> dict:
    """What the Owner is told when they ask for an artefact inside the
    directory they authorise, under the name they choose."""
    request = {
        "operation": "build",
        "source": hour_clock() if source is None else source,
        "entry": entry,
    }
    if directory is not None:
        request["output_directory"] = directory if isinstance(
            directory, (int, float, bool, list, dict)
        ) else str(directory)
    if name is not None:
        request["output_name"] = name if isinstance(
            name, (int, float, bool, list, dict)
        ) else str(name)
    if replace is not None:
        request["replace"] = replace
    request.update(extra)
    return ask(request, lowered=lowered)


def diagnostics_of(answer: dict) -> list:
    return list(answer.get("diagnostics") or [])


def categories_of(answer: dict) -> set:
    return {d.get("category") for d in diagnostics_of(answer)}


def reasons_of(answer: dict) -> str:
    return " ".join(d.get("reason", "") for d in diagnostics_of(answer))


def working_files_under(directory: pathlib.Path) -> list:
    """The working files a build left behind under `directory`."""
    return sorted(
        entry.name
        for entry in pathlib.Path(directory).iterdir()
        if entry.name.startswith(WORKING_FILE)
    )


def entries_under(directory: pathlib.Path) -> list:
    """Every name under `directory`, links included, without following
    any of them."""
    return sorted(entry.name for entry in pathlib.Path(directory).iterdir())


def digest_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def a_program_whose_example_is_wrong() -> str:
    """A program whose one example claims an answer one too large: every
    obligation of it is discharged and the example does not pass, so the
    whole of it was never shown and no artefact of it may be published.
    """
    return (
        "(defn plus-one\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        "  (requires (>= n 0))\n"
        "  (ensures (>= result 0))\n"
        f"  (examples (example (plus-one 1) {A} 3))\n"
        "  (+ n 1))\n"
    )


def says_the_authority_rule(answer: dict, authority) -> str | None:
    """Why this refusal does not name the authority rule, or `None`.

    A refusal about where a build may write says three things: the
    directory the request authorised, that the rule is about staying
    inside it, and that nothing was written. A refusal that says only
    that something went wrong leaves the Owner guessing which of the
    rules they broke.
    """
    reasons = reasons_of(answer)
    if str(authority) not in reasons:
        return f"it does not name the authorised directory {str(authority)!r}"
    if "authorised" not in reasons:
        return "it does not say that the destination is an authorised one"
    if "nothing was written" not in reasons.lower():
        return "it does not say that nothing was written"
    return None
