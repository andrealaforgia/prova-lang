"""The one table that decides whether the word `verified` may be said.

A wrong `verified` is as bad as a wrong `proved`: it tells the Owner that
the whole of a program was shown when part of it was not, and an artefact
built on it would carry that claim further. So the word is decided in one
place, by a pure function over three things -- what became of every
obligation, what the declared examples did when they were run, and the
evidence that the static checks passed -- and nothing else may say it.

SPEC.md, "Results and evidence scope": "An aggregate verified result
requires a complete inventory of required obligations, all discharged,
plus passing examples and static checks for the selected profile."

Every expected outcome in the table below is written out by hand from
that sentence and from F21's acceptance criteria. None of them is read
off the tool: a table copied from what the code answers would agree with
the code however wrong both were.

The module under test is imported inside each test rather than at the top
of the file, so a row this tool cannot answer yet fails as the case it is,
named, instead of stopping the file from being collected at all.
"""

from __future__ import annotations

import pytest

# What one obligation came back as: where it stands as a statement, and
# what happened to the attempt to settle it. SPEC.md lines 270-284 keep
# the two apart; the pairs below are the ones this tool can build.
PROVED = ("proved", "completed")
DISPROVED = ("disproved", "completed")
UNKNOWN_OUTSIDE_THE_FRAGMENT = ("unknown", "unsupported")
UNKNOWN_OUT_OF_TIME = ("unknown", "timed_out")
UNKNOWN_NO_SOLVER_LOADED = ("unknown", "tool_failure")
NOTHING_ATTEMPTED = ("not_attempted", "unsupported")

# The two words the aggregate may stand as.
VERIFIED = "verified"
NOT_VERIFIED = "not_verified"

# What the declared examples did. The third is not a failing example: it
# is a run this tool could not finish inside its own evaluation budget,
# which says nothing about the program and must not be read as a pass.
ALL_EIGHT_PASSED = ("all passed", 8)
ONE_OF_EIGHT_FAILED = ("one failed", 8)
THE_RUN_WAS_STOPPED = ("stopped", 8)

# The table. Each row: what the Owner would be looking at, the obligations
# of the program, what its examples did, and the two words the aggregate
# must carry. Written from the criteria, by hand.
#
# Row 3 is F21 criterion 3 read literally -- "one failing example, then the
# aggregate is not verified even if every obligation is proved". Through
# `verify` a failing example also breaks its own example-validity
# obligation, so that row cannot be reached from outside; it is stated
# here because the rule is about the examples and not about that
# obligation, and a tool that dropped the examples from the table would
# still pass every test that can be run through the command.
THE_TABLE = (
    (
        "one obligation proved and every example passing",
        (PROVED,),
        ALL_EIGHT_PASSED,
        VERIFIED,
        "completed",
    ),
    (
        "twenty obligations proved and every example passing",
        (PROVED,) * 20,
        ALL_EIGHT_PASSED,
        VERIFIED,
        "completed",
    ),
    (
        "every obligation proved and one example failing",
        (PROVED, PROVED),
        ONE_OF_EIGHT_FAILED,
        NOT_VERIFIED,
        "completed",
    ),
    (
        "every obligation proved and the example run stopped part way",
        (PROVED, PROVED),
        THE_RUN_WAS_STOPPED,
        NOT_VERIFIED,
        "resource_exhausted",
    ),
    (
        "one obligation left outside the fragment",
        (PROVED, UNKNOWN_OUTSIDE_THE_FRAGMENT),
        ALL_EIGHT_PASSED,
        NOT_VERIFIED,
        "unsupported",
    ),
    (
        "one obligation the solver ran out of time on",
        (PROVED, UNKNOWN_OUT_OF_TIME),
        ALL_EIGHT_PASSED,
        NOT_VERIFIED,
        "timed_out",
    ),
    (
        "one obligation no solver could be loaded for",
        (PROVED, UNKNOWN_NO_SOLVER_LOADED),
        ALL_EIGHT_PASSED,
        NOT_VERIFIED,
        "tool_failure",
    ),
    (
        "one obligation disproved",
        (PROVED, DISPROVED),
        ALL_EIGHT_PASSED,
        NOT_VERIFIED,
        "completed",
    ),
    (
        "one obligation nothing attempted",
        (PROVED, NOTHING_ATTEMPTED),
        ALL_EIGHT_PASSED,
        NOT_VERIFIED,
        "unsupported",
    ),
    (
        "a timed-out obligation beside one no solver could be loaded for",
        (UNKNOWN_OUT_OF_TIME, UNKNOWN_NO_SOLVER_LOADED),
        ALL_EIGHT_PASSED,
        NOT_VERIFIED,
        "tool_failure",
    ),
    (
        "nothing owed at all",
        (),
        ALL_EIGHT_PASSED,
        NOT_VERIFIED,
        "completed",
    ),
)

