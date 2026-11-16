"""The Owner reads one word that says whether the whole program was shown.

Until now the Owner read an inventory of obligations and had to add it up
themselves: twenty entries, each proved or not, with the declared examples
run by a separate command. SPEC.md, "Results and evidence scope", says
what the word over the whole is worth: "An aggregate verified result
requires a complete inventory of required obligations, all discharged,
plus passing examples and static checks for the selected profile. ...
Incomplete verification must never produce an artefact labelled verified."

So the word appears in an answer only when all three hold, and an answer
that cannot say it says which of the three stopped it.

Drives only the `prova` command's real JSON stdin/stdout surface, the way
the Owner does. No imports from src/prova.
"""

from __future__ import annotations

import pathlib

from _f18_fixtures import completed, obligations_of, the_manifest, verify

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

A = "=>"

# The hour clock this repository ships, and how many examples it declares,
# counted by hand from the file a reader can open: four for `valid-state`,
# one for `initial` and three for `step`.
THE_SHIPPED_EXAMPLES = 8

# The one example of the shipped clock this file makes wrong, and what it
# says instead. `valid-state` of an hour of 1 is true in the program; the
# copy says it is false, so that one example fails when it is run while
# the program itself is unchanged in every other way.
A_TRUE_EXAMPLE = f"(example (valid-state (Clock 1)) {A} true)"
THE_SAME_EXAMPLE_MADE_WRONG = f"(example (valid-state (Clock 1)) {A} false)"

# A program whose body does not have the type its signature declares. The
# checker refuses it, so nothing about it is ever shown.
THE_CHECKER_REFUSES = f"""(defn truthy
  (sig ((n Int)) -> Bool ! pure)
  (examples (example (truthy 1) {A} true))
  n)
"""

# A program whose promise needs the product of two numbers neither of
# which is known. SPEC.md keeps the automated fragment linear and puts the
# general product outside it, so that obligation comes back unsettled --
# while the obligations of the function beside it are settled as usual.
A_MIX_OF_INSIDE_AND_OUTSIDE = f"""(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (requires (>= n 0))
  (ensures (>= result 0))
  (examples (example (doubled 3) {A} 6))
  (* 2 n))

(defn product
  (sig ((n Int) (m Int)) -> Int ! pure)
  (requires (and (>= n 0) (>= m 0)))
  (ensures (>= result 0))
  (examples (example (product 2 3) {A} 6))
  (* n m))
"""


def _hour_clock() -> str:
    return (REPO_ROOT / "examples" / "hour-clock.prova").read_text(encoding="utf-8")


def _aggregate(answer: dict, about: str) -> dict:
    aggregate = answer.get("aggregate")
    assert isinstance(aggregate, dict), (
        f"WHAT: the verify answer about {about} carries no aggregate: "
        f"{sorted(answer)}. "
        "WHY: the Owner reads one word for the whole program; an answer that "
        "only lists entries leaves them to add it up, and SPEC.md requires "
        "the aggregate to rest on the complete inventory. "
        f"HOW: inspect the answer: {answer}"
    )
    return aggregate


def test_a_program_shown_whole_comes_back_verified_with_its_inventory():
    """Given the hour clock this repository ships, whose every obligation
    is discharged and whose 8 declared examples all pass, when the Owner
    verifies it, then the answer says `verified` and carries the inventory
    it rests on.

    still passes if: the tool said `verified` for every program -- the
    four tests below each give it a program where one of the three
    conditions does not hold, and require the word to be withheld.
    """
    source = _hour_clock()
    answer = completed(verify(source), "the shipped hour clock")
    aggregate = _aggregate(answer, "the shipped hour clock")
    entries = obligations_of(answer, "the shipped hour clock")

    assert aggregate["result"] == "verified", (
        f"WHAT: the aggregate over the shipped hour clock is "
        f"{aggregate['result']!r}. "
        "WHY: every obligation of this program is discharged, every example "
        "it declares passes and the checker accepts it, which is what the "
        "word stands for. "
        f"HOW: inspect the entries that are not proved: "
        f"{[e['id'] for e in entries if e.get('result') != 'proved']}"
    )
    assert aggregate["execution_status"] == "completed", aggregate

    counted = aggregate["obligations"]
    assert counted["of"] == len(entries) and counted["discharged"] == len(entries), (
        f"WHAT: the aggregate counts {counted} over the {len(entries)} "
        "obligations the answer lists. "
        "WHY: the word rests on a complete inventory, so the count must name "
        "the list it counts. "
        f"HOW: inspect the inventory: {counted}"
    )
    assert counted["undischarged"] == [], counted

    examples = aggregate["examples"]
    assert examples == {
        "of": THE_SHIPPED_EXAMPLES,
        "passed": THE_SHIPPED_EXAMPLES,
        "failed": [],
        "not_run": 0,
    }, (
        f"WHAT: the aggregate reports {examples} over the "
        f"{THE_SHIPPED_EXAMPLES} examples the shipped clock declares. "
        "WHY: the word rests on the examples passing, and they are counted "
        "against the program a reader can open. "
        "HOW: run every declared example and count all three outcomes."
    )
    assert aggregate["static_checks"] == {"passed": True, "diagnostics": 0}, aggregate


