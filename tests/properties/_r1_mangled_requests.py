"""The mangled requests R1's fuzz sends, and the way it sends them.

Not a test module (no `test_` prefix); pytest will not collect it.

The corpus is built from a fixed seed and from the programs this
repository ships, so the same requests are sent on every run: a fuzz
that found a crash once and cannot be re-run has not caught a
regression.

How the requests are sent: the console script's own entry point is
called in this process with standard input and standard output replaced,
so the exit code read back is the one the command would exit with and
the text read back is the bytes it would print. Thousands of requests
through thousands of subprocesses would cost minutes; the acceptance
tests keep one real `prova` subprocess per family of mangled request,
where the cost of a process is paid once.
"""

from __future__ import annotations

import io
import json
import pathlib
import random
import sys
from dataclasses import dataclass

import prova.__main__ as command_line

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

SEED = 20261115

OPERATIONS = (
    "check",
    "examples",
    "evaluate",
    "verify",
    "discover",
    "parse",
    "format",
    "build",
    "not-an-operation",
)

# Every kind of JSON value a client can put in a field, including the
# ones no field of any request holds.
WRONG_KINDS = (None, 7, -1, 3.5, True, False, "", "x", [], ["x"], [7], {}, {"a": 1})

FIELDS = ("operation", "source", "function", "arguments", "prova")


@dataclass(frozen=True)
class Answer:
    exit_code: int
    stdout: str
    crash: BaseException | None


def ask(request: object) -> Answer:
    """One request through the command's own entry point."""
    captured = io.StringIO()
    saved_out, saved_in = sys.stdout, sys.stdin
    sys.stdout = captured
    sys.stdin = io.StringIO(json.dumps(request))
    try:
        command_line.main()
        code = 0
    except SystemExit as leaving:
        code = leaving.code if isinstance(leaving.code, int) else 0
    except BaseException as escaped:  # noqa: BLE001 - the fuzz exists to see these
        return Answer(-1, captured.getvalue(), escaped)
    finally:
        sys.stdout, sys.stdin = saved_out, saved_in
    return Answer(code, captured.getvalue(), None)


def shipped_programs() -> dict[str, str]:
    spec = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    start = spec.index("## Core conformance example")
    opening = spec.index("```", start)
    body = spec.index("\n", opening) + 1
    return {
        "hour-clock": (REPO_ROOT / "examples" / "hour-clock.prova").read_text(
            encoding="utf-8"
        ),
        "add-one": (REPO_ROOT / "conformance" / "add-one.prova").read_text(
            encoding="utf-8"
        ),
        "reservation": spec[body : spec.index("```", body)],
    }


def token_boundaries(text: str) -> list[int]:
    """Where one token of the text ends and the next begins."""
    boundaries = [0]
    for index, character in enumerate(text):
        if character in "()" or character.isspace():
            boundaries.append(index)
            boundaries.append(index + 1)
    boundaries.append(len(text))
    return sorted(set(boundaries))


def nested(depth: int) -> str:
    return "(" * depth + "1" + ")" * depth


def nested_program(depth: int) -> str:
    body = "(not " * (depth - 1) + "true" + ")" * (depth - 1)
    return (
        "(defn deeply-nested\n"
        "  (sig () -> Bool ! pure)\n"
        "  (examples (example (deeply-nested) => true))\n"
        f"  {body})\n"
    )


def corpus() -> list[tuple[str, object]]:
    """Every mangled request the suite sends, each with the words that
    say what was done to it."""
    cases: list[tuple[str, object]] = []
    programs = shipped_programs()

    for name, text in programs.items():
        for index in range(len(text)):
            cases.append(
                (f"{name} with character {index} deleted",
                 {"operation": "examples", "source": text[:index] + text[index + 1 :]})
            )
            cases.append(
                (f"{name} cut off after character {index}",
                 {"operation": "check", "source": text[:index]})
            )
        for index in token_boundaries(text):
            cases.append(
                (f"{name} cut off at the token boundary at {index}",
                 {"operation": "examples", "source": text[:index]})
            )
            cases.append(
                (f"{name} cut off at the token boundary at {index}, verified",
                 {"operation": "verify", "source": text[:index]})
            )

    clock = programs["hour-clock"]
    for operation in OPERATIONS:
        for wrong in WRONG_KINDS:
            cases.append(
                (f"{operation} with a source of the wrong kind",
                 {"operation": operation, "source": wrong})
            )
            cases.append(
                (f"{operation} with a function of the wrong kind",
                 {"operation": operation, "source": clock, "function": wrong,
                  "arguments": ["(Clock 1)"]})
            )
            cases.append(
                (f"{operation} with arguments of the wrong kind",
                 {"operation": operation, "source": clock, "function": "step",
                  "arguments": wrong})
            )
            cases.append(
                (f"{operation} with one argument of the wrong kind",
                 {"operation": operation, "source": clock, "function": "step",
                  "arguments": ["(Clock 1)", wrong]})
            )
            cases.append(
                (f"an operation that is {wrong!r}",
                 {"operation": wrong, "source": clock})
            )

    for operation in OPERATIONS:
        cases.append((f"{operation} with no other field", {"operation": operation}))
        cases.append(
            (f"{operation} with no source",
             {"operation": operation, "function": "step", "arguments": []})
        )
        cases.append(
            (f"{operation} with no function",
             {"operation": operation, "source": clock, "arguments": []})
        )
        cases.append(
            (f"{operation} with no arguments",
             {"operation": operation, "source": clock, "function": "initial"})
        )
    cases.append(("a request with no fields at all", {}))

    for wrong in WRONG_KINDS:
        cases.append((f"a request that is {wrong!r}", wrong))

    for depth in (1, 2, 50, 127, 128, 129, 200, 450, 700, 1000, 2000, 10000):
        cases.append(
            (f"a bare text nested {depth} deep",
             {"operation": "check", "source": nested(depth)})
        )
        if depth >= 5:
            cases.append(
                (f"a program nested {depth} deep",
                 {"operation": "examples", "source": nested_program(depth)})
            )
        cases.append(
            (f"an argument nested {depth} deep",
             {"operation": "evaluate", "source": clock, "function": "valid-state",
              "arguments": ["(" * depth + "Clock" + ")" * depth]})
        )

    cases.extend(_shuffled_fields())
    return cases


def _shuffled_fields() -> list[tuple[str, object]]:
    """Requests whose fields hold each other's values, drawn from one
    fixed seed so the same ones are sent every run."""
    rolling = random.Random(SEED)
    clock = shipped_programs()["hour-clock"]
    values = list(WRONG_KINDS) + [clock, "step", ["(Clock 1)", "(Tick)"], "check"]
    drawn = []
    for draw in range(500):
        request = {
            field: rolling.choice(values)
            for field in FIELDS
            if rolling.random() < 0.8
        }
        drawn.append((f"a request drawn from seed {SEED}, draw {draw}", request))
    return drawn
