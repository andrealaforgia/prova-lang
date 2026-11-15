"""Laws the answer about what a program owes obeys for any program in
the fragment, not only the two examples this repository ships.

Each program is built from a plan written here first -- what the function
asks for, what it promises and what it does -- and a reference model of
what that body answers is written beside it. The plan and the model are
the oracle: neither reads how the tool works anything out.

LAW1 whatever is answered proved is never contradicted by running the
     program: for inputs that meet what the function asks for, the tool's
     own evaluator never refuses the call for the promise it was proved
     to keep.
LAW2 whatever is answered disproved carries an input that really breaks
     the promise: replayed through the evaluator, that input is refused
     for exactly that promise.
LAW3 every obligation stands as one of the four results beside one of
     the seven execution statuses, the counts partition the list, and
     anything left unsettled says why.
LAW4 an obligation the translation does not cover comes back unknown
     with its reason, and never proved: multiplying two unknown numbers
     is executable core syntax and outside the fragment this tool
     automates.

Drives the `prova` command over its JSON stdin/stdout surface, as the
other property tests here do. No imports from src/prova.

Derandomised, and the laws that run over a closed grid draw one case per
cell, so the verdict does not depend on which cases Hypothesis happens to
draw.
"""

from __future__ import annotations

import json
import subprocess

from hypothesis import given, settings
from hypothesis import strategies as st

# SPEC.md lines 270-284: the four words a logical result may carry and
# the seven an execution status may carry. No word belongs to both.
LOGICAL_RESULTS = {"proved", "disproved", "unknown", "not_attempted"}
EXECUTION_STATUSES = {
    "completed",
    "unsupported",
    "timed_out",
    "cancelled",
    "resource_exhausted",
    "invalid_input",
    "tool_failure",
}

# What the generated function asks for, and the smallest whole number
# that meets it, so inputs are built to reach the case rather than
# filtered until they do.
ASKS = {
    "anything": (None, -50),
    "a positive number": ("(> n 0)", 1),
    "a number that is not negative": ("(>= n 0)", 0),
}

# What it promises about its answer.
PROMISES = {
    "nothing": None,
    "an answer that is not negative": "(>= result 0)",
    "a positive answer": "(> result 0)",
    "an answer at least as large as its input": "(>= result n)",
    "twice its input": "(= result (* n 2))",
}

# What it does, with a model of the value it answers written beside it.
BODIES = {
    "answers its input": ("n", lambda n: n),
    "adds one": ("(+ n 1)", lambda n: n + 1),
    "doubles": ("(* n 2)", lambda n: n * 2),
    "negates": ("(- 0 n)", lambda n: -n),
    "answers its input or zero": ("(if (> n 0) n 0)", lambda n: n if n > 0 else 0),
}

# A model of each promise, so what the program answers can be judged
# without asking the tool whether it kept it.
KEEPS = {
    "nothing": lambda n, answer: True,
    "an answer that is not negative": lambda n, answer: answer >= 0,
    "a positive answer": lambda n, answer: answer > 0,
    "an answer at least as large as its input": lambda n, answer: answer >= n,
    "twice its input": lambda n, answer: answer == n * 2,
}

# Plans whose promise is false for some whole number the function
# accepts, written out here so every case of LAW2 really is one the tool
# must disprove rather than one it happens to.
PROMISES_THAT_ARE_FALSE = (
    ("anything", "a positive answer", "answers its input"),
    ("anything", "an answer that is not negative", "answers its input"),
    ("anything", "an answer that is not negative", "negates"),
    ("anything", "a positive answer", "adds one"),
    ("anything", "an answer at least as large as its input", "doubles"),
    ("anything", "a positive answer", "answers its input or zero"),
)

# Bodies that multiply two numbers neither of which is known, which
# SPEC.md puts outside the fragment this tool automates, each with the
# value it answers at (2, 3) so the example the program declares is a
# true one and the only unsettled thing about it is its promise.
MULTIPLYING_TWO_UNKNOWNS = (
    ("(* n m)", 6),
    ("(* (+ n 1) m)", 9),
    ("(* n (* m m))", 18),
)

# Plans whose promise holds for every whole number the function accepts,
# written out here so LAW5 runs over cases that are true by construction
# rather than over whichever ones the tool happens to settle. They are
# also the positive control for LAW1: a tool that proved nothing at all
# would satisfy that law and fail every case of this one.
PROMISES_THAT_HOLD = (
    ("a positive number", "a positive answer", "answers its input"),
    (
        "a number that is not negative",
        "an answer that is not negative",
        "answers its input",
    ),
    ("anything", "twice its input", "doubles"),
    ("anything", "an answer at least as large as its input", "answers its input"),
    (
        "a number that is not negative",
        "an answer that is not negative",
        "answers its input or zero",
    ),
    ("anything", "nothing", "negates"),
    ("a positive number", "a positive answer", "adds one"),
)

THE_PROMISE = "body_postcondition:f:body"

