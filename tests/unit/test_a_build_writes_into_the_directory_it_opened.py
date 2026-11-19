"""A build writes into the directory it was authorised over, even where
the pathname of that directory is made to name another one while the
build runs.

The authority was resolved to a pathname and every later step -- what
stands under the name, the working file, the one step that gives the
name away -- opened that pathname again. A concurrent rename of the
authorised directory, with a link put up under its old name, redirected
all of them: the artefact landed outside the directory the request
authorised, and the answer said `completed`.

The directory is now opened once, when the destination is resolved, and
everything after that is done against the open directory itself. These
tests hook exactly there: between resolving the destination and
publishing the text, which is the window the review's reproduction
raced with a pipe.
"""

from __future__ import annotations

import os
import pathlib


def _building():
    """The unit under test: these are facts about one unit, not about an
    answer of the tool."""
    from prova import building

    return building


THE_NAME = "clock.py"
THE_TEXT = "# the artefact\n"


def _swap(authorised: pathlib.Path, elsewhere: pathlib.Path) -> pathlib.Path:
    """Move the authorised directory aside and put a link to another
    directory up under its old name, which is the race the review
    reproduced."""
    moved = authorised.parent / "moved-aside"
    os.rename(authorised, moved)
    os.symlink(elsewhere, authorised)
    return moved


def test_the_artefact_lands_in_the_directory_that_was_authorised(tmp_path):
    building = _building()
    authorised = tmp_path / "authorised"
    authorised.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    destination = building.AuthorisedDestination.inside(str(authorised), THE_NAME)
    assert not isinstance(destination, building.Unwritable), destination
    moved = _swap(authorised, elsewhere)

    unwritten = destination.publish(THE_TEXT)

    assert unwritten is None, unwritten
    assert (moved / THE_NAME).read_text(encoding="utf-8") == THE_TEXT, sorted(
        p.name for p in moved.iterdir()
    )
    assert sorted(p.name for p in elsewhere.iterdir()) == [], (
        "the build wrote into the directory the pathname was made to name "
        "after the request was authorised"
    )


def test_an_authorised_replacement_replaces_inside_the_same_directory(tmp_path):
    building = _building()
    authorised = tmp_path / "authorised"
    authorised.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (authorised / THE_NAME).write_bytes(b"OLD\n")
    (elsewhere / THE_NAME).write_bytes(b"NOT THIS ONE\n")

    destination = building.AuthorisedDestination.inside(
        str(authorised), THE_NAME, building.Replacement.asked(True)
    )
    assert not isinstance(destination, building.Unwritable), destination
    moved = _swap(authorised, elsewhere)

    unwritten = destination.publish(THE_TEXT)

    assert unwritten is None, unwritten
    assert (moved / THE_NAME).read_text(encoding="utf-8") == THE_TEXT
    assert (elsewhere / THE_NAME).read_bytes() == b"NOT THIS ONE\n", (
        "the authorised replacement replaced a file in another directory"
    )


def test_no_working_file_is_left_in_either_directory(tmp_path):
    building = _building()
    authorised = tmp_path / "authorised"
    authorised.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()

    destination = building.AuthorisedDestination.inside(str(authorised), THE_NAME)
    moved = _swap(authorised, elsewhere)
    destination.publish(THE_TEXT)

    assert sorted(p.name for p in moved.iterdir()) == [THE_NAME], sorted(
        p.name for p in moved.iterdir()
    )
    assert sorted(p.name for p in elsewhere.iterdir()) == []


def test_a_file_that_appears_under_the_name_is_still_not_written_over(tmp_path):
    """The rule the open directory must not lose: where no replacement
    was authorised and something appears under the name after the
    destination was resolved, the build refuses and changes nothing."""
    building = _building()
    authorised = tmp_path / "authorised"
    authorised.mkdir()

    destination = building.AuthorisedDestination.inside(str(authorised), THE_NAME)
    (authorised / THE_NAME).write_bytes(b"APPEARED\n")

    unwritten = destination.publish(THE_TEXT)

    assert unwritten is not None, "the file that appeared was written over"
    assert unwritten.category == "output_file_exists", unwritten
    assert (authorised / THE_NAME).read_bytes() == b"APPEARED\n"
    assert sorted(p.name for p in authorised.iterdir()) == [THE_NAME]
