"""The Owner asks what would have to be shown for a program, before any
solver exists.

`verify` answers with the complete inventory of obligations the program
owes: one for each potentially evaluated call's precondition under the
condition that reaches it, one per function connecting body to
postcondition, and separate entries for example validity, contract
definedness and structural termination (SPEC.md "Verification obligations
and the initial fragment", and "A checker that never ran has
`not_attempted`, not success").

Every entry is `not_attempted` and nothing in the answer reports work that
did not happen.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# Words that would report work this tool never did. Scanned over the whole
# answer, keys and values alike. `verify` itself is the operation's public
# name and says nothing about an outcome, so it is not listed.
CLAIM_WORD = re.compile(
    r"\b(verified|verifies|verification|proved|proven|proves|proof|"
    r"discharged|guaranteed|sound|correct|holds|built)\b",
    re.IGNORECASE,
)

# The hour clock this repository ships, read by hand: its three functions
# in the order it declares them, and how many examples each one declares.
# Written out here so every expected count comes from the shipped program a
# reader can open, never from the answer under observation.
CLOCK_FUNCTIONS = ("valid-state", "initial", "step")
CLOCK_EXAMPLE_COUNTS = {"valid-state": 4, "initial": 1, "step": 3}

# Every call to a declared function in the shipped hour clock, read by
# hand: who is called, from which function, and from which contract clause
# or body position. Nothing in the clock calls a function from a branch, so
# every one of them is reached unconditionally.
CLOCK_CALLS = {
    ("initial", "ensures[0]", "valid-state"),
    ("step", "requires[0]", "valid-state"),
    ("step", "ensures[0]", "valid-state"),
}

# The reservation example SPEC.md publishes, read by hand the same way.
RESERVATION_FUNCTIONS = ("valid-state", "initial", "step")
RESERVATION_EXAMPLE_COUNTS = {"valid-state": 2, "initial": 1, "step": 4}
RESERVATION_CALLS = {
    ("step", "requires[0]", "valid-state"),
    ("step", "ensures[0]", "valid-state"),
}

# A program whose call can never run: the condition reaching it is `false`.
# `caller`'s declared example returns 0 without ever calling `tiny`.
UNREACHABLE_CALL_SOURCE = """(defn tiny
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (examples (example (tiny 1) => 1))
  n)

(defn caller
  (sig ((n Int)) -> Int ! pure)
  (examples (example (caller 5) => 0))
  (if false (tiny n) 0))
"""

# The same program with the call in the branch that does run, so the
# condition reaching it differs and nothing else does.
REACHABLE_CALL_SOURCE = UNREACHABLE_CALL_SOURCE.replace(
    "(if false (tiny n) 0))", "(if true (tiny n) 0))"
)

# A program whose calls sit under more than one condition at once: three
# match clauses, the last of which matches anything, and an `if` inside a
# `let` inside the second clause. `pick` calls `tiny` four times.
NESTED_CONDITIONS_SOURCE = """(defn tiny
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (examples (example (tiny 1) => 1))
  n)

(defn pick
  (sig ((n Int)) -> Int ! pure)
  (examples (example (pick 1) => 1))
  (match n
    (0 (tiny n))
    (1 (let ((m n)) (if (> n 5) (tiny n) (tiny m))))
    (_ (tiny n))))