_EVERY_PLAN = tuple(
    (asks, promise, body)
    for asks in sorted(ASKS)
    for promise in sorted(PROMISES)
    for body in sorted(BODIES)
)


def _ask(request: dict) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=60.0,
    )
    assert proc.returncode == 0, (
        f"the tool exited {proc.returncode} for {request.get('operation')!r} "
        f"instead of answering: {proc.stderr[-500:]!r}"
    )
    return json.loads(proc.stdout)


def _program(asks: str, promise: str, body: str) -> str:
    """The source of the one-function program the plan describes."""
    text, model = BODIES[body]
    smallest = ASKS[asks][1]
    lines = ["(defn f", "  (sig ((n Int)) -> Int ! pure)"]
    if ASKS[asks][0] is not None:
        lines.append(f"  (requires {ASKS[asks][0]})")
    if PROMISES[promise] is not None:
        lines.append(f"  (ensures {PROMISES[promise]})")
    lines.append(f"  (examples (example (f {smallest}) => {model(smallest)}))")
    lines.append(f"  {text})")
    return "\n".join(lines) + "\n"


def _entry(source: str, identity: str = THE_PROMISE) -> dict:
    answer = _ask({"operation": "verify", "source": source})
    assert answer["status"] == "completed", (
        f"the program was answered {answer['status']!r} instead of being "
        f"listed:\n{source}\n{answer}"
    )
    entries = answer["result"]["inventory"]["obligations"]
    for entry in entries:
        if entry["id"] == identity:
            return entry
    raise AssertionError(
        f"no obligation {identity!r} in {[e['id'] for e in entries]} "
        f"for:\n{source}"
    )


def _refusals(source: str, arguments: list) -> set:
    answer = _ask(
        {
            "operation": "evaluate",
            "source": source,
            "function": "f",
            "arguments": arguments,
        }
    )
    return {d.get("category") for d in (answer.get("diagnostics") or [])}


# How far past the smallest number a function accepts the law reaches:
# the first few, and distances far past any machine word, because Int is
# the mathematical integers here and a translation that quietly made it
# a machine number would agree with the evaluator only near zero.
THE_DISTANCES = (0, 1, 2, 41, 10**18, 10**30, 10**60)


@given(
    plan=st.sampled_from(_EVERY_PLAN),
    distance=st.one_of(
        st.sampled_from(THE_DISTANCES), st.integers(min_value=0, max_value=40)
    ),
    second=st.one_of(
        st.sampled_from(THE_DISTANCES), st.integers(min_value=0, max_value=40)
    ),
)
@settings(max_examples=25, deadline=None, derandomize=True)
def test_what_is_proved_is_never_contradicted_by_running_the_program(
    plan, distance, second
):
    """LAW1: given a program whose promise came back proved, when the
    same tool runs it over whole numbers it accepts -- the smallest ones
    and numbers far past any machine word -- then it never refuses the
    call for that promise."""
    asks, promise, body = plan
    source = _program(asks, promise, body)
    if _entry(source)["result"] != "proved":
        return

    smallest = ASKS[asks][1]
    model = BODIES[body][1]
    for n in (smallest + distance, smallest + second):
        assert KEEPS[promise](n, model(n)), (
            f"WHAT: the promise of {promise!r} came back proved and the "
            f"program {body!r} answers {model(n)} at {n}, which breaks it. "
            "WHY: a wrong 'proved' is the worst defect this tool can have. "
            f"HOW: the program was:\n{source}"
        )
        refused = _refusals(source, [str(n)])
        assert "postcondition_violation" not in refused, (
            f"WHAT: the promise of {promise!r} came back proved and running "
            f"the program at {n} is refused for that same promise. "
            "WHY: the solver and the evaluator read one language; the two "
            "disagreeing means one of them is wrong, and a reader was told "
            "the promise holds. "
            f"HOW: the program was:\n{source}"
        )


@given(plan=st.sampled_from(PROMISES_THAT_ARE_FALSE))
@settings(
    max_examples=len(PROMISES_THAT_ARE_FALSE), deadline=None, derandomize=True
)
def test_what_is_disproved_names_an_input_that_really_breaks_the_promise(plan):
    """LAW2: given a program whose promise is false for some whole number
    it accepts, when the Owner reads the answer, then it is disproved and
    the input it names is refused for that promise when it is run."""
    asks, promise, body = plan
    source = _program(asks, promise, body)
    entry = _entry(source)

    assert entry["result"] == "disproved", (
        f"WHAT: a promise of {promise!r} by a program that {body} is "
        f"answered {entry['result']!r}. "
        "WHY: a whole number this function accepts breaks that promise, and "
        "the Owner asked what this program owes. "
        f"HOW: the program was:\n{source}"
    )
    witness = entry.get("counterexample") or {}
    assert witness.get("function") == "f" and witness.get("arguments"), (
        f"WHAT: the disproof carries {witness}. "
        "WHY: SPEC.md requires a validated source-level witness; without the "
        "input, nothing can be reproduced. "
        f"HOW: the program was:\n{source}"
    )
    assert "postcondition_violation" in _refusals(source, witness["arguments"]), (
        f"WHAT: running the program over {witness['arguments']} is not "
        "refused for the promise the answer says it breaks. "
        "WHY: a witness that fails to replay yields unknown, not a disproof: "
        "SPEC.md forbids an invented one. "
        f"HOW: the program was:\n{source}"
    )


