"""Shared fixtures for feature F9: sources that use something the
`core-0` profile does not have, the nearly identical sources that use
only what it does have, and the fourteen preserved counterexamples in
`evidence/cases/`.

Every out-of-profile source here has an in-profile twin that differs
only in the one construct under observation, so a test that observes a
refusal is always paired with a control that observes the same program
answered without that refusal. Without the twins a tool that refused
every source would pass.

The expected status of a twin is pinned, never its diagnostic category:
the categories of an in-profile mistake belong to the rules that own
them, and F9 must not freeze another rule's wording.

Not itself a test module (no `test_` prefix); pytest will not collect it.
The helpers here drive only the `prova` command's real JSON
stdin/stdout surface. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
from dataclasses import dataclass

# The status and the category the tool answers with when the source uses
# a construct `core-0` does not have. Part of the tool's published
# response vocabulary -- the manifest lists them -- not internal symbols.
UNSUPPORTED_STATUS = "unsupported"
UNSUPPORTED_CATEGORY = "unsupported_construct"

# The status the tool already answers with when the source is a program
# `core-0` defines but a rule of `core-0` refuses it.
INVALID_PROGRAM_STATUS = "invalid_program"

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
EVIDENCE_CASES = REPO_ROOT / "evidence" / "cases"


# --- the in-profile program every source below is a copy of ---------------

WELL_FORMED = """\
(defn f
  (sig ((n Int)) -> Int ! pure)
  (examples (example (f 1) => 1))
  n)
