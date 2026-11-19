"""Every status and category word a built artefact answers with is
published before anyone holds one: by `discover`, by the artefact's own
header, and by the artefact as data.

SPEC.md asks agents to discover signatures and bindings without guessing
an undocumented API, and asks diagnostics to carry a stable category. A
caller who must branch on the exit status of an artefact cannot read
that status out of prose; a word and a number that nothing publishes are
a word and a number with no meaning.

Drives only the `prova` command's real JSON stdin/stdout surface, the
artefact it writes, and that artefact read as a module. No imports from
src/prova.
"""

from __future__ import annotations

import pathlib
import tempfile

import pytest

from _f22_fixtures import run_artefact
from _f23_fixtures import (
    THE_REFUSALS,
    an_artefact_of,
    first_line_word,
    read_as_data,
    reservation_source,
    the_published_table,
)


@pytest.fixture(scope="module")
def the_built_component():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield an_artefact_of(
            reservation_source(), "step", pathlib.Path(tmp_dir)
        )


def test_the_manifest_publishes_every_status_an_artefact_answers_with():
    """Given a client that has sent no request of its own, when it asks
    what this tool offers, then the manifest publishes one entry per
    category word a built artefact can answer with, each carrying the
    exit status of that word and what it means.

    still passes if: the manifest had published the words with no exit
    statuses -- the status of every word is read and compared, and a
    word published for a status it does not carry fails here.
    """
    published = the_published_table()
    assert set(published) == {word for word, _, _ in THE_REFUSALS}, (
        f"WHAT: the manifest publishes the artefact words {sorted(published)} "
        f"and an artefact answers with "
        f"{sorted(word for word, _, _ in THE_REFUSALS)}. "
        "WHY: a caller branches on the status an artefact exits with and "
        "reads its meaning from the tool; an unpublished word cannot be "
        "looked up, and a published word that never happens is a promise of "
        "something that does not exist. "
        f"HOW: publish the table in manifest.py: {published}"
    )
    for word, status, _ in THE_REFUSALS:
        entry = published[word]
        assert entry.get("exit_status") == status, (
            f"WHAT: the manifest publishes {word!r} with the exit status "
            f"{entry.get('exit_status')!r} and an artefact exits {status} "
            "for it. "
            "WHY: the number a caller branches on is the number the tool "
            "publishes, or the two disagree about what happened. "
            f"HOW: publish one table and read the artefact's behaviour from "
            f"it: {entry}"
        )
        assert len(str(entry.get("meaning") or "")) > 20, (
            f"WHAT: the manifest says {entry.get('meaning')!r} about "
            f"{word!r}. "
            "WHY: an agent reads what a status means before it sends a "
            "request, not after a run surprises it. "
            f"HOW: say what the status is about: {entry}"
        )


def test_the_artefact_carries_the_same_table_as_data_and_in_its_header(
    the_built_component,
):
    """Given one built artefact, when it is read as a module, then the
    table of words and statuses it carries as data is the table the
    tool publishes, and its header documents each word beside its own
    status.

    still passes if: the header had named every word with a number that
    is not its own -- the pairs are read out of the header and compared
    as pairs, so a header documenting the status 12 for MALFORMED fails
    here rather than passing because '2' stands inside '12'.
    """
    carried = read_as_data(the_built_component, "m['REFUSALS']")
    assert carried == {
        word: status for word, status, _ in THE_REFUSALS
    }, (
        f"WHAT: the artefact carries {carried} as its table of refusals and "
        f"the tool publishes {[(w, s) for w, s, _ in THE_REFUSALS]}. "
        "WHY: the Owner holding an artefact reads what its statuses mean "
        "from the file itself, where neither the compiler nor the manifest "
        "is installed; the two cannot disagree. "
        f"HOW: write the artefact's table from the one the tool publishes."
    )

    header = read_as_data(the_built_component, "m['__doc__']") or ""
    documented = {}
    for line in header.splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[0].isdigit() and ":" in parts[1]:
            documented[parts[1].split(":", 1)[0].strip()] = int(parts[0])
    assert documented == {
        word: status for word, status, _ in THE_REFUSALS
    }, (
        f"WHAT: the artefact's header documents {documented} and an artefact "
        f"answers with {[(w, s) for w, s, _ in THE_REFUSALS]}. "
        "WHY: a reader opening the file must find each status it can exit "
        "with beside the word that status carries, and the pair must be the "
        "pair: a header naming the right words with other numbers is worse "
        "than none, because it is believed. "
        "HOW: write the table into the header the build generates."
    )


def test_every_word_an_artefact_actually_answers_with_is_published(
    the_built_component,
):
    """Given the built reservation component, when it is run over three
    inputs it refuses for three different reasons, then the word each
    refusal opens with is one the manifest publishes and the status it
    exits with is the one published for that word.

    still passes if: the table had been published with no behaviour
    behind it -- these three runs are real refusals of a real artefact.
    """
    published = the_published_table()
    observed = {}
    for arguments in (
        ["(Reserv", "(Reserve)"],
        ["(Reserve)", "(Reserve)"],
        ["(Reservation 9)", "(Reserve)"],
    ):
        ran = run_artefact(the_built_component, arguments)
        word = first_line_word(ran)
        observed[word] = ran.returncode
        assert word in published, (
            f"WHAT: the refusal of {arguments} opens with {word!r}, which "
            f"the manifest does not publish: {sorted(published)}. "
            "WHY: a client reads the vocabulary of every refusal from the "
            "tool; a word nothing declares cannot be read. "
            f"HOW: publish it beside the others: {ran.stderr[:200]!r}"
        )
        assert published[word].get("exit_status") == ran.returncode, (
            f"WHAT: {arguments} was refused with the word {word!r} and the "
            f"status {ran.returncode}, and the manifest publishes "
            f"{published[word].get('exit_status')!r} for that word. "
            "WHY: the published table is what a caller branches on. "
            f"HOW: write the artefact's statuses from the published table."
        )

    assert len(observed) == 3, (
        f"WHAT: the three refusals carried {observed}, which is "
        f"{len(observed)} distinct words and not 3. "
        "WHY: unreadable text, a value of the wrong type and a state outside "
        "the precondition are three different repairs. "
        "HOW: give each kind its own word."
    )