# Which execution status the aggregate carries when several are in play,
# most serious first. A failure of this tool outranks a limit this tool
# stopped at, which outranks a question it declined to translate, which
# outranks an attempt that finished: a reader must be told the worst thing
# that happened to the verification, not the commonest.
MOST_SERIOUS_FIRST = (
    "tool_failure",
    "invalid_input",
    "resource_exhausted",
    "cancelled",
    "timed_out",
    "unsupported",
    "completed",
)


def _verdict():
    """The module that owns the word, imported where a failure to import
    it is the case under test failing and not the file refusing to be
    read."""
    from prova import verdict

    return verdict


def _findings(pairs):
    """One finding per obligation, by identity, built straight from the
    pairs of the table: this file states what came back, and the function
    under test decides what that is worth."""
    from prova import discharge

    return {
        f"o{number}": discharge.Finding(result, status)
        for number, (result, status) in enumerate(pairs, start=1)
    }


def _examples(what):
    """The declared examples of a program, as the run left them."""
    verdict = _verdict()
    name, declared = what
    if name == "all passed":
        entries = [
            {"function": "valid-state", "ordinal": ordinal, "passed": True}
            for ordinal in range(declared)
        ]
        return verdict.ExamplesRun.of(entries, declared)
    if name == "one failed":
        entries = [
            {"function": "valid-state", "ordinal": ordinal, "passed": ordinal != 0}
            for ordinal in range(declared)
        ]
        return verdict.ExamplesRun.of(entries, declared)
    return verdict.ExamplesRun.stopped_at(
        [],
        declared,
        "resource_exhausted",
        "the run reached the evaluation depth this tool allows",
    )


def _checks():
    """The evidence a program passed the static checks: the checker
    accepted it and reported nothing."""
    return _verdict().StaticChecksPassed.of(())


def _aggregate(pairs, examples):
    return _verdict().Verdict.over(_findings(pairs), _examples(examples), _checks())


@pytest.mark.parametrize(
    "label,pairs,examples,expected_result,expected_status",
    [(row[0], row[1], row[2], row[3], row[4]) for row in THE_TABLE],
    ids=[row[0] for row in THE_TABLE],
)
def test_each_row_of_the_table_is_decided_the_way_the_criteria_say(
    label, pairs, examples, expected_result, expected_status
):
    """Given each situation the criteria name, when the aggregate is
    decided, then it stands as the word the criteria give it and says
    what happened to the attempt.

    still passes if: the tool answered `not_verified` for everything --
    the two verified rows at the top of the table require the word to be
    said where it is owed.
    """
    aggregate = _aggregate(pairs, examples)

    assert (aggregate.result, aggregate.execution_status) == (
        expected_result,
        expected_status,
    ), (
        f"WHAT: with {label} the aggregate is "
        f"{(aggregate.result, aggregate.execution_status)}, and the criteria "
        f"give it {(expected_result, expected_status)}. "
        "WHY: the word 'verified' may be said only when every obligation is "
        "discharged, every example passes and the static checks passed, and "
        "the status beside it must say what happened to the attempt. "
        "HOW: decide the row in prova/verdict.py, where the table lives."
    )