"""

# The condition that reaches each of those four calls, read by hand from
# the program above: a clause is reached when no earlier clause matched and
# this one does, and the clause that matches anything adds no condition of
# its own.
NESTED_CONDITIONS = {
    "call_precondition:pick:body/case[0]": "(matches n 0)",
    "call_precondition:pick:body/case[1]/in/then": (
        "(and (not (matches n 0)) (matches n 1) (> n 5))"
    ),
    "call_precondition:pick:body/case[1]/in/else": (
        "(and (not (matches n 0)) (matches n 1) (not (> n 5)))"
    ),
    "call_precondition:pick:body/case[2]": (
        "(and (not (matches n 0)) (not (matches n 1)))"
    ),
}

# The calls each function of that program makes, counted by hand.
NESTED_DIRECT_CALLS = {"tiny": 0, "pick": 4}


def _hour_clock_source() -> str:
    path = REPO_ROOT / "examples" / "hour-clock.prova"
    assert path.is_file(), (
        f"WHAT: the shipped hour clock {path} is missing, so nothing was read. "
        "WHY: this test states what the Owner is owed for that very program. "
        "HOW: restore it with `git checkout -- examples/hour-clock.prova`."
    )
    return path.read_text(encoding="utf-8")


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    start = text.index("## Core conformance example")
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    return text[fence_start : text.index("```", fence_start)]


def _run(operation: str, source: str) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps({"prova": "i1", "operation": operation, "source": source}),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure on {operation}: stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response from {operation}: {proc.stdout!r}")


def _inventory(response: dict) -> dict:
    assert response.get("status") == "completed", (
        f"WHAT: verify did not answer; it reported {response.get('status')!r}. "
        "WHY: the Owner asked for the list of obligations the program owes. "
        f"HOW: read the diagnostics in the answer: {response}"
    )
    inventory = (response.get("result") or {}).get("inventory")
    assert isinstance(inventory, dict), (
        "WHAT: the answer carries no inventory. "
        "WHY: the Owner cannot see the size and shape of the job without it. "
        f"HOW: the answer was: {response}"
    )
    return inventory


def _obligations(response: dict) -> list[dict]:
    entries = _inventory(response).get("obligations")
    assert isinstance(entries, list), f"the inventory lists no obligations: {response}"
    return entries


def _of_kind(entries: list[dict], kind: str) -> list[dict]:
    return [entry for entry in entries if entry.get("kind") == kind]


def _claim_words(value) -> list[str]:
    hits: list[str] = []

    def walk(node):
        if isinstance(node, str):
            hits.extend(match.group(0) for match in CLAIM_WORD.finditer(node))
        elif isinstance(node, dict):
            for key, child in node.items():
                walk(key)
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(value)
    return hits


def test_each_call_owes_its_precondition_under_the_condition_that_reaches_it():
    """Given the hour clock, when the Owner asks what must be shown, then
    the answer owes one obligation for each call the program can evaluate,
    naming who is called, where from, and the condition that reaches it.

    still passes if: the tool reported every condition as `true` whatever
    the branch -- every call in the hour clock is reached unconditionally.
    The unreachable-branch case below closes that.
    """
    entries = _of_kind(_obligations(_run("verify", _hour_clock_source())), "call_precondition")

    found = {(e.get("function"), e.get("site"), e.get("callee")) for e in entries}
    assert found == CLOCK_CALLS, (
        f"WHAT: the calls owing a precondition obligation are {sorted(found)}, "
        f"not the {len(CLOCK_CALLS)} calls the hour clock makes: {sorted(CLOCK_CALLS)}. "
        "WHY: every potentially evaluated call owes a precondition obligation; "
        "a missing one hides work, an extra one invents it. "
        "HOW: compare the answer with examples/hour-clock.prova clause by clause."
    )
    assert len(entries) == len(CLOCK_CALLS), f"one call was listed twice: {entries}"
    for entry in entries:
        assert entry.get("path_condition") == "true", (
            f"WHAT: the call at {entry.get('site')!r} in {entry.get('function')!r} is "
            f"reported as reached under {entry.get('path_condition')!r}. "
            "WHY: no call in the hour clock sits inside a branch, so each is reached "
            "whenever its function runs. "
            f"HOW: inspect that entry: {entry}"
        )


def test_the_owner_sees_what_each_function_owes_for_body_contract_examples_and_ending():
    """Given the hour clock, when the Owner asks what must be shown, then
    each of its three functions owes exactly one body-to-postcondition
    entry, one contract-definedness entry and one structural-termination
    entry, and each declared example owes its own validity entry.

    still passes if: the tool listed the right number of entries with
    useless text in them -- the honesty test below reads what each entry
    says it owes.
    """
    entries = _obligations(_run("verify", _hour_clock_source()))

    for kind in ("body_postcondition", "contract_definedness", "structural_termination"):
        functions = [entry.get("function") for entry in _of_kind(entries, kind)]
        assert sorted(functions) == sorted(CLOCK_FUNCTIONS), (
            f"WHAT: {kind} is owed by {sorted(functions)}, not once by each of the "
            f"hour clock's functions {sorted(CLOCK_FUNCTIONS)}. "
            "WHY: SPEC.md owes each of these per function, including a function that "
            "declares no postcondition: the entry is then trivial, not absent. "
            f"HOW: look at the {kind} entries in the answer."
        )

    per_function: dict[str, list[int]] = {name: [] for name in CLOCK_FUNCTIONS}
    for entry in _of_kind(entries, "example_validity"):
        assert entry.get("function") in per_function, f"unknown function in {entry}"
        per_function[entry["function"]].append(entry.get("ordinal"))
    counted = {name: len(ordinals) for name, ordinals in per_function.items()}
    assert counted == CLOCK_EXAMPLE_COUNTS, (
        f"WHAT: example-validity entries per function are {counted}, not the "
        f"{CLOCK_EXAMPLE_COUNTS} examples the hour clock declares. "
        "WHY: every declared example owes its own validity record. "
        "HOW: count the (example ...) forms in examples/hour-clock.prova."
    )
    for name, ordinals in per_function.items():
        assert sorted(ordinals) == list(range(CLOCK_EXAMPLE_COUNTS[name])), (
            f"WHAT: the examples of {name!r} are identified as {sorted(ordinals)}. "
            "WHY: the Owner must be able to tell one example's entry from another's. "
            f"HOW: number them as the function declares them, 0 upwards."
        )


def test_a_call_that_can_never_run_still_owes_its_obligation():
    """Given a program whose call sits in a branch that can never be taken,
    when the Owner asks what must be shown, then the obligation for that
    call is still listed, carrying the condition that reaches it.

    still passes if: the tool printed the same condition for every call --
    the reachable twin below differs only in that condition, and the two
    answers must differ there.
    """
    unreachable = _of_kind(
        _obligations(_run("verify", UNREACHABLE_CALL_SOURCE)), "call_precondition"
    )
    sites = {(e.get("function"), e.get("site"), e.get("callee")) for e in unreachable}
    assert sites == {("caller", "body/then", "tiny")}, (
        "WHAT: the call to 'tiny' inside the branch that can never be taken is "
        f"reported as {sorted(sites)}. "
        "WHY: an unreachable path makes an obligation vacuous; it does not remove it, "
        "so the Owner still sees the whole size of the job. "
        "HOW: list the call with the condition that reaches it instead of dropping it."
    )
    assert unreachable[0].get("path_condition") == "false", (
        f"WHAT: the condition reported for the unreachable call is "
        f"{unreachable[0].get('path_condition')!r}, not the branch's own `false`. "
        "WHY: the obligation is owed under the condition that reaches it. "
        f"HOW: inspect the entry: {unreachable[0]}"
    )

    reachable = _of_kind(_obligations(_run("verify", REACHABLE_CALL_SOURCE)), "call_precondition")
    assert len(reachable) == len(unreachable) == 1, (reachable, unreachable)
    assert reachable[0].get("path_condition") == "true", (
        f"WHAT: moving the call into the branch that does run left the condition "
        f"{reachable[0].get('path_condition')!r}. "
        "WHY: the condition reported must be the one that actually reaches the call, "
        "not a fixed word. "
        f"HOW: inspect the entry: {reachable[0]}"
    )


def test_a_call_behind_several_conditions_is_owed_under_all_of_them():
    """Given a program whose calls sit behind three match clauses and an
    `if` inside a `let`, when the Owner asks what must be shown, then each
    call carries every condition on the way to it, joined into one
    condition, in the order the program writes them.

    still passes if: the tool reported these four conditions and dropped a
    call somewhere else in the program -- the identity of every obligation
    this program owes is read in the laws test beside this one.
    """
    entries = _of_kind(
        _obligations(_run("verify", NESTED_CONDITIONS_SOURCE)), "call_precondition"
    )
    reported = {entry.get("id"): entry.get("path_condition") for entry in entries}

    assert reported == NESTED_CONDITIONS, (
        f"WHAT: the conditions reaching the calls are {reported}, not the "
        f"{len(NESTED_CONDITIONS)} the program writes: {NESTED_CONDITIONS}. "
        "WHY: an obligation is owed under the condition that reaches it, and here "
        "several conditions stand in front of each call at once: a clause is reached "
        "only when no earlier clause matched, and a branch only when its own test "
        "holds. Reporting one of them, or reporting a condition for the clause that "
        "matches anything, misstates what has to be shown. "
        f"HOW: read the program and compare clause by clause:\n"
        f"{NESTED_CONDITIONS_SOURCE}"
    )


def test_the_ending_entry_says_how_many_calls_the_function_makes():
    """Given the same program, when the Owner reads the entry that says a
    function ends, then it counts the calls that function makes: four for
    the one that calls, none for the one that calls nothing.

    still passes if: the tool counted the calls of the whole program for
    every function -- the function that makes no call is read here too, and
    it must be reported as making none.
    """
    entries = _of_kind(
        _obligations(_run("verify", NESTED_CONDITIONS_SOURCE)), "structural_termination"
    )
    counted = {entry.get("function"): entry.get("direct_calls") for entry in entries}

    assert counted == NESTED_DIRECT_CALLS, (
        f"WHAT: the ending entries report {counted} calls, not the "
        f"{NESTED_DIRECT_CALLS} the program writes. "
        "WHY: a function ends structurally because the calls it reaches are acyclic, "
        "so the Owner is told how many calls that claim is about; a fixed number "
        "tells them nothing about this program. "
        f"HOW: count the calls in:\n{NESTED_CONDITIONS_SOURCE}"
    )


def test_nothing_in_the_answer_reports_work_the_tool_never_did():
    """Given the hour clock and the reservation example, when the Owner
    reads the answers, then every obligation is marked `not_attempted`, the
    counts say none was attempted, and no word in either answer reports a
    program as checked, shown or built.

    still passes if: the tool marked entries `not_attempted` while a later
    field claimed an overall outcome -- the word scan over the whole answer,
    keys included, covers that.
    """
    assert _claim_words("this program was proved and the postcondition holds"), (
        "WHAT: the scan for words reporting work found nothing in a sentence that "
        "plainly reports it. WHY: a scan that cannot fire proves nothing. "
        "HOW: fix CLAIM_WORD in this test."
    )

    for label, source in (
        ("the hour clock", _hour_clock_source()),
        ("the reservation example", _reservation_source()),
    ):
        response = _run("verify", source)
        inventory = _inventory(response)
        entries = _obligations(response)

        results = {entry.get("result") for entry in entries}
        assert results == {"not_attempted"}, (
            f"WHAT: {label} has obligations reported as {sorted(results)}. "
            "WHY: this tool has no solver; a checker that never ran is `not_attempted`, "
            "never a success. "
            f"HOW: inspect the answer: {response}"
        )

        totals = inventory.get("totals") or {}
        assert totals.get("obligations") == len(entries), (
            f"WHAT: {label} reports {totals.get('obligations')} obligations while listing "
            f"{len(entries)}. WHY: the count must name the list it counts. "
            f"HOW: inspect the totals: {totals}"
        )
        assert totals.get("attempted") == 0, f"{label}: {totals}"
        assert totals.get("attempted", 0) + totals.get("not_attempted", -1) == len(entries), (
            f"WHAT: for {label} the attempted and not-attempted counts do not add up to "
            f"the {len(entries)} obligations listed. "
            "WHY: every obligation is in exactly one of the two. "
            f"HOW: inspect the totals: {totals}"
        )

        hits = _claim_words(response)
        assert not hits, (
            f"WHAT: the answer for {label} contains {sorted(set(hits))}. "
            "WHY: nothing ran, so the answer must report no outcome at all. "
            f"HOW: reword the answer: {response}"
        )
        assert isinstance(inventory.get("note"), str) and inventory["note"].strip(), (
            f"WHAT: the answer for {label} carries no note saying nothing was attempted. "
            "WHY: a reader must not mistake a list of work owed for work done. "
            f"HOW: inspect the inventory: {inventory}"
        )


def test_the_reservation_example_owes_an_entry_for_every_function_it_declares():
    """Given the reservation example SPEC.md publishes, when the Owner asks
    what must be shown, then the inventory names every function it declares,
    owes the four kinds of entry SPEC.md lists, and misses none of its
    examples or calls.

    still passes if: the tool invented an extra obligation for a function
    that does not exist -- the function names are compared as a whole set,
    so an extra one fails too.
    """
    entries = _obligations(_run("verify", _reservation_source()))

    named = {entry.get("function") for entry in entries}
    assert named == set(RESERVATION_FUNCTIONS), (
        f"WHAT: the inventory names {sorted(named)}, not the reservation example's "
        f"functions {sorted(RESERVATION_FUNCTIONS)}. "
        "WHY: no function of the program may be missing from the inventory. "
        "HOW: compare with the Core conformance example in SPEC.md."
    )

    kinds = {entry.get("kind") for entry in entries}
    assert kinds == {
        "call_precondition",
        "body_postcondition",
        "example_validity",
        "contract_definedness",
        "structural_termination",
    }, (
        f"WHAT: the inventory owes the kinds {sorted(kinds)}. "
        "WHY: SPEC.md names precondition obligations, body-to-postcondition "
        "obligations and separate records for example validity, contract "
        "definedness and structural termination. "
        "HOW: add the missing kind or drop the invented one."
    )

    calls = {
        (e.get("function"), e.get("site"), e.get("callee"))
        for e in _of_kind(entries, "call_precondition")
    }
    assert calls == RESERVATION_CALLS, (
        f"WHAT: the calls owing a precondition obligation are {sorted(calls)}, not "
        f"{sorted(RESERVATION_CALLS)}. "
        "WHY: the example calls `valid-state` from `step`'s precondition and from its "
        "postcondition, and nowhere else. "
        "HOW: compare with the Core conformance example in SPEC.md."
    )

    counted = {name: 0 for name in RESERVATION_FUNCTIONS}
    for entry in _of_kind(entries, "example_validity"):
        counted[entry["function"]] += 1
    assert counted == RESERVATION_EXAMPLE_COUNTS, (
        f"WHAT: example-validity entries per function are {counted}, not the "
        f"{RESERVATION_EXAMPLE_COUNTS} examples the published program declares. "
        "WHY: every declared example owes its own validity record. "
        "HOW: count the (example ...) forms in SPEC.md's conformance example."
    )
    for kind in ("body_postcondition", "contract_definedness", "structural_termination"):
        assert len(_of_kind(entries, kind)) == len(RESERVATION_FUNCTIONS), (
            f"WHAT: {kind} is owed {len(_of_kind(entries, kind))} times, not once for "
            f"each of the {len(RESERVATION_FUNCTIONS)} functions declared. "
            "WHY: SPEC.md owes this record per function. "
            "HOW: inspect those entries in the answer."
        )


def test_asking_twice_about_the_same_program_owes_exactly_the_same_list():
    """Given the hour clock, when the Owner asks what must be shown twice,
    then both answers list the same obligations with the same identities in
    the same order.

    still passes if: both runs were equally wrong -- the other tests fix
    what the list must contain; this one fixes only that it does not drift.
    """
    source = _hour_clock_source()
    first = _run("verify", source)
    second = _run("verify", source)

    assert first.get("result") == second.get("result"), (
        "WHAT: two runs on the same source answered with different inventories. "
        "WHY: the Owner must be able to compare two answers and see real change. "
        f"HOW: first={first.get('result')} second={second.get('result')}"
    )
    identities = [entry.get("id") for entry in _obligations(first)]
    assert len(set(identities)) == len(identities), (
        f"WHAT: {len(identities) - len(set(identities))} obligation identities repeat. "
        "WHY: an identity must name one obligation, so answers can be compared. "
        f"HOW: inspect the identities: {identities}"
    )
    assert all(isinstance(identity, str) and identity for identity in identities), identities
