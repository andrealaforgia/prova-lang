"""Laws the word `verified` obeys for any program, not only the two this
repository ships.

Each program is built from a plan written here first, so what the answer
ought to say is known before the answer is read.

LAW8  whenever an answer says a program is verified, every obligation it
      lists is proved and every example the program declares passes when
      the tool is asked to run them -- which is a second, separate answer,
      not the one under observation.
LAW9  a program whose every promise is provable and whose examples hold
      does come back verified, so LAW8 is not a law about a tool that
      says `verified` for nothing at all.
LAW10 a program carrying one promise this tool cannot translate is never
      verified, and the obligations of the functions beside it keep the
      results they had.

Drives the `prova` command over its JSON stdin/stdout surface, as the
other property tests here do. No imports from src/prova.
"""

from __future__ import annotations

import json
import subprocess

from hypothesis import given, settings
from hypothesis import strategies as st

A = "=>"

# A promise this tool cannot translate: SPEC.md keeps the automated
# fragment linear, so the product of two numbers neither of which is
# known is left outside it. Its own example is about two literals, so
# that entry is settled as usual: the function is a mixture on purpose.
THE_PROMISE_IT_CANNOT_TRANSLATE = f"""(defn product
  (sig ((n Int) (m Int)) -> Int ! pure)
  (requires (and (>= n 0) (>= m 0)))
  (ensures (>= result 0))
  (examples (example (product 2 3) {A} 6))
  (* n m))
"""

THE_UNTRANSLATABLE_FUNCTION = "product"

_plans = st.lists(
    st.tuples(st.integers(min_value=0, max_value=3), st.integers(min_value=0, max_value=5)),
    min_size=1,
    max_size=2,
)


def _function(index: int, constant: int, argument: int) -> str:
    """One function that adds a known number to a number at least zero,
    and promises an answer at least that known number. True of every
    input of its declared type, and its example is true of the program."""
    name = f"add-{index}"
    return (
        f"(defn {name}\n"
        f"  (sig ((n Int)) -> Int ! pure)\n"
        f"  (requires (>= n 0))\n"
        f"  (ensures (>= result {constant}))\n"
        f"  (examples (example ({name} {argument}) {A} {argument + constant}))\n"
        f"  (+ n {constant}))"
    )


def render_program(plans, with_the_untranslatable: bool = False) -> str:
    written = [
        _function(index, constant, argument)
        for index, (constant, argument) in enumerate(plans)
    ]
    source = "\n\n".join(written) + "\n"
    if with_the_untranslatable:
        source += "\n" + THE_PROMISE_IT_CANNOT_TRANSLATE
    return source


def _ask(operation: str, source: str) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps({"operation": operation, "source": source}),
        capture_output=True,
        text=True,
        timeout=60.0,
    )
    assert proc.returncode == 0, (
        f"WHAT: the command exited {proc.returncode} for {operation!r}. "
        "WHY: every request is answered. "
        f"HOW: read its error output: {proc.stderr[-400:]!r}"
    )
    answer = json.loads(proc.stdout)
    assert answer.get("status") == "completed", (
        f"WHAT: {operation!r} answered {answer.get('status')!r} for a program "
        "this test generated to be read and checked. "
        f"WHY: the law is about a program the tool accepts. "
        f"HOW: the program was:\n{source}\nthe answer was: {answer}"
    )
    return answer


def _entries(answer: dict) -> list:
    return ((answer.get("result") or {}).get("inventory") or {}).get(
        "obligations"
    ) or []


def _aggregate(answer: dict, source: str) -> dict:
    aggregate = answer.get("aggregate")
    assert isinstance(aggregate, dict), (
        f"WHAT: the verify answer carries no aggregate: {sorted(answer)}. "
        "WHY: every completed verify answer says where the program as a whole "
        "stands. "
        f"HOW: the program was:\n{source}"
    )
    return aggregate


@settings(derandomize=True, max_examples=5, deadline=None)
@given(plans=_plans, carries_the_untranslatable=st.booleans())
def test_a_program_called_verified_has_every_obligation_proved_and_every_example_passing(
    plans, carries_the_untranslatable
):
    """LAW8. Given any generated program, when the answer says it is
    verified, then every obligation it lists is proved and a separate run
    of its declared examples passes every one of them."""
    source = render_program(plans, carries_the_untranslatable)
    answer = _ask("verify", source)
    aggregate = _aggregate(answer, source)
    if aggregate["result"] != "verified":
        return

    not_proved = [
        (entry["id"], entry["result"])
        for entry in _entries(answer)
        if entry.get("result") != "proved"
    ]
    assert not not_proved, (
        f"WHAT: a program called verified lists {not_proved}. "
        "WHY: the word stands for a complete inventory, all discharged; an "
        "entry that is not proved is part of the program that was not shown. "
        f"HOW: the program was:\n{source}"
    )

    ran = (_ask("examples", source).get("result") or {}).get("examples") or []
    assert ran, f"no example was run for:\n{source}"
    did_not_pass = [
        (entry["function"], entry["ordinal"])
        for entry in ran
        if entry.get("passed") is not True
    ]
    assert not did_not_pass, (
        f"WHAT: a program called verified has examples that do not pass: "
        f"{did_not_pass}. "
        "WHY: the word rests on passing examples, and this run of them is a "
        "separate answer from the one that said the word. "
        f"HOW: the program was:\n{source}"
    )


@settings(derandomize=True, max_examples=5, deadline=None)
@given(plans=_plans)
def test_a_program_whose_every_promise_holds_does_come_back_verified(plans):
    """LAW9. Given a generated program every promise of which is true of
    every input of its declared types, and whose examples hold, when the
    Owner verifies it, then it comes back verified.

    The positive control for LAW8: without it, a tool that never said the
    word would obey LAW8 perfectly.
    """
    source = render_program(plans)
    answer = _ask("verify", source)
    aggregate = _aggregate(answer, source)

    assert aggregate["result"] == "verified", (
        f"WHAT: a program whose every promise holds comes back "
        f"{aggregate['result']!r}, saying {aggregate.get('reason')!r}. "
        "WHY: every obligation of this program is provable in the fragment "
        "this tool declares and every example of it is true, so the word is "
        "owed. "
        f"HOW: the program was:\n{source}"
    )


@settings(derandomize=True, max_examples=5, deadline=None)
@given(plans=_plans)
def test_one_promise_it_cannot_translate_withholds_the_word_and_nothing_else(plans):
    """LAW10. Given a generated program with one function promising
    something about the product of two unknown numbers, when the Owner
    verifies it, then the program is not verified and every obligation of
    the other functions is still proved."""
    source = render_program(plans, with_the_untranslatable=True)
    answer = _ask("verify", source)
    aggregate = _aggregate(answer, source)
    entries = _entries(answer)

    assert aggregate["result"] == "not_verified", (
        f"WHAT: a program with a promise this tool cannot translate comes "
        f"back {aggregate['result']!r}. "
        "WHY: an obligation left outside the fragment is one the program was "
        "not shown to meet. "
        f"HOW: the program was:\n{source}"
    )
    beside_it = [
        (entry["id"], entry["result"])
        for entry in entries
        if entry.get("function") != THE_UNTRANSLATABLE_FUNCTION
    ]
    assert beside_it, f"no obligation stands beside the untranslatable one:\n{source}"
    assert all(result == "proved" for _, result in beside_it), (
        f"WHAT: the obligations of the functions beside the untranslatable "
        f"one came back {beside_it}. "
        "WHY: SPEC.md: no unsupported function may erase unrelated "
        "obligations. "
        f"HOW: the program was:\n{source}"
    )