"""

BODY_LINE = 4


def with_body(expression: str) -> str:
    """The in-profile program with `expression` as its body, which stands
    on line 4 of the source."""
    return WELL_FORMED.replace("  n)\n", f"  {expression})\n")


def declared_with(word: str) -> str:
    """The in-profile program whose declaration word is `word` instead of
    `defn`. The word stands on line 1."""
    return WELL_FORMED.replace("(defn ", f"({word} ", 1)


# --- the closed family of constructs `core-0` does not have ---------------

@dataclass(frozen=True)
class OutOfProfileSource:
    """One source that uses a construct `core-0` does not have: the
    source, the words the refusal must say so a reader knows what to
    repair, the line the construct stands on, and the in-profile twin
    that differs only in that construct."""

    source: str
    naming: tuple[str, ...]
    line: int
    twin: str
    twin_status: str = "completed"


OUT_OF_PROFILE: dict[str, OutOfProfileSource] = {
    "division": OutOfProfileSource(
        source=with_body("(/ n 1)"),
        naming=("division", "/"),
        line=BODY_LINE,
        twin=with_body("(* n 1)"),
    ),
    "a decimal literal": OutOfProfileSource(
        source=with_body("1.5"),
        naming=("decimal", "1.5"),
        line=BODY_LINE,
        twin=with_body("1"),
    ),
    "a decimal literal in an example": OutOfProfileSource(
        source=WELL_FORMED.replace("=> 1)", "=> 1.0)"),
        naming=("decimal", "1.0"),
        line=3,
        twin=WELL_FORMED,
    ),
    "a text literal": OutOfProfileSource(
        source=with_body('"ok"'),
        naming=("text", '"ok"'),
        line=BODY_LINE,
        twin=with_body("1"),
    ),
    "a trailing top-level expression": OutOfProfileSource(
        source=WELL_FORMED + "\n(f 1)\n",
        naming=("top-level expression", "f"),
        line=6,
        twin=WELL_FORMED,
    ),
    "the declaration word 'defspec'": OutOfProfileSource(
        source=declared_with("defspec"),
        naming=("defspec", "declaration"),
        line=1,
        twin=WELL_FORMED,
    ),
    "the declaration word 'fn'": OutOfProfileSource(
        source=declared_with("fn"),
        naming=("fn", "declaration"),
        line=1,
        twin=WELL_FORMED,
    ),
    "the declaration word 'trust'": OutOfProfileSource(
        source=declared_with("trust"),
        naming=("trust", "declaration"),
        line=1,
        twin=WELL_FORMED,
    ),
    "the declaration word 'module'": OutOfProfileSource(
        source=declared_with("module"),
        naming=("module", "declaration"),
        line=1,
        twin=WELL_FORMED,
    ),
}


# --- sources that stay exactly as they are answered today -----------------

# A misspelled declaration word is not a use of an out-of-profile
# feature: it is a word the reader cannot place, and it keeps the
# refusal the reader already gives it.
MISSPELLED_DECLARATION_WORD = "(deftypo T (record (x Int)))\n"

# An in-profile program that breaks an in-profile rule: it must keep the
# status and the category its own rule owns.
UNBOUND_NAME_IN_PROFILE = with_body("(+ n missing-name)")

SHIPPED_PROGRAMS = ("examples/hour-clock.prova", "conformance/add-one.prova")


def shipped_source(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


# --- the fourteen preserved counterexamples -------------------------------

def top_level_forms(text: str) -> list[str]:
    """Every top-level parenthesised form of `text`, in source order.

    Counts parentheses only, which is enough for the preserved files:
    they carry no comment and no text literal containing a parenthesis.
    """
    forms: list[str] = []
    depth = 0
    start = None
    for index, character in enumerate(text):
        if character == "(":
            if depth == 0:
                start = index
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0 and start is not None:
                forms.append(text[start : index + 1])
                start = None
    return forms


def without_its_last_form(text: str) -> str:
    """`text` with its last top-level form removed."""
    forms = top_level_forms(text)
    return " ".join(forms[:-1])


@dataclass(frozen=True)
class PreservedCase:
    """One of the fourteen files kept in `evidence/cases/`: the words its
    refusal must say, and how to write the same case using only what
    `core-0` has.

    The file itself is provenance and is never edited; the adaptation is
    derived from its text by the recorded substitutions, so a file that
    changed under the test would stop matching them and be reported.
    """

    naming: tuple[str, ...]
    substitutions: tuple[tuple[str, str], ...] = ()
    drop_last_form: bool = True
    adapted_status: str = INVALID_PROGRAM_STATUS

    def source(self, name: str) -> str:
        return (EVIDENCE_CASES / f"{name}.prova").read_text(encoding="utf-8")

    def adaptation(self, name: str) -> str:
        text = self.source(name)
        if self.drop_last_form:
            text = without_its_last_form(text)
        for old, new in self.substitutions:
            if old not in text:
                raise AssertionError(
                    f"WHAT: the preserved case {name!r} no longer contains "
                    f"{old!r}, so its recorded adaptation cannot be derived. "
                    "WHY: the adaptation is derived from the file so that the "
                    "control stays a copy of the case it controls. "
                    "HOW: the files in evidence/cases/ are provenance and are "
                    "not edited; restore the file, or record the substitution "
                    "that replaces this one."
                )
            text = text.replace(old, new)
        return text


_TO_WHOLE_NUMBERS = (("Decimal", "Int"), ("3.0", "3"), ("1.0", "1"))

PRESERVED_CASES: dict[str, PreservedCase] = {
    "boolean-operands": PreservedCase(naming=("top-level expression", "choose")),
    "builtin-hides-name": PreservedCase(naming=("top-level expression", "choose")),
    "builtin-hides-type": PreservedCase(naming=("top-level expression", "choose")),
    "constant-division": PreservedCase(
        naming=("decimal", "1.0"),
        substitutions=_TO_WHOLE_NUMBERS + (("(/ 3 3)", "(* 3 3)"), ("=> 1)", "=> 9)")),
        adapted_status="completed",
    ),
    "exact-division": PreservedCase(
        naming=("decimal", "3.0"),
        substitutions=_TO_WHOLE_NUMBERS
        + (("(/ amount 3)", "(* amount 1)"), ("=> 1)", "=> 3)")),
        adapted_status="completed",
    ),
    "false-contract": PreservedCase(
        naming=("top-level expression", "wrong"), adapted_status="completed"
    ),
    "false-contract-plus-unencoded": PreservedCase(
        naming=("top-level expression", "wrong"), adapted_status="completed"
    ),
    "hidden-operator-type": PreservedCase(naming=("top-level expression", "choose")),
    "hidden-unknown-name": PreservedCase(naming=("top-level expression", "choose")),
    "inexact-division": PreservedCase(
        naming=("decimal", "3.0"),
        substitutions=_TO_WHOLE_NUMBERS
        + (("(/ amount 3)", "(* amount 1)"), ("=> 1)", "=> 3)")),
        adapted_status="completed",
    ),
    "missing-call-precondition": PreservedCase(
        naming=("defspec", "declaration"),
        substitutions=(("(defspec ", "(defn "),),
        adapted_status="completed",
    ),
    "named-call-arity": PreservedCase(naming=("top-level expression", "choose")),
    "non-bool-condition": PreservedCase(naming=("top-level expression", "choose")),
    "valid-builtin": PreservedCase(
        naming=("text", '"ok"'), substitutions=(('"ok"', "1"),)
    ),
}


# --- running the command --------------------------------------------------

@dataclass(frozen=True)
class ToolRun:
    """One run of the `prova` command: everything the operating system
    and the command reported, kept so a crash stays visible."""

    exit_code: int
    stdout: str
    stderr: str

    def response(self) -> dict:
        try:
            return json.loads(self.stdout)
        except (json.JSONDecodeError, ValueError):
            raise AssertionError(
                "the command's answer is not valid JSON, so a caller cannot read "
                f"an outcome from it; it exited {self.exit_code} and printed "
                f"{self.stdout!r} on standard output and {self.stderr[-600:]!r} on "
                "standard error. A source the tool cannot read must come back as "
                "one JSON response, never as a crash."
            ) from None


def run(request: dict) -> ToolRun:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=30.0,
    )
    return ToolRun(proc.returncode, proc.stdout, proc.stderr)


def check(source: str) -> ToolRun:
    return run({"prova": "i1", "operation": "check", "source": source})


def discover() -> ToolRun:
    return run({"prova": "i1", "operation": "discover"})


# --- reading a refusal back -----------------------------------------------

def categories(response: dict) -> list[str]:
    return [d.get("category") for d in response.get("diagnostics") or []]


def assert_unsupported_naming(run_result: ToolRun, *, naming, why: str) -> str:
    """The source was refused with the unsupported status, with exactly
    one out-of-profile refusal, and that refusal says it is outside this
    profile and names the construct. Returns the sentence."""
    response = run_result.response()
    assert response.get("status") == UNSUPPORTED_STATUS, (
        f"{why} was answered {response.get('status')!r}, not "
        f"{UNSUPPORTED_STATUS!r}: {response}. A source using something core-0 "
        "does not have is outside the profile, which is a different answer from "
        "a program of the profile that breaks one of its rules."
    )
    refusals = [
        d
        for d in response.get("diagnostics") or []
        if d.get("category") == UNSUPPORTED_CATEGORY
    ]
    assert len(refusals) == 1, (
        f"expected exactly 1 {UNSUPPORTED_CATEGORY!r} refusal for {why}, got "
        f"{len(refusals)}: {response}. One out-of-profile construct is one "
        "defect with one repair; report it once."
    )
    reason = refusals[0].get("reason", "")
    for word in (*naming, "core-0", "unsupported"):
        assert word in reason, (
            f"the refusal for {why} does not say {word!r}, so a reader cannot "
            f"tell which construct is outside the profile: {reason!r}. Name the "
            "construct and say that core-0 does not have it."
        )
    return reason


def assert_refused_at(run_result: ToolRun, *, line: int, why: str) -> None:
    """The refusal points at the line the construct stands on."""
    response = run_result.response()
    location = (response.get("diagnostics") or [{}])[0].get("location") or {}
    assert location.get("line") == line, (
        f"the refusal for {why} is placed at {location or 'nowhere'} but the "
        f"construct stands on line {line}: {response}. A refusal must say where "
        "it happened, so a reader can go to that line."
    )


def assert_answered_without_the_unsupported_status(
    run_result: ToolRun, *, expected_status: str, why: str
) -> None:
    """The in-profile twin is answered, and never as out-of-profile: the
    unsupported answer is given to the construct, not to everything."""
    response = run_result.response()
    assert response.get("status") == expected_status, (
        f"{why} was answered {response.get('status')!r} instead of "
        f"{expected_status!r}: {response}. It uses only what core-0 has, so the "
        "profile boundary has nothing to say about it."
    )
    assert UNSUPPORTED_CATEGORY not in categories(response), (
        f"{why} carries an out-of-profile refusal: {response}. It uses only "
        "what core-0 has; refusing it as unsupported would make the new answer "
        "a refusal of everything."
    )
