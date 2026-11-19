"""The value that stands for a place a build is allowed to write.

Nothing in this tool opens a file for writing except through this value,
so what it refuses to be built from is what no build can reach. Each
case here is the same rule the command answers with, read one step
closer to where it is decided: a refusal carries its reason, and an
accepted destination carries the one path it stands for.
"""

from __future__ import annotations

import os


def _building():
    from prova import building

    return building


def test_a_name_that_is_not_a_plain_file_name_is_refused_with_a_reason(tmp_path):
    building = _building()
    authority = str(tmp_path)
    for name in ("../escape.py", "sub/clock.py", "", ".", "..", "clo\x00ck.py"):
        refused = building.AuthorisedDestination.inside(authority, name)
        assert isinstance(refused, building.Unwritable), (
            f"WHAT: the name {name!r} built a destination instead of being "
            "refused. "
            "WHY: a destination that can be built from such a name is a "
            "place a build can write outside the authority. "
            f"HOW: refuse it in the one constructor: got {refused!r}"
        )
        assert len(refused.reason) > 40 and str(authority) in refused.reason, (
            f"WHAT: the refusal of {name!r} reads {refused.reason!r}. "
            "WHY: every refusal names the authorised directory and the rule "
            "it stands on. "
            "HOW: write the rule into the reason."
        )


def test_a_plain_name_inside_the_authority_is_accepted_and_names_its_path(tmp_path):
    building = _building()
    accepted = building.AuthorisedDestination.inside(str(tmp_path), "clock.py")
    assert not isinstance(accepted, building.Unwritable), (
        f"WHAT: a plain name inside an existing directory was refused: "
        f"{accepted!r}. "
        "WHY: this is the case every build goes through. "
        "HOW: accept it."
    )
    assert str(accepted.path) == os.path.join(
        os.path.realpath(str(tmp_path)), "clock.py"
    ), (
        f"WHAT: the destination stands at {accepted.path!r}. "
        "WHY: the path a build writes is the authorised directory as it "
        "really is, with the chosen name inside it. "
        "HOW: join the resolved authority and the name."
    )


def test_a_directory_that_is_not_there_is_refused_with_a_reason(tmp_path):
    building = _building()
    refused = building.AuthorisedDestination.inside(
        str(tmp_path / "not-there"), "clock.py"
    )
    assert isinstance(refused, building.Unwritable), (
        f"WHAT: a directory that is not there built a destination: "
        f"{refused!r}. "
        "WHY: an artefact is written inside a directory that already exists. "
        "HOW: refuse it in the constructor."
    )
    assert "not-there" in refused.reason, (
        f"WHAT: the refusal reads {refused.reason!r}. "
        "WHY: the Owner reads which directory is missing. "
        "HOW: name it."
    )


def test_a_file_that_appears_before_publishing_is_not_written_over(tmp_path):
    """The destination is read, and only then does a file appear under
    the chosen name. Without an authorised replacement the artefact is
    not published over it and the file is byte for byte what it was.
    """
    building = _building()
    destination = building.AuthorisedDestination.inside(str(tmp_path), "clock.py")
    appeared = tmp_path / "clock.py"
    appeared.write_bytes(b"APPEARED\n")

    unwritten = destination.publish("# the artefact\n")

    assert isinstance(unwritten, building.Unwritable), (
        "WHAT: a destination that nothing stood at when it was read "
        "published over the file that appeared there. "
        "WHY: where no replacement was authorised, the name is given to the "
        "new file in a step that fails if anything is already there; a tool "
        "that moves the name onto it, or copies over it, replaces what the "
        "Owner has without being asked. "
        f"HOW: give the name away with a step that refuses: got {unwritten!r}"
    )
    assert appeared.read_bytes() == b"APPEARED\n", (
        f"WHAT: the file that appeared now reads {appeared.read_bytes()!r}. "
        "WHY: an unauthorised replacement changes nothing. "
        "HOW: never write over a name this build did not authorise."
    )
    assert sorted(p.name for p in tmp_path.iterdir()) == ["clock.py"], (
        f"WHAT: the directory holds "
        f"{sorted(p.name for p in tmp_path.iterdir())}. "
        "WHY: the working file is removed whatever happens. "
        "HOW: remove it on every path out."
    )


def test_an_authorised_replacement_takes_the_name_in_one_step(tmp_path):
    """Where the replacement was authorised and an artefact stood there
    when the destination was read, the name is moved onto the new file:
    the artefact that was there is gone and the new text is under the
    name.
    """
    building = _building()
    standing = tmp_path / "clock.py"
    standing.write_bytes(b"OLD\n")
    destination = building.AuthorisedDestination.inside(
        str(tmp_path), "clock.py", building.Replacement.asked(True)
    )
    assert not isinstance(destination, building.Unwritable), destination

    unwritten = destination.publish("# the artefact\n")

    assert unwritten is None, (
        f"WHAT: an authorised replacement answered {unwritten!r}. "
        "WHY: the one thing in the way was the artefact the Owner "
        "authorised replacing. "
        "HOW: move the name onto the new file."
    )
    assert standing.read_text(encoding="utf-8") == "# the artefact\n", (
        f"WHAT: the name now reads {standing.read_text(encoding='utf-8')!r}. "
        "WHY: the authorised replacement is the new artefact under the old "
        "name. "
        "HOW: move the name in one step."
    )
    assert sorted(p.name for p in tmp_path.iterdir()) == ["clock.py"], (
        f"WHAT: the directory holds "
        f"{sorted(p.name for p in tmp_path.iterdir())}. "
        "WHY: nothing of the build is left beside the artefact. "
        "HOW: remove the working file on every path out."
    )
