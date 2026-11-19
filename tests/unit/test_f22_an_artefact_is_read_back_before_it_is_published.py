"""The text of an artefact is read by the interpreter it is written for
before anything is published.

A file that cannot be read is not an artefact: it would be published,
kept, and fail the first time the Owner ran it. No program this tool
accepts can reach this refusal -- a module nests one block per match,
the interpreter reads 100 blocks, and a text nesting the 200 forms that
would take is already refused by the reader at 128 -- so the guard is
exercised here, where a text can be handed to it directly.
"""

from __future__ import annotations

from prova import building, checker


def _a_record_of_one_build() -> dict:
    return {
        "artefact_format": building.ARTEFACT_FORMAT,
        "source_revision": "0" * 64,
        "entry": "step",
        "configuration": {},
        "evidence_digest": "1" * 64,
    }


def test_a_text_the_interpreter_cannot_read_is_refused_with_its_depth():
    """Given generated text the interpreter cannot read -- 120 blocks
    standing inside one another, which is past what it compiles -- when
    an artefact is asked for it, then the answer is the refusal, it names
    the depth the text reached, and no artefact is built."""
    written = ["def _deep():"]
    for depth in range(1, 121):
        written.append(("    " * depth) + f"if {depth}:")
    written.append(("    " * 121) + "return 1")

    refused = building.Artefact._read_back(
        "\n".join(written) + "\n", _a_record_of_one_build()
    )

    assert isinstance(refused, building.Unwritable), (
        f"WHAT: text the interpreter cannot read became {type(refused).__name__}. "
        "WHY: an artefact is a module that can be run; publishing text that "
        "cannot be read gives the Owner a file that fails when they use it. "
        f"HOW: inspect what was returned: {refused}"
    )
    assert refused.category == checker.GENERATED_NESTING_EXCEEDED, refused
    assert "121" in refused.reason, (
        f"WHAT: the refusal does not name the depth the text reached: "
        f"{refused.reason!r}. "
        "WHY: the Owner has to know what to shorten. "
        "HOW: count the blocks of the deepest line and name the number."
    )
    assert "Nothing was written" in refused.reason, refused.reason


def test_a_text_the_interpreter_reads_becomes_an_artefact():
    """Given generated text the interpreter reads, when an artefact is
    asked for it, then the artefact carries that text and the record of
    the build -- so the refusal above is about the text and not about
    every text."""
    text = "ARTEFACT = {}\n\n\ndef main(argv):\n    return 0\n"

    artefact = building.Artefact._read_back(text, _a_record_of_one_build())

    assert isinstance(artefact, building.Artefact), artefact
    assert artefact.text == text
    assert artefact.recorded["entry"] == "step"
