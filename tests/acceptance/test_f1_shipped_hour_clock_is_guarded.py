"""Acceptance tests for F1: the hour clock this repository ships is guarded
by the suite. The Owner's one command shows that the shipped clock still
checks with no diagnostics, still runs every example it declares, and still
walks the whole dial; that a copy with the wrap at 12 taken out is reported
as a failure while the shipped file is left untouched; and that a run which
cannot find the shipped file fails with a missing-file error rather than
skipping.

The reservation example's half of the same outcome is already proved by
tests this change leaves alone: its clean check by
test_s5_b1_unmodified_source_accepted_with_no_errors, its declared examples
and a wrong copy by test_s2_int_examples_pass_and_wrong_copy_fails_end_to_end,
and its six-row transition table by test_s1_b1_step_six_row_table.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys

import pytest

import _hour_clock_fixtures as clock

# The number of examples the request says the shipped clock declares.
DECLARED_EXAMPLES_IN_THE_REQUEST = 8

COPIES_WITHOUT_THE_WRAP = [
    pytest.param(clock.clock_without_the_wrap, id="wrap-gone-from-the-step"),
    pytest.param(
        clock.clock_without_the_wrap_or_its_promise, id="wrap-gone-from-step-and-promise"
    ),
]


def test_the_shipped_hour_clock_checks_clean_and_runs_every_example_it_declares():
    """Given the hour clock this repository ships, when the Owner checks it
    and runs its declared examples, then the check completes with no
    diagnostic at all, and every example written in the file is reported,
    each one passing."""
    source = clock.shipped_clock_source()
    declared_in_the_file = source.count("(example ")

    checked = clock.check(source)
    examples = clock.declared_examples(source)

    assert checked.get("status") == "completed", (
        f"WHAT: checking the shipped hour clock did not complete: {checked}. "
        "WHY: the Owner is promised that the shipped clock still checks. "
        f"HOW: run the check on {clock.CLOCK_RELATIVE_PATH} and repair the "
        "program or the promise it breaks."
    )
    assert checked.get("diagnostics") == [], (
        f"WHAT: checking the shipped hour clock reported {checked.get('diagnostics')}. "
        "WHY: the promise is a check with no diagnostics at all, not a check that "
        "merely completes. "
        f"HOW: repair {clock.CLOCK_RELATIVE_PATH} until the check reports none."
    )

    reported = (examples.get("result") or {}).get("examples") or []
    assert len(reported) == declared_in_the_file, (
        f"WHAT: the file writes {declared_in_the_file} examples but "
        f"{len(reported)} were reported. "
        "WHY: the promise is that every declared example is run, not a sample. "
        f"HOW: compare the `(example ...)` forms in {clock.CLOCK_RELATIVE_PATH} "
        f"with the reported list: {reported}"
    )
    assert declared_in_the_file == DECLARED_EXAMPLES_IN_THE_REQUEST, (
        f"WHAT: the shipped clock now declares {declared_in_the_file} examples, "
        f"not the {DECLARED_EXAMPLES_IN_THE_REQUEST} the Owner was promised. "
        "WHY: an example silently added or removed changes what the suite guards. "
        "HOW: restore the declared examples, or agree the new number with the "
        "Owner and change DECLARED_EXAMPLES_IN_THE_REQUEST with it."
    )
    failed = [e for e in reported if e.get("passed") is not True]
    assert failed == [], (
        f"WHAT: {len(failed)} of the {len(reported)} declared examples did not pass: "
        f"{failed}. "
        "WHY: the Owner is promised that every example the shipped clock declares "
        "still passes. "
        f"HOW: each entry names its function, its arguments, the expected value and "
        f"the value actually produced; repair {clock.CLOCK_RELATIVE_PATH}."
    )


def test_the_clock_at_hour_12_ticks_round_to_hour_1_and_the_tick_is_accepted():
    """Given the shipped clock showing hour 12, when a tick is applied, then
    the clock shows hour 1 and the tick is accepted."""
    response = clock.tick(clock.shipped_clock_source(), 12)

    assert response.get("diagnostics") == [], (
        f"WHAT: ticking from hour 12 reported {response.get('diagnostics')}. "
        "WHY: a tick from hour 12 is promised to be accepted, not refused. "
        f"HOW: repair the wrap at 12 in {clock.CLOCK_RELATIVE_PATH}."
    )
    hour, accepted = clock.hour_and_acceptance(response)
    assert (hour, accepted) == (1, True), (
        f"WHAT: a tick from hour 12 gave hour {hour}, accepted={accepted}, "
        "not hour 1, accepted. "
        "WHY: the clock wraps round at 12; hour 13 is not on the dial. "
        f"HOW: repair the wrap at 12 in {clock.CLOCK_RELATIVE_PATH}."
    )


@pytest.mark.parametrize("hour", sorted(clock.DIAL))
def test_every_hour_on_the_dial_ticks_to_the_next_hour_and_is_accepted(hour):
    """Given the shipped clock showing each hour from 1 to 12 in turn, when
    a tick is applied, then the clock shows the next hour on the dial, 2 to
    12 and then 1 again, and every one of those ticks is accepted."""
    response = clock.tick(clock.shipped_clock_source(), hour)

    assert response.get("diagnostics") == [], (
        f"WHAT: ticking from hour {hour} reported {response.get('diagnostics')}. "
        "WHY: every hour from 1 to 12 is on the dial, so every tick from one of "
        "them is promised to be accepted. "
        f"HOW: repair `step` in {clock.CLOCK_RELATIVE_PATH}."
    )
    observed = clock.hour_and_acceptance(response)
    assert observed == (clock.DIAL[hour], True), (
        f"WHAT: a tick from hour {hour} gave hour {observed[0]}, "
        f"accepted={observed[1]}, not hour {clock.DIAL[hour]}, accepted. "
        "WHY: the Owner is promised the hours 2 to 12 and then 1, each accepted. "
        f"HOW: repair `step` in {clock.CLOCK_RELATIVE_PATH}."
    )


@pytest.mark.parametrize("remove_the_wrap", COPIES_WITHOUT_THE_WRAP)
def test_a_copy_without_the_wrap_at_12_is_reported_as_a_failure(
    tmp_path, remove_the_wrap
):
    """Given a separate copy of the shipped clock on disk with the wrap at
    12 taken out, when that copy is checked and its declared examples are
    run, then the copy still checks with no diagnostic but exactly one
    declared example is reported as failing, the one that ticks from hour
    12, and a tick from hour 12 is refused; the shipped file keeps the same
    bytes throughout and still passes afterwards."""
    digest_before = clock.clock_digest()
    shipped = clock.shipped_clock_source()

    copy_path = tmp_path / "hour-clock-without-the-wrap.prova"
    copy_path.write_text(remove_the_wrap(shipped), encoding="utf-8")
    copied = copy_path.read_text(encoding="utf-8")
    assert copied != shipped, "the copy must differ from the shipped file"

    checked = clock.check(copied)
    assert checked.get("status") == "completed" and checked.get("diagnostics") == [], (
        f"WHAT: the copy without the wrap did not check cleanly: {checked}. "
        "WHY: the copy must break only the wrap at 12; a copy that fails to "
        "check would make the rest of this test pass for the wrong reason. "
        "HOW: repair the copy the fixture builds in "
        "tests/acceptance/_hour_clock_fixtures.py."
    )

    reported = (clock.declared_examples(copied).get("result") or {}).get("examples") or []
    failing = [e for e in reported if e.get("passed") is not True]
    assert len(failing) == 1, (
        f"WHAT: {len(failing)} of the {len(reported)} declared examples of the copy "
        f"failed, not exactly one: {failing}. "
        "WHY: taking out the wrap at 12 breaks the tick from hour 12 and nothing "
        "else; if the suite reported no failure it would not be guarding the "
        "shipped clock at all. "
        "HOW: read the reported entries and the copy the fixture builds."
    )
    assert failing[0]["function"] == "step" and failing[0]["arguments"] == [
        "(Clock 12)",
        "(Tick)",
    ], (
        f"WHAT: the failing example is {failing[0]}, not the tick from hour 12. "
        "WHY: the wrap at 12 is what the copy removed, so that is the example "
        "that must be reported as failing. "
        "HOW: read the copy the fixture builds and the reported entries."
    )

    refused = clock.tick(copied, 12)
    assert refused.get("diagnostics"), (
        f"WHAT: a tick from hour 12 on the copy without the wrap was not refused: "
        f"{refused}. "
        "WHY: without the wrap the clock would show hour 13, which is not on the "
        "dial, so the attempt must be reported, not accepted. "
        "HOW: read the response above."
    )
    still_ticks = clock.tick(copied, 11)
    assert clock.hour_and_acceptance(still_ticks) == (12, True), (
        "WHAT: the copy without the wrap no longer ticks from hour 11 to hour 12. "
        "WHY: the copy must differ from the shipped clock at hour 12 only. "
        "HOW: repair the copy the fixture builds."
    )

    assert clock.clock_digest() == digest_before, (
        f"WHAT: {clock.CLOCK_RELATIVE_PATH} changed while this test ran. "
        "WHY: the copy is written to a temporary directory; the shipped file is "
        "never edited. "
        "HOW: restore it with `git checkout -- " + clock.CLOCK_RELATIVE_PATH + "`."
    )
    assert clock.shipped_clock_source() == shipped
    assert clock.hour_and_acceptance(clock.tick(shipped, 12)) == (1, True), (
        "WHAT: the shipped clock no longer ticks from hour 12 to hour 1 after the "
        "copy was run. "
        "WHY: running a copy must leave the shipped clock exactly as it was. "
        "HOW: restore the shipped file and re-run."
    )


def test_a_run_that_cannot_find_the_clock_file_fails_instead_of_skipping(tmp_path):
    """Given a tree in which the shipped clock file is absent, when these
    same hour-clock tests run over that tree, then every one of them is
    reported as a failure naming the missing file and none is skipped; and
    given the same tree with the file put back, the same run passes, so the
    failures are the absent file and not a broken harness."""
    tree = tmp_path / "tree-without-the-clock"
    suite = tree / "tests" / "acceptance"
    suite.mkdir(parents=True)
    for module in (clock.__file__, __file__):
        shutil.copyfile(module, suite / pathlib.Path(module).name)
    copied_test_file = suite / pathlib.Path(__file__).name

    all_tests = _collected(copied_test_file, tree)
    without_this_one = _collected(copied_test_file, tree, "-k", "not cannot_find")
    assert all_tests - without_this_one == 1 and without_this_one >= 4, (
        f"WHAT: selecting the hour-clock tests of the copied tree gave "
        f"{without_this_one} of {all_tests} tests. "
        "WHY: this test runs the others over a tree with no clock file; it must "
        "deselect itself and still leave the rest of them to run. "
        "HOW: check the -k expression against the test names in this file."
    )

    missing = _run(copied_test_file, tree, "-k", "not cannot_find")
    assert missing.returncode != 0, (
        "WHAT: the hour-clock tests passed over a tree with no clock file. "
        "WHY: with nothing to read they prove nothing about the shipped clock, so "
        "they must fail. "
        f"HOW: read the run: {missing.stdout}"
    )
    assert _counted("failed", missing.stdout) == without_this_one, (
        f"WHAT: {_counted('failed', missing.stdout)} of {without_this_one} hour-clock "
        f"tests failed over a tree with no clock file. "
        "WHY: every one of them reads the shipped file, so every one must fail. "
        f"HOW: read the run: {missing.stdout}"
    )
    assert _counted("skipped", missing.stdout) == 0, (
        f"WHAT: {_counted('skipped', missing.stdout)} hour-clock test(s) were "
        "skipped over a tree with no clock file. "
        "WHY: a skipped test reports no problem; a missing shipped example is a "
        "problem the Owner must see. "
        f"HOW: remove the skip: the fixture must raise instead. Run: {missing.stdout}"
    )
    assert clock.CLOCK_RELATIVE_PATH in missing.stdout, (
        "WHAT: the failures do not name the file that is missing. "
        "WHY: the Owner must be told which file to restore. "
        f"HOW: read the run: {missing.stdout}"
    )

    shutil.copyfile(clock.clock_path(), _restored(tree))
    restored = _run(copied_test_file, tree, "-k", "hour_12")
    assert restored.returncode == 0 and _counted("passed", restored.stdout) == 1, (
        "WHAT: with the clock file put back, the same selected run did not pass. "
        "WHY: without this control the failures above could come from the copied "
        "harness rather than from the absent file. "
        f"HOW: read the run: {restored.stdout}"
    )


def _restored(tree: pathlib.Path) -> pathlib.Path:
    path = clock.clock_path(tree)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _run(test_file: pathlib.Path, tree: pathlib.Path, *selection: str):
    return subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-q", "--tb=line",
         "-p", "no:cacheprovider", *selection],
        cwd=tree,
        capture_output=True,
        text=True,
        timeout=120.0,
    )


def _collected(test_file: pathlib.Path, tree: pathlib.Path, *selection: str) -> int:
    outcome = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-q", "--collect-only",
         "-p", "no:cacheprovider", *selection],
        cwd=tree,
        capture_output=True,
        text=True,
        timeout=120.0,
    )
    assert outcome.returncode == 0, f"collecting the copied tests failed: {outcome.stdout}"
    # "5 tests collected" with nothing deselected, "4/5 tests collected" with.
    found = re.search(r"(?:(\d+)/)?(\d+) tests? collected", outcome.stdout)
    assert found, f"no collected count in: {outcome.stdout}"
    return int(found.group(1) or found.group(2))


def _counted(word: str, output: str) -> int:
    found = re.search(rf"(\d+) {word}\b", output)
    return int(found.group(1)) if found else 0