@given(plan=st.sampled_from(PROMISES_THAT_HOLD))
@settings(max_examples=len(PROMISES_THAT_HOLD), deadline=None, derandomize=True)
def test_a_promise_that_holds_everywhere_comes_back_proved(plan):
    """LAW5: given a program whose promise holds for every whole number
    it accepts, when the Owner asks what it owes, then that promise comes
    back proved."""
    asks, promise, body = plan
    source = _program(asks, promise, body)
    entry = _entry(source)

    assert entry["result"] == "proved", (
        f"WHAT: a program that {body} and promises {promise!r} of every "
        f"number it accepts is answered {entry['result']!r}. "
        "WHY: the Owner runs this to be told their promise is owed no "
        "longer; a tool that settles nothing is as useless as one that "
        "settles the wrong thing. "
        f"HOW: the program was:\n{source}"
    )
    assert entry["execution_status"] == "completed", (entry, source)


@given(plan=st.sampled_from(_EVERY_PLAN))
@settings(max_examples=25, deadline=None, derandomize=True)
def test_every_obligation_stands_as_one_result_beside_one_status(plan):
    """LAW3: given any program of the plan, when the Owner reads the
    answer, then each obligation carries one of the four results beside
    one of the seven statuses, anything unsettled says why, and the
    counts partition the list."""
    source = _program(*plan)
    answer = _ask({"operation": "verify", "source": source})
    inventory = answer["result"]["inventory"]
    entries = inventory["obligations"]

    for entry in entries:
        assert entry["result"] in LOGICAL_RESULTS, (entry, source)
        assert entry["execution_status"] in EXECUTION_STATUSES, (entry, source)
        if entry["result"] in ("unknown", "not_attempted"):
            assert str(entry.get("reason", "")).strip(), (
                f"WHAT: {entry['id']} is answered {entry['result']!r} with no "
                "reason beside it. "
                "WHY: the Owner reading an unsettled obligation has to learn "
                "whether their program is outside what this tool automates or "
                "whether something went wrong. "
                f"HOW: the program was:\n{source}"
            )

    totals = inventory["totals"]
    settled = [e for e in entries if e["result"] != "not_attempted"]
    assert totals["obligations"] == len(entries), (totals, source)
    assert totals["attempted"] == len(settled), (
        f"WHAT: the answer reports {totals['attempted']} attempted and "
        f"{len(settled)} of the {len(entries)} obligations carry a result "
        "something reached. "
        "WHY: the count of what was tried must be the number really tried, or "
        "a reader of the summary reads a different verdict from a reader of "
        f"the entries. HOW: the program was:\n{source}"
    )
    assert totals["attempted"] + totals["not_attempted"] == len(entries), (
        totals,
        source,
    )
    assert sum(totals["by_result"].values()) == len(entries), (
        f"WHAT: the counts by result {totals['by_result']} do not add up to "
        f"the {len(entries)} obligations listed. "
        "WHY: every obligation stands as exactly one result. "
        f"HOW: the program was:\n{source}"
    )


@given(
    multiplied=st.sampled_from(MULTIPLYING_TWO_UNKNOWNS),
    promise=st.sampled_from(["(>= result 0)", "(= result (* n 2))"]),
)
@settings(max_examples=6, deadline=None, derandomize=True)
def test_what_the_translation_does_not_cover_comes_back_unknown(
    multiplied, promise
):
    """LAW4: given a program multiplying two numbers neither of which is
    known, when the Owner asks what it owes, then its promise comes back
    unknown with the reason, and never proved."""
    body, at_two_and_three = multiplied
    source = (
        "(defn f\n"
        "  (sig ((n Int) (m Int)) -> Int ! pure)\n"
        f"  (ensures {promise})\n"
        f"  (examples (example (f 2 3) => {at_two_and_three}))\n"
        f"  {body})\n"
    )
    entry = _entry(source)

    assert entry["result"] == "unknown", (
        f"WHAT: a promise about {body} is answered {entry['result']!r}. "
        "WHY: SPEC.md puts general Int multiplication outside the automation "
        "required here; an obligation remaining outside the fragment returns "
        "unknown with that reason and must not be translated unsoundly. "
        f"HOW: the program was:\n{source}"
    )
    assert str(entry.get("reason", "")).strip(), (
        f"WHAT: {entry['id']} is answered unknown with no reason beside it. "
        "WHY: the Owner has to learn that their program is outside what this "
        "tool automates, not that something went wrong. "
        f"HOW: the program was:\n{source}"
    )
