"""The two premises the structural discharge rests on, as laws over
generated programs rather than as an argument on paper.

Two of the five kinds of obligation are not sent to a solver at all.
They are settled by a rule of the profile, and these laws put that rule
under test with the tool's own evaluator as the oracle.

LAW6 every clause of a contract is defined for every value of the
     declared types: whatever the arguments, running the function
     answers a value or refuses it for a contract it does not keep, and
     never fails inside the tool. That is what "the contract is defined
     for every typed input" means where it can be observed.
LAW7 a program the checker accepted ends: run over values of its
     declared types, it never exhausts the evaluation limit. The
     programs here are of 3 functions calling one another in a chain and
     nest 6 forms deep at most, which is the bound this law is claimed
     within.

Neither law is a proof. Each is a search for a counterexample over the
programs the plan writes, and each would fail loudly on a profile that
admitted a partial operation or a cycle.

Drives the `prova` command over its JSON stdin/stdout surface, as the
other property tests here do. No imports from src/prova.
"""

from __future__ import annotations

import json
import subprocess

from hypothesis import given, settings
from hypothesis import strategies as st

# What the tool may answer about a program it accepted and ran: a value,
# or a refusal of a contract that program does not keep. Anything else
# means a clause could not be worked out at all.
REFUSALS_OF_A_CONTRACT = {"precondition_violation", "postcondition_violation"}

# How deep a run may go before the tool refuses to go on. A program of
# this plan never reaches it; a program that did would be a cycle the
# checker should have refused.
TOO_DEEP = "evaluation_depth_exceeded"

ASKED_OF_THE_INPUT = (
    "(> (.amount b) 0)",
    "(= b (Box 1))",
    "(and (>= (.amount b) 0) (<= (.amount b) 10))",
    "(not (< (.amount b) 0))",
    "(or (> (.amount b) 5) (< (.amount b) 5))",
)

PROMISED_OF_THE_ANSWER = (
    "(> (.amount result) 0)",
    "(= (.amount result) (+ (.amount b) 1))",
    "(not (= result b))",
    "(or (> (.amount result) 0) (<= (.amount result) 0))",
)

# Numbers at the edges of what a program can be given, and far past any
# machine word, because Int is the mathematical integers here.
THE_EDGES = (0, 1, -1, 2, -2, 10, 11, -10, 10**30, -(10**30), 10**60)


def _program(asked: str, promised: str) -> str:
    """A chain of 3 functions over a record, the outermost carrying the
    contract under test. The declared example is a true one: shifting
    (Box 1) answers (Box 2), which meets every clause of the plan."""
    return (
        "(deftype Box (record (amount Int)))\n\n"
        "(defn carried\n"
        "  (sig ((b Box)) -> Int ! pure)\n"
        "  (examples (example (carried (Box 1)) => 1))\n"
        "  (.amount b))\n\n"
        "(defn raised\n"
        "  (sig ((b Box)) -> Int ! pure)\n"
        "  (examples (example (raised (Box 1)) => 2))\n"
        "  (+ (carried b) 1))\n\n"
        "(defn shift\n"
        "  (sig ((b Box)) -> Box ! pure)\n"
        f"  (requires {asked})\n"
        f"  (ensures {promised})\n"
        "  (examples (example (shift (Box 1)) => (Box 2)))\n"
        "  (Box (raised b)))\n"
    )


def _run(source: str, amount: int) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(
            {
                "operation": "evaluate",
                "source": source,
                "function": "shift",
                "arguments": [f"(Box {amount})"],
            }
        ),
        capture_output=True,
        text=True,
        timeout=60.0,
    )
    assert proc.returncode == 0, (
        f"the tool exited {proc.returncode} instead of answering for "
        f"(Box {amount}): {proc.stderr[-400:]!r}"
    )
    return json.loads(proc.stdout)


@given(
    asked=st.sampled_from(ASKED_OF_THE_INPUT),
    promised=st.sampled_from(PROMISED_OF_THE_ANSWER),
    amount=st.one_of(
        st.sampled_from(THE_EDGES), st.integers(min_value=-(10**12), max_value=10**12)
    ),
)
@settings(max_examples=25, deadline=None, derandomize=True)
def test_every_contract_clause_is_defined_for_every_value_of_its_type(
    asked, promised, amount
):
    """LAW6: given a function whose contract reads its input and its
    answer, when it is run over any whole number at all, then the tool
    answers a value or refuses a contract, and never fails inside
    itself."""
    source = _program(asked, promised)
    answer = _run(source, amount)

    assert answer["status"] == "completed", (
        f"WHAT: running the function over (Box {amount}) is answered "
        f"{answer['status']!r}. "
        "WHY: every clause of this contract is built from total operations "
        "of the profile, so it has a value at every input; a status other "
        "than completed means one of them could not be worked out. "
        f"HOW: the program was:\n{source}\n{answer}"
    )
    categories = {d.get("category") for d in (answer.get("diagnostics") or [])}
    unexpected = sorted(categories - REFUSALS_OF_A_CONTRACT)
    assert not unexpected, (
        f"WHAT: running the function over (Box {amount}) reports "
        f"{unexpected}. "
        "WHY: a contract that is defined everywhere can be kept or broken, "
        "and nothing else; any other refusal is a clause that had no value. "
        f"HOW: the program was:\n{source}\n{answer}"
    )
    assert bool(answer.get("result")) != bool(categories), (
        f"WHAT: running over (Box {amount}) answers "
        f"{answer.get('result')} beside {sorted(categories)}. "
        "WHY: a call either answers a value or is refused for a contract it "
        "does not keep; both at once, or neither, leaves the reader with no "
        f"outcome. HOW: the program was:\n{source}\n{answer}"
    )


@given(
    asked=st.sampled_from(ASKED_OF_THE_INPUT),
    promised=st.sampled_from(PROMISED_OF_THE_ANSWER),
    amount=st.one_of(
        st.sampled_from(THE_EDGES), st.integers(min_value=-(10**12), max_value=10**12)
    ),
)
@settings(max_examples=25, deadline=None, derandomize=True)
def test_a_program_the_checker_accepted_ends(asked, promised, amount):
    """LAW7: given a chain of 3 functions the checker accepted, when it
    is run over any whole number at all, then the run ends rather than
    exhausting the limit on how deep a run may go."""
    source = _program(asked, promised)
    answer = _run(source, amount)

    categories = {d.get("category") for d in (answer.get("diagnostics") or [])}
    assert TOO_DEEP not in categories, (
        f"WHAT: running the chain over (Box {amount}) exhausts the limit on "
        "how deep a run may go. "
        "WHY: the calls a core-0 program can reach are acyclic, which is why "
        "a function is said to end structurally; a program of 3 calls that "
        "runs out of depth would mean that rule does not hold. "
        f"HOW: the program was:\n{source}\n{answer}"
    )
    assert answer["status"] != "resource_exhausted", (
        f"WHAT: running the chain over (Box {amount}) is answered "
        "resource_exhausted. "
        "WHY: this program is 3 calls deep and nests 6 forms; a budget "
        "passed here would mean the run did not end for a reason this law "
        f"is about. HOW: the program was:\n{source}\n{answer}"
    )
