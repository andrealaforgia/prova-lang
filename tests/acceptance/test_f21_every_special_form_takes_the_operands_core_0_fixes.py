"""A form of core-0 carries what core-0 fixes it carries, and nothing more.

SPEC.md fixes the shape of every special form: `if` has a condition, a
then-branch and an else-branch, `let` has its bindings and one body, a
field selector reads one value, `deftype` names one type and gives one
body. A source that writes another operand into one of them is not
writing that form, and a tool that reads the operands it knows and drops
the rest answers about a program the source does not write -- which is
how `(if true n n (missing n))` came back as a program whose every
obligation was discharged, with a call to a function that does not exist
standing in its body.

So every form that fixes its own number of operands is refused where it
stands when it carries another one, before any tree is built: nothing can
be checked, run or discharged about a form the tool did not read whole.

The table below is over every special form of this profile. The two the
review named are `if` and a field selector; the others are here so that a
form which stops refusing is caught by the same table.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

import json
import subprocess

import pytest

A = "=>"

# A record to read a field of, declared only by the cases that need one.
A_RECORD = "(deftype Clock (record (hr Int)))"


def _a_function_whose_body_is(body: str, declared: str = "") -> str:
    return (
        f"{declared}(defn f\n"
        f"  (sig ((n Int)) -> Int ! pure)\n"
        f"  (examples (example (f 0) {A} 0))\n"
        f"  {body})\n"
    )


def _a_function_reading(body: str) -> str:
    return (
        f"{A_RECORD}\n(defn f\n"
        f"  (sig ((c Clock)) -> Int ! pure)\n"
        f"  (examples (example (f (Clock 1)) {A} 1))\n"
        f"  {body})\n"
    )


# form => (the form named in the source, one operand too many, one too few)
#
# `match`, `requires`, `ensures` and `examples` are not here: each takes
# as many clauses as the source writes, so neither of them has an operand
# too many. `match` with no clause at all is the too-few case of its own
# rule and is covered by the F7 and F8 families already.
TOO_MANY_AND_TOO_FEW = {
    "if": (
        _a_function_whose_body_is("(if true n n (missing n))"),
        _a_function_whose_body_is("(if true n)"),
    ),
    "let": (
        _a_function_whose_body_is("(let ((x 1)) n (missing n))"),
        _a_function_whose_body_is("(let ((x 1)))"),
    ),
    "a field selector": (
        _a_function_reading("(.hr c (missing c))"),
        _a_function_reading("(.hr)"),
    ),
    "deftype": (
        _a_function_whose_body_is("n", f"{A_RECORD[:-1]} extra)\n"),
        _a_function_whose_body_is("n", "(deftype Clock)\n"),
    ),
    "sig": (
        f"(defn f (sig ((n Int)) -> Int ! pure extra) (examples (example (f 0) {A} 0)) n)\n",
        f"(defn f (sig ((n Int)) -> Int) (examples (example (f 0) {A} 0)) n)\n",
    ),
    "example": (
        f"(defn f (sig ((n Int)) -> Int ! pure) (examples (example (f 0) {A} 0 1)) n)\n",
        f"(defn f (sig ((n Int)) -> Int ! pure) (examples (example (f 0) {A})) n)\n",
    ),
    "defn": (
        _a_function_whose_body_is("n") .replace("  n)\n", "  n (missing n))\n"),
        "(defn f)\n",
    ),
}


def _answer(operation: str, source: str) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps({"operation": operation, "source": source}),
        capture_output=True,
        text=True,
        timeout=60.0,
    )
    assert proc.returncode == 0, (
        f"WHAT: the command exited {proc.returncode} instead of answering. "
        "WHY: a malformed source is refused, never a run that stops. "
        f"HOW: read its error output: {proc.stderr[-400:]!r}"
    )
    return json.loads(proc.stdout)


def _refusal_of(source: str, label: str) -> dict:
    answer = _answer("check", source)

    assert answer.get("status") == "invalid_program", (
        f"WHAT: {label} was answered {answer.get('status')!r}. "
        "WHY: core-0 fixes the operands of this form, so a source that "
        "writes another one is not writing it; a tool that reads the "
        "operands it knows and drops the rest answers about a program "
        "nobody wrote. "
        f"HOW: the source was:\n{source}\nthe answer was: {answer}"
    )
    diagnostics = answer.get("diagnostics") or []
    assert len(diagnostics) == 1, (
        f"WHAT: {label} is refused with {len(diagnostics)} diagnostics. "
        "WHY: one defect of shape is one refusal, named once. "
        f"HOW: inspect them: {diagnostics}"
    )
    entry = diagnostics[0]
    assert entry.get("category") == "syntax", (
        f"WHAT: {label} is refused under the category "
        f"{entry.get('category')!r}. "
        "WHY: a form whose operands do not match what core-0 fixes is a "
        "defect of shape, under the category the manifest publishes for one. "
        f"HOW: inspect the refusal: {entry}"
    )
    place = entry.get("location") or {}
    assert place.get("line", 0) >= 1 and place.get("column", 0) >= 1, (
        f"WHAT: {label} is refused at {place}. "
        "WHY: a reader of the refusal must have a line and a column to open. "
        f"HOW: inspect the refusal: {entry}"
    )
    return entry


@pytest.mark.parametrize("form", sorted(TOO_MANY_AND_TOO_FEW))
def test_a_form_with_one_operand_too_many_is_refused_where_it_stands(form):
    """Given a program whose only defect is one operand too many in a
    form core-0 fixes, when the Owner checks it, then it is refused
    where that form stands, under the published category for a defect of
    shape.

    still passes if: the tool refused every program -- the control below
    requires the same programs without the extra operand to be accepted.
    """
    too_many, _ = TOO_MANY_AND_TOO_FEW[form]
    _refusal_of(too_many, f"a {form!r} form with one operand too many")


@pytest.mark.parametrize("form", sorted(TOO_MANY_AND_TOO_FEW))
def test_a_form_with_one_operand_too_few_is_refused_where_it_stands(form):
    """Given a program whose only defect is one operand missing from a
    form core-0 fixes, when the Owner checks it, then it is refused where
    that form stands, under the same published category."""
    _, too_few = TOO_MANY_AND_TOO_FEW[form]
    _refusal_of(too_few, f"a {form!r} form with one operand too few")


def test_an_extra_operand_is_not_quietly_discharged():
    """Given the program the review found -- an `if` carrying a fourth
    operand that calls a function nobody declared -- when the Owner
    verifies it, then nothing about it is called verified.

    This is the whole point of the rule: that fourth operand was read by
    nothing, so the body the tool discharged was not the body the source
    wrote, and the answer said the word over a program containing a call
    that cannot be resolved.
    """
    source = _a_function_whose_body_is("(if true n n (missing n))")
    answer = _answer("verify", source)

    assert answer.get("status") == "invalid_program", (
        f"WHAT: the program the review found is answered "
        f"{answer.get('status')!r}. "
        "WHY: it contains a call to a function nobody declared, inside an "
        "operand core-0 does not give to an 'if'. "
        f"HOW: the answer was: {answer}"
    )
    assert "verified" not in json.dumps(answer).lower(), (
        f"WHAT: the answer about a malformed program uses the word "
        f"'verified': {answer}. "
        "WHY: nothing was shown about a program that was never read whole. "
        "HOW: refuse the form before anything is discharged."
    )


def test_the_same_forms_written_as_core_0_fixes_them_are_accepted():
    """Control. Given the same forms with exactly the operands core-0
    fixes, when the Owner checks them, then every one is accepted -- so
    the table above is about the extra operand and not about the form.
    """
    accepted = {
        "if": _a_function_whose_body_is("(if true n n)"),
        "let": _a_function_whose_body_is("(let ((x 1)) n)"),
        "a field selector": _a_function_reading("(.hr c)"),
        "deftype": _a_function_whose_body_is("n", f"{A_RECORD}\n"),
    }
    for form, source in accepted.items():
        answer = _answer("check", source)
        assert answer.get("status") == "completed", (
            f"WHAT: a well-formed {form!r} is answered "
            f"{answer.get('status')!r}. "
            "WHY: the rule is about an operand core-0 does not give the "
            "form, and must leave every form the profile does have alone. "
            f"HOW: the source was:\n{source}\nthe answer was: {answer}"
        )