def test_a_program_that_is_not_verified_says_which_part_was_not_shown():
    """Given a program with one obligation outside the fragment, when the
    aggregate is read, then it names that obligation and says what to do
    about it.

    still passes if: the reason named every obligation -- the proved one
    must not be listed as undischarged.
    """
    aggregate = _aggregate(
        (PROVED, UNKNOWN_OUTSIDE_THE_FRAGMENT), ALL_EIGHT_PASSED
    )
    published = aggregate.published()

    assert published["obligations"]["undischarged"] == ["o2"], (
        f"WHAT: the aggregate reports {published['obligations']} as "
        "undischarged, and the one obligation that was not discharged is "
        "'o2'. "
        "WHY: a reader told the whole was not shown must be told which part "
        "was not, or they have nowhere to start. "
        "HOW: list exactly the obligations whose result is not 'proved'."
    )
    assert isinstance(published.get("reason"), str) and published["reason"].strip(), (
        f"WHAT: the aggregate carries no reason: {published}. "
        "WHY: a verdict of 'not_verified' with no reason tells a reader "
        "nothing they can act on. "
        "HOW: say what was not shown, why that stops the word, and what to do."
    )
    assert "o2" in published["reason"], (
        f"WHAT: the reason {published['reason']!r} does not name 'o2'. "
        "WHY: the fact the reader needs is which obligation stopped the word. "
        "HOW: write the undischarged identities into the reason."
    )


def test_a_verified_program_says_nothing_was_left_undischarged():
    """Given a program whose every obligation is proved and whose examples
    all pass, when the aggregate is read, then it carries the word and no
    reason, and the counts it publishes add up to what it counted."""
    aggregate = _aggregate((PROVED,) * 20, ALL_EIGHT_PASSED)
    published = aggregate.published()

    assert published["result"] == VERIFIED, published
    assert "reason" not in published, (
        f"WHAT: a verified aggregate carries a reason: {published}. "
        "WHY: a reason says what stopped the word; where nothing stopped it "
        "there is nothing to say, and prose beside the word invites a reader "
        "to look for a catch. "
        "HOW: carry the reason only where the aggregate is not verified."
    )
    counted = published["obligations"]
    assert counted["discharged"] + len(counted["undischarged"]) == counted["of"], (
        f"WHAT: the obligation counts {counted} do not add up to the "
        f"{counted['of']} obligations they are about. "
        "WHY: every obligation is discharged or it is not; a count that does "
        "not partition the list it counts can hide one. "
        "HOW: count both from the same findings."
    )
    examples = published["examples"]
    assert examples["passed"] + len(examples["failed"]) + examples["not_run"] == (
        examples["of"]
    ), (
        f"WHAT: the example counts {examples} do not add up to the "
        f"{examples['of']} examples the program declares. "
        "WHY: every declared example passed, failed or was not run. "
        "HOW: count all three from the same run."
    )


def test_the_counts_say_what_a_rule_settled_apart_from_what_a_solver_settled():
    """Given obligations settled both ways, when the aggregate is read,
    then it counts the two apart and the two add up to what was
    discharged.

    SPEC.md: "The inventory identifies structurally discharged checks as
    well as solver checks."

    still passes if: the tool counted every entry as solver-discharged --
    the structural count is compared to the 2 entries a rule settled.
    """
    from prova import discharge

    findings = {
        "by-the-solver-1": discharge.Finding.proved_by_the_solver(),
        "by-the-solver-2": discharge.Finding.proved_by_the_solver(),
        "by-the-solver-3": discharge.Finding.proved_by_the_solver(),
        "by-a-rule-1": discharge.Finding.proved_by_a_rule("acyclic_calls"),
        "by-a-rule-2": discharge.Finding.proved_by_a_rule("acyclic_calls"),
    }
    aggregate = _verdict().Verdict.over(
        findings, _examples(ALL_EIGHT_PASSED), _checks()
    )
    counted = aggregate.published()["obligations"]

    assert counted["by"] == {"solver": 3, "structure": 2}, (
        f"WHAT: the aggregate counts {counted['by']} over 3 obligations a "
        "solver settled and 2 a rule of core-0 settled. "
        "WHY: a reader must be able to tell what rests on a solver's word "
        "from what rests on a rule of the profile. "
        "HOW: count each finding under the way it was discharged."
    )
    assert sum(counted["by"].values()) == counted["discharged"], (
        f"WHAT: the two ways of discharging add up to "
        f"{sum(counted['by'].values())} and {counted['discharged']} "
        "obligations were discharged. "
        "WHY: every discharged obligation was discharged one way or the "
        "other; a count that does not sum to the whole hides one. "
        "HOW: count both from the same findings."
    )


