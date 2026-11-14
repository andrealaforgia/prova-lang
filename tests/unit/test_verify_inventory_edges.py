"""The edges of the obligation inventory: a program with nothing in it, a
program that does not read, a program that does not check -- and the fact
that answering what `verify` owes did not make `build` answer anything.

Exercises the service's public operation contract in process, as the other
unit tests here do; the user-facing journey is driven through the `prova`
command in tests/acceptance.
"""

from __future__ import annotations

from prova import service


def _ask(operation: str, source: str) -> dict:
    return service.handle({"prova": "i1", "operation": operation, "source": source})


def test_a_program_with_nothing_in_it_owes_nothing_and_says_so():
    """Given an empty program, when the Owner asks what must be shown, then
    the answer is an inventory of no obligations -- which reads differently
    from the refusal an unreadable program gets.

    still passes if: the tool answered an empty inventory for everything --
    the unreadable program in the same test must not get one.
    """
    empty = _ask("verify", "")
    assert empty["status"] == "completed", empty
    inventory = empty["result"]["inventory"]
    assert inventory["obligations"] == [], (
        "WHAT: an empty program was reported as owing "
        f"{len(inventory['obligations'])} obligations. "
        "WHY: a program that declares nothing owes nothing. "
        f"HOW: inspect the answer: {empty}"
    )
    assert inventory["totals"]["obligations"] == 0, inventory
    assert inventory["totals"]["attempted"] == 0, inventory

    unreadable = _ask("verify", "(defn broken")
    assert unreadable["status"] == "invalid_program", (
        "WHAT: a program whose text does not read was answered with "
        f"{unreadable['status']!r}. "
        "WHY: the Owner must see that nothing could be read, not an empty list of "
        "work. "
        f"HOW: inspect the answer: {unreadable}"
    )
    assert {d["category"] for d in unreadable["diagnostics"]} == {"syntax"}, unreadable
    assert "result" not in unreadable, (
        f"WHAT: a refused program still carried a result: {unreadable}. "
        "WHY: nothing was read, so nothing can be owed. "
        "HOW: return the refusal alone."
    )
    assert unreadable["status"] != empty["status"], (empty, unreadable)


def test_a_program_that_does_not_check_is_refused_instead_of_listed():
    """Given a program that calls a function it never declares, when the
    Owner asks what must be shown, then the answer refuses it with the same
    diagnostic the whole-program check gives, and lists no obligations.

    still passes if: the tool refused every program it was given -- the
    empty and the shipped programs in the other tests are answered.
    """
    source = (
        "(defn caller\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        "  (examples (example (caller 1) => 1))\n"
        "  (missing n))\n"
    )
    refused = _ask("verify", source)
    checked = _ask("check", source)

    assert refused["status"] == "invalid_program", refused
    assert "result" not in refused, refused
    assert [d["category"] for d in refused["diagnostics"]] == [
        d["category"] for d in checked["diagnostics"]
    ], (
        "WHAT: the refusal categories differ from the ones the whole-program check "
        f"reports: {refused['diagnostics']} against {checked['diagnostics']}. "
        "WHY: every declaration, branch and call is resolved and typed before any "
        "obligation is listed, and the Owner should read one vocabulary for that. "
        "HOW: report the check's own diagnostics unchanged."
    )
    assert "unbound_name" in {d["category"] for d in refused["diagnostics"]}, (
        "WHAT: the call to a function the program never declares was not reported as "
        f"an unbound name: {refused}. "
        "WHY: that is the category the whole-program check gives it, and verify must "
        "speak the same vocabulary. "
        "HOW: compare with the check operation's answer for the same source."
    )


def test_listing_what_verify_owes_did_not_make_build_answer():
    """Given the same program, when the Owner asks what must be shown and
    then asks for a built artefact, then the first is answered and the
    second is still refused as unavailable.

    still passes if: both were refused -- the inventory of the first is
    read here as well.
    """
    source = "(defn one\n  (sig () -> Int ! pure)\n  (examples (example (one) => 1))\n  1)\n"

    listed = _ask("verify", source)
    assert listed["status"] == "completed", listed
    assert listed["result"]["inventory"]["obligations"], listed

    refused = _ask("build", source)
    assert refused["status"] == "unavailable", (
        "WHAT: `build` answered with "
        f"{refused['status']!r} after `verify` learned to list obligations. "
        "WHY: a build must stay closed while the obligations are not attempted. "
        f"HOW: inspect the answer: {refused}"
    )
    assert {d["category"] for d in refused["diagnostics"]} == {"operation_unavailable"}, refused