def test_an_obligation_left_unsettled_withholds_the_word():
    """Given a program of two functions, one of which promises something
    about the product of two unknown numbers, when the Owner verifies it,
    then the aggregate is not verified, names that obligation, and the
    results of the other function are still there to read.

    F19 criterion 4 and F21 criterion 2 and 4 together: an obligation the
    tool cannot translate stops the word over the whole, and removes
    nothing from the rest of the program.

    still passes if: the tool dropped the unsettled obligation from the
    inventory instead of reporting it -- the entries of `doubled` are
    required to be proved and the unsettled entry is required to be
    present and named.
    """
    about = "a program mixing an in-fragment and an out-of-fragment promise"
    answer = completed(verify(A_MIX_OF_INSIDE_AND_OUTSIDE), about)
    aggregate = _aggregate(answer, about)
    entries = obligations_of(answer, about)

    unsettled = [entry for entry in entries if entry.get("result") == "unknown"]
    assert unsettled, (
        f"WHAT: every obligation of {about} was settled. "
        "WHY: this test needs the obligation about the product of two unknown "
        "numbers to be the one the fragment does not cover; a tool that "
        "settles it has grown a fragment this test no longer describes. "
        f"HOW: inspect the entries: {[(e['id'], e['result']) for e in entries]}"
    )
    assert aggregate["result"] == "not_verified", (
        f"WHAT: the aggregate is {aggregate['result']!r} while "
        f"{len(unsettled)} obligations are unsettled. "
        "WHY: the word stands for a complete inventory, all discharged; one "
        "obligation the tool cannot translate means the program was not "
        "shown. "
        f"HOW: inspect the aggregate: {aggregate}"
    )
    assert aggregate["execution_status"] == "unsupported", aggregate

    named = set(aggregate["obligations"]["undischarged"])
    assert named == {entry["id"] for entry in unsettled}, (
        f"WHAT: the aggregate names {sorted(named)} as undischarged and the "
        f"unsettled entries are {sorted(e['id'] for e in unsettled)}. "
        "WHY: a reader told the program was not shown needs to know exactly "
        "which part of it was not. "
        f"HOW: inspect the answer: {aggregate}"
    )

    beside_it = [
        (entry["id"], entry["result"])
        for entry in entries
        if entry.get("function") == "doubled"
    ]
    assert beside_it and all(result == "proved" for _, result in beside_it), (
        f"WHAT: the obligations of the function beside the untranslatable one "
        f"came back {beside_it}. "
        "WHY: SPEC.md: no unsupported function may erase unrelated "
        "obligations; what was shown about the rest of the program stays "
        "visible. "
        f"HOW: inspect the answer: {answer}"
    )


def test_an_example_that_does_not_pass_withholds_the_word():
    """Given the shipped hour clock with one of its 8 examples made wrong,
    when the Owner verifies it, then the aggregate is not verified and
    names that one example, while the other 7 are reported as passing.

    F21 criterion 3. The examples are run, not read off the obligations:
    the answer says how many of the program's own examples passed.

    still passes if: the tool reported every example as failing once one
    did -- the passing count is compared to the 7 that still pass.
    """
    source = _hour_clock().replace(A_TRUE_EXAMPLE, THE_SAME_EXAMPLE_MADE_WRONG)
    assert source != _hour_clock(), (
        "WHAT: the shipped clock does not contain the example this test "
        f"makes wrong: {A_TRUE_EXAMPLE}. "
        "WHY: a test that silently changed nothing would verify the shipped "
        "clock under another name. "
        "HOW: read examples/hour-clock.prova and fix the text above."
    )
    about = "the hour clock with one example made wrong"
    answer = completed(verify(source), about)
    aggregate = _aggregate(answer, about)

    assert aggregate["result"] == "not_verified", (
        f"WHAT: the aggregate is {aggregate['result']!r} for a program one of "
        "whose own examples does not hold. "
        "WHY: the word rests on passing examples as well as on discharged "
        "obligations. "
        f"HOW: inspect the aggregate: {aggregate}"
    )
    examples = aggregate["examples"]
    assert examples["of"] == THE_SHIPPED_EXAMPLES, examples
    assert examples["passed"] == THE_SHIPPED_EXAMPLES - 1, (
        f"WHAT: the aggregate reports {examples['passed']} of "
        f"{THE_SHIPPED_EXAMPLES} examples passing, and only one was made "
        "wrong. "
        "WHY: a reader must see which examples still hold; reporting them all "
        "as failed over one wrong answer says the program is worse than it "
        "is. "
        f"HOW: inspect the aggregate: {examples}"
    )
    assert examples["failed"] == [{"function": "valid-state", "ordinal": 0}], (
        f"WHAT: the aggregate names {examples['failed']} as the failing "
        "examples, and the one made wrong is the first example of "
        "'valid-state'. "
        "WHY: a reader needs the example to open, not a count. "
        f"HOW: inspect the aggregate: {examples}"
    )


