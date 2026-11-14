"""Shared fixtures for the shipped hour clock's acceptance tests: where the
shipped example program lives, how a run that cannot find it refuses, the
two wrap-removed copies, and the `prova` command runner.

Not itself a test module (no `test_` prefix); imported by
test_f1_shipped_hour_clock_is_guarded. Drives only the installed `prova`
command over its JSON stdin/stdout surface, as `_reservation_fixtures` does
for the reservation example. No imports from src/prova.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CLOCK_RELATIVE_PATH = "examples/hour-clock.prova"

# The dial the request states: hour 1 ticks to 2, on to hour 11 ticking to
# 12, and hour 12 back round to 1. Written out by hand so that every
# expected hour comes from the request, never from the clock source the
# tests put under observation.
DIAL = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 11: 12, 12: 1}

# The wrap at 12, exactly as the shipped `step` writes it. It appears twice
# in the shipped file: once in the promise `step` makes about its result,
# once in the body that produces it. Each copy below removes one or both.
_WRAP = "(if (= (.hr current) 12) 1 (+ (.hr current) 1))"
_BODY_WITH_WRAP = f"(Clock {_WRAP})"
_BODY_WITHOUT_WRAP = "(Clock (+ (.hr current) 1))"
_PROMISE_WITH_WRAP = f"(= (.hr (.state result))\n       {_WRAP})"
_PROMISE_WITHOUT_WRAP = "(= (.hr (.state result))\n       (+ (.hr current) 1))"


def clock_path(root: pathlib.Path = REPO_ROOT) -> pathlib.Path:
    return root.joinpath(*CLOCK_RELATIVE_PATH.split("/"))


def shipped_clock_source(root: pathlib.Path = REPO_ROOT) -> str:
    """The hour clock program this repository ships, read from disk.

    A missing or renamed file raises here, so a run that cannot find the
    shipped program fails and is never quietly skipped.
    """
    path = clock_path(root)
    if not path.is_file():
        raise FileNotFoundError(
            f"WHAT: the shipped example program {CLOCK_RELATIVE_PATH} is missing "
            f"from {root}; nothing was read. "
            "WHY: these tests exist to show that the hour clock this repository "
            "ships still checks and still runs its declared examples; with no "
            "file to read they prove nothing about it, so the run fails here "
            "instead of passing or skipping. "
            f"HOW: restore the file with `git checkout -- {CLOCK_RELATIVE_PATH}`; "
            "if it was renamed on purpose, change CLOCK_RELATIVE_PATH in "
            "tests/acceptance/_hour_clock_fixtures.py to the new name."
        )
    return path.read_text(encoding="utf-8")


def clock_digest(root: pathlib.Path = REPO_ROOT) -> str:
    shipped_clock_source(root)  # the one place a missing shipped file refuses
    return hashlib.sha256(clock_path(root).read_bytes()).hexdigest()


def _replace_once(source: str, old: str, new: str) -> str:
    assert source.count(old) == 1, (
        f"WHAT: expected exactly one occurrence of {old!r} in the shipped clock, "
        f"found {source.count(old)}. "
        "WHY: the copies these tests build must differ from the shipped file in "
        "the wrap at 12 and in nothing else; a different count means the fixture "
        "no longer describes the shipped program. "
        "HOW: re-read examples/hour-clock.prova and update the fixture text in "
        "tests/acceptance/_hour_clock_fixtures.py to match it."
    )
    return source.replace(old, new, 1)


def clock_without_the_wrap(source: str) -> str:
    """The same program with the wrap at 12 taken out of what `step` does,
    leaving the promise `step` makes about its result as shipped."""
    return _replace_once(source, _BODY_WITH_WRAP, _BODY_WITHOUT_WRAP)


def clock_without_the_wrap_or_its_promise(source: str) -> str:
    """The same program with the wrap at 12 taken out of what `step` does
    and out of the promise it makes, so no promise mentions the wrap."""
    without_body = clock_without_the_wrap(source)
    return _replace_once(without_body, _PROMISE_WITH_WRAP, _PROMISE_WITHOUT_WRAP)


def run_prova(request: dict) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure: stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response: {proc.stdout!r}")


def check(source: str) -> dict:
    return run_prova({"prova": "i1", "operation": "check", "source": source})


def declared_examples(source: str) -> dict:
    return run_prova({"prova": "i1", "operation": "examples", "source": source})


def tick(source: str, hour: int) -> dict:
    return run_prova(
        {
            "prova": "i1",
            "operation": "evaluate",
            "source": source,
            "function": "step",
            "arguments": [f"(Clock {hour})", "(Tick)"],
        }
    )


def hour_and_acceptance(response: dict) -> tuple[int, bool]:
    """The hour and the accepted flag reported in `(Outcome (Clock N) true)`."""
    value = ((response.get("result") or {}).get("value")) or ""
    assert value.startswith("(Outcome (Clock ") and value.endswith(")"), (
        f"WHAT: the reported outcome {value!r} is not an outcome of the hour clock. "
        "WHY: the test reads the hour and the accepted flag out of it. "
        f"HOW: inspect the whole response: {response}"
    )
    inner = value[len("(Outcome ") : -1]
    state, accepted = inner.rsplit(" ", 1)
    return int(state[len("(Clock ") : -1]), {"true": True, "false": False}[accepted]
