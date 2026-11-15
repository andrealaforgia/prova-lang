"""Laws the contract report obeys for any program, not only the examples
this repository ships.

Each program is built from a plan written here first: how many functions,
and what each of them writes in its two contract blocks. The plan is the
oracle -- it says which strength each block has, independently of how the
tool works it out.

LAW1 every block is recorded with the strength its own text has: absent is
     omitted, every clause the literal `true` is trivial, and one clause
     that is not the literal `true` is stated.
LAW2 the report names every declared function exactly once, in the order
     the program declares them.
LAW3 the report says the program states a contract exactly when at least
     one block of one function is stated.
LAW4 the counts partition the blocks: omitted, trivial and stated sum back
     to two per declared function and agree with the listed entries.

Drives the `prova` command over its JSON stdin/stdout surface, as the
other property tests here do. No imports from src/prova.
"""

from __future__ import annotations

import json
import subprocess

from hypothesis import given, settings
from hypothesis import strategies as st

# Every way a block can be written in core-0, with the strength a reader
# of that text writes down. The case is generated from this closed set,
# so every branch of the rule is built by construction rather than
# searched for.
REQUIRES_TEXTS = (
    ("omitted", ""),
    ("trivial", "(requires true)"),
    ("trivial", "(requires true true)"),
    ("stated", "(requires (> n 0))"),
    ("stated", "(requires true (> n 0))"),
    ("stated", "(requires false)"),
)
ENSURES_TEXTS = (
    ("omitted", ""),
    ("trivial", "(ensures true)"),
    ("trivial", "(ensures true true)"),
    ("stated", "(ensures (= result (* n 2)))"),
    ("stated", "(ensures true (= result (* n 2)))"),
    ("stated", "(ensures false)"),
)
FUNCTION_NAMES = ("twice-a", "twice-b", "twice-c")
BLOCKS = ("precondition", "postcondition")


def _function_text(name: str, requires: str, ensures: str) -> str:
    parts = [f"(defn {name}", "  (sig ((n Int)) -> Int ! pure)"]
    if requires:
        parts.append(f"  {requires}")
    if ensures:
        parts.append(f"  {ensures}")
    parts.append(f"  (examples (example ({name} 2) => 4))")
    parts.append("  (* n 2))")
    return "\n".join(parts)


def _program_of(plan: tuple) -> str:
    return "\n\n".join(
        _function_text(FUNCTION_NAMES[index], requires_text, ensures_text)
        for index, ((_, requires_text), (_, ensures_text)) in enumerate(plan)
    )


def _expected(plan: tuple) -> list:
    return [
        {
            "function": FUNCTION_NAMES[index],
            "precondition": requires_strength,
            "postcondition": ensures_strength,
        }
        for index, ((requires_strength, _), (ensures_strength, _)) in enumerate(plan)
    ]


def _report_of(plan: tuple) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps({"operation": "check", "source": _program_of(plan)}),
        capture_output=True,
        text=True,
        timeout=20.0,
    )
    answer = json.loads(proc.stdout)
    assert answer.get("status") == "completed", (
        f"the generated program was refused: {answer.get('status')!r} with "
        f"{answer.get('diagnostics')}. Every program this plan builds keeps "
        f"the rules of core-0:\n{_program_of(plan)}"
    )
    report = answer.get("contract_report")
    assert isinstance(report, dict), (
        f"the answer carries no contract report: keys {sorted(answer)}."
    )
    return report


plans = st.lists(
    st.tuples(st.sampled_from(REQUIRES_TEXTS), st.sampled_from(ENSURES_TEXTS)),
    min_size=1,
    max_size=len(FUNCTION_NAMES),
)


@given(plans)
@settings(max_examples=12, derandomize=True, deadline=None)
def test_every_block_is_recorded_with_the_strength_its_own_text_has(plan):
    """LAW1: absent reads omitted, all-`true` reads trivial, and a clause
    that is not `true` reads stated."""
    report = _report_of(tuple(plan))

    assert report.get("functions") == _expected(tuple(plan)), (
        f"the report records {report.get('functions')} for a program whose "
        f"blocks the plan wrote as {_expected(tuple(plan))}. A block is read "
        f"from its own text:\n{_program_of(tuple(plan))}"
    )


@given(plans)
@settings(max_examples=12, derandomize=True, deadline=None)
def test_the_report_names_every_declared_function_once_in_declaration_order(plan):
    """LAW2: one entry per declared function, in the order the program
    declares them."""
    report = _report_of(tuple(plan))

    named = [entry.get("function") for entry in report.get("functions") or []]
    declared = list(FUNCTION_NAMES[: len(plan)])
    assert named == declared, (
        f"the report names {named} and the program declares {declared}. "
        "Every function is recorded exactly once, in declaration order, so "
        "a reader can count them against the source."
    )


@given(plans)
@settings(max_examples=12, derandomize=True, deadline=None)
def test_the_program_states_a_contract_exactly_when_one_block_says_something(plan):
    """LAW3: the one field the Owner reads is true exactly when some block
    is stated."""
    report = _report_of(tuple(plan))

    some_block_states_something = any(
        strength == "stated"
        for (requires, ensures) in plan
        for strength in (requires[0], ensures[0])
    )
    assert report.get("states_a_contract") is some_block_states_something, (
        f"the report says states_a_contract="
        f"{report.get('states_a_contract')!r} for a program the plan wrote "
        f"with {'a stated' if some_block_states_something else 'no stated'} "
        f"block:\n{_program_of(tuple(plan))}"
    )


@given(plans)
@settings(max_examples=12, derandomize=True, deadline=None)
def test_the_counts_partition_the_blocks_of_the_declared_functions(plan):
    """LAW4: omitted, trivial and stated sum back to two blocks per
    declared function and agree with the listed entries."""
    report = _report_of(tuple(plan))
    totals = report.get("totals") or {}

    counted = {"omitted": 0, "trivial": 0, "stated": 0}
    for entry in _expected(tuple(plan)):
        for block in BLOCKS:
            counted[entry[block]] += 1
    assert totals.get("functions") == len(plan), (
        f"the totals count {totals.get('functions')!r} functions and the "
        f"program declares {len(plan)}."
    )
    assert totals.get("contracts") == 2 * len(plan), (
        f"the totals count {totals.get('contracts')!r} blocks and the "
        f"{len(plan)} declared functions have {2 * len(plan)}."
    )
    assert {word: totals.get(word) for word in counted} == counted, (
        f"the totals say {totals} and the plan wrote {counted}: a block is "
        "omitted, trivial or stated and nothing else, so the parts sum back "
        "to the whole."
    )