def test_a_program_the_checker_refuses_is_never_called_verified():
    """Given a program whose body does not have the type its signature
    declares, when the Owner verifies it, then the answer is the refusal,
    it carries no aggregate at all, and the word appears nowhere in it.

    The third condition of the word: the static checks must pass. A
    refused program has no inventory, so there is nothing to aggregate and
    nothing to say about it.
    """
    answer = verify(THE_CHECKER_REFUSES)

    assert answer.get("status") == "invalid_program", (
        f"WHAT: a program the checker refuses was answered "
        f"{answer.get('status')!r}. "
        "WHY: this test is about what a refusal says; an accepted program "
        "would not exercise it. "
        f"HOW: inspect the answer: {answer}"
    )
    assert "aggregate" not in answer, (
        f"WHAT: the refusal carries an aggregate: {answer.get('aggregate')}. "
        "WHY: nothing was shown about a program that was never read past its "
        "static checks, so there is nothing to aggregate. "
        f"HOW: inspect the answer: {answer}"
    )
    assert "verified" not in str(answer).lower(), (
        f"WHAT: the word 'verified' appears in a refusal: {answer}. "
        "WHY: the word may be said only where the three conditions behind it "
        "are published, and a refusal publishes none of them. "
        "HOW: carry the aggregate only on a completed answer."
    )


def test_the_manifest_describes_the_word_before_a_request_is_sent():
    """Given a client that has sent no request of its own yet, when it
    asks what this tool offers, then the fields of a verify answer
    include the aggregate, and what is published about it says the three
    things the word rests on.

    A reader who meets `verified` must be able to look up what it stands
    for before trusting it, from the published shape rather than from
    prose found somewhere in the answer.
    """
    published = (
        (the_manifest().get("result") or {})
        .get("operation_schemas", {})
        .get("verify", {})
        .get("response", {})
        .get("fields", {})
    )

    assert "aggregate" in published, (
        f"WHAT: a verify answer publishes the fields {sorted(published)}. "
        "WHY: an answer may carry no field the manifest does not describe, "
        "and a client that meets the word must be able to look it up before "
        "it sends a request. "
        "HOW: describe the field in manifest.py beside the others."
    )
    described = str(published["aggregate"]).lower()
    for owed in ("discharged", "examples", "static"):
        assert owed in described, (
            f"WHAT: what the manifest publishes about the aggregate does not "
            f"mention {owed!r}: {described}. "
            "WHY: the word rests on a complete inventory all discharged, on "
            "passing examples and on the static checks passing, and a reader "
            "told only the word knows none of that. "
            "HOW: say all three in the field's description."
        )


def test_the_aggregate_counts_rules_apart_from_solver_answers():
    """Given the shipped hour clock, when the Owner reads the aggregate,
    then the obligations a rule of core-0 settled are counted apart from
    the ones a solver answered, and the two add up to what was discharged.

    F21 criterion 5, read over the whole: "The inventory identifies
    structurally discharged checks as well as solver checks."

    still passes if: the tool counted every entry under one of the two --
    both counts are compared with the entries of the answer itself.
    """
    about = "the shipped hour clock"
    answer = completed(verify(_hour_clock()), about)
    aggregate = _aggregate(answer, about)
    entries = obligations_of(answer, about)

    by_the_entries = {
        way: len([e for e in entries if e.get("discharged_by") == way])
        for way in ("solver", "structure")
    }
    assert aggregate["obligations"]["by"] == by_the_entries, (
        f"WHAT: the aggregate counts {aggregate['obligations']['by']} and the "
        f"entries it is over are {by_the_entries}. "
        "WHY: the count over the whole must be the count of the list it is "
        "over, or the two tell a reader different things. "
        f"HOW: count each entry under the way it was discharged: {aggregate}"
    )
    assert min(by_the_entries.values()) > 0, (
        f"WHAT: the shipped clock has obligations settled only one way: "
        f"{by_the_entries}. "
        "WHY: this test needs both kinds to tell them apart; with one kind it "
        "would pass over a tool that could not. "
        f"HOW: inspect the entries: "
        f"{[(e['id'], e.get('discharged_by')) for e in entries]}"
    )
    assert sum(aggregate["obligations"]["by"].values()) == (
        aggregate["obligations"]["discharged"]
    ), aggregate