@pytest.mark.parametrize("worst", MOST_SERIOUS_FIRST)
def test_the_aggregate_carries_the_most_serious_thing_that_happened(worst):
    """Given obligations whose attempts ended in several ways, when the
    aggregate is read, then it carries the most serious of them.

    The case for 'completed' is the control: where nothing worse happened
    the aggregate says so, so a tool that always answered 'tool_failure'
    fails here.
    """
    if worst == "completed":
        pairs = (PROVED, PROVED)
    else:
        milder = MOST_SERIOUS_FIRST[MOST_SERIOUS_FIRST.index(worst) + 1 :]
        pairs = tuple(("unknown", status) for status in (worst,) + milder)

    aggregate = _aggregate(pairs, ALL_EIGHT_PASSED)

    assert aggregate.execution_status == worst, (
        f"WHAT: over attempts that ended as {[pair[1] for pair in pairs]} the "
        f"aggregate says {aggregate.execution_status!r}, not {worst!r}. "
        "WHY: a reader is told the worst thing that happened to the "
        "verification; reporting the commonest would hide a failure of this "
        "tool behind a list of ordinary results. "
        f"HOW: order the statuses as {list(MOST_SERIOUS_FIRST)} and take the "
        "first that occurred."
    )


def test_an_obligation_that_pairs_proved_with_a_stopped_attempt_is_refused():
    """Given a finding hand-built to say `proved` beside an attempt that
    timed out -- which no constructor of this tool builds -- when the
    aggregate is asked for, then it refuses loudly instead of counting it
    as discharged.

    Only a completed justified result may be `proved` (SPEC.md lines
    280-284). A pair like this is a defect in the caller, and an aggregate
    that quietly believed it would say `verified` over a proof that never
    finished.
    """
    from prova import discharge

    findings = {"o1": discharge.Finding("proved", "timed_out")}

    with pytest.raises(ValueError) as refusal:
        _verdict().Verdict.over(findings, _examples(ALL_EIGHT_PASSED), _checks())

    said = str(refusal.value)
    assert "o1" in said and "timed_out" in said, (
        f"WHAT: the refusal says {said!r}. "
        "WHY: the reader is the author of the caller, who needs the "
        "obligation and the pair that cannot be. "
        "HOW: name the identity and both words in the refusal."
    )


def test_an_example_run_that_misses_a_declared_example_is_refused():
    """Given a complete run that reports 7 outcomes for 8 declared
    examples, when it is built, then it refuses: a run that lost one
    example would otherwise be read as a run where every example passed.
    """
    verdict = _verdict()
    entries = [
        {"function": "valid-state", "ordinal": ordinal, "passed": True}
        for ordinal in range(7)
    ]

    with pytest.raises(ValueError) as refusal:
        verdict.ExamplesRun.of(entries, 8)

    said = str(refusal.value)
    assert "7" in said and "8" in said, (
        f"WHAT: the refusal says {said!r}. "
        "WHY: the reader needs both numbers to see which example went "
        "missing. "
        "HOW: name how many ran and how many the program declares."
    )


def test_the_static_check_evidence_cannot_be_built_for_a_refused_program():
    """Given a program the checker refused with 1 diagnostic, when the
    evidence that its static checks passed is asked for, then there is
    none; given a program it accepted, then there is.

    The aggregate takes that evidence as an argument, so a program whose
    static checks did not pass cannot have an aggregate computed for it at
    all: the third of the three conditions is kept by construction rather
    than by a branch somebody could forget.
    """
    verdict = _verdict()
    a_diagnostic = {"category": "type_mismatch", "reason": "fare is Int, not Bool"}

    assert verdict.StaticChecksPassed.of((a_diagnostic,)) is None, (
        "WHAT: evidence that the static checks passed was built for a program "
        "the checker refused. "
        "WHY: the word 'verified' rests on the static checks passing; "
        "evidence that can be built for a refused program is not evidence. "
        "HOW: build it only from an empty list of diagnostics."
    )
    passed = verdict.StaticChecksPassed.of(())
    assert passed is not None and passed.published() == {
        "passed": True,
        "diagnostics": 0,
    }, (
        f"WHAT: a program the checker accepted publishes {passed}. "
        "WHY: the answer says all three conditions of the word, and this is "
        "the third. "
        "HOW: publish the evidence beside the other two."
    )
