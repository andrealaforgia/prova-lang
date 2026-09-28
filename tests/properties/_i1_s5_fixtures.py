"""Shared fixtures for I1.S5 property tests: whole-program `check`, two
hand-built hidden-defect variants (a Bool-arithmetic type error inside
`step`'s Reserve/Release accepted arms, and an unbound name in `initial`'s
body), their layout renderings, and their minimally corrected counterparts.

Not a test module (no `test_` prefix); pytest will not collect it.
"""

from __future__ import annotations

from _prova_client import SPEC_ORACLE_SHA, load_reservation_source_at, run_prova

# Runtime evaluation categories introduced by earlier stories (I1.S3, I1.S4).
# A `check` diagnostic reporting a static defect must not be one of these:
# nothing in `check` runs the program, so nothing it reports can be a
# runtime verdict.
EVALUATION_CATEGORIES = {
    "precondition_violation",
    "call_precondition_violation",
    "postcondition_violation",
    "malformed_value",
    "ill_typed_value",
}


def protected_source() -> str:
    return load_reservation_source_at(SPEC_ORACLE_SHA)


def run_check(source: str) -> tuple[int, dict | None, str, str]:
    request = {"prova": "i1", "operation": "check", "source": source}
    return run_prova(request)


def diagnostic_categories(response: dict) -> set[str]:
    return {d.get("category") for d in (response.get("diagnostics") or [])}


def assert_accepted(returncode, response, stdout, stderr) -> None:
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("operation") == "check", response
    assert response.get("status") == "completed", (
        f"expected whole-program acceptance, got: {response}"
    )
    assert not response.get("diagnostics"), (
        f"acceptance carried diagnostics: {response}"
    )
    claim = response.get("claim") or {}
    assert claim.get("kind") == "static_check", (
        f"expected a static_check claim, got: {claim}"
    )


def assert_rejected_as_invalid_program(returncode, response, stdout, stderr) -> set[str]:
    """Assert `check` rejected the source with a status distinct from
    `unsupported`/`invalid_input`/`tool_failure`, i.e. attributable to a
    genuine static defect in an otherwise well-formed, fully-supported
    program -- not a parser/grammar refusal or a malformed request.
    Returns the diagnostic categories for further inspection."""
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("operation") == "check", response
    assert response.get("status") == "invalid_program", (
        f"expected status invalid_program, got: {response}"
    )
    assert not response.get("result"), f"rejection carried a result: {response}"
    categories = diagnostic_categories(response)
    assert categories, f"rejection carried no diagnostics: {response}"
    assert categories.isdisjoint(EVALUATION_CATEGORIES), (
        f"a static rejection reported a runtime evaluation category: {categories}"
    )
    return categories


def line_col(text: str, index: int) -> tuple[int, int]:
    """1-indexed (line, column) of `index` within `text`, counting only
    newline characters -- independent of any tokenizer or reader."""
    prefix = text[:index]
    line = prefix.count("\n") + 1
    last_newline = prefix.rfind("\n")
    column = index - last_newline
    return line, column


def render(source: str, blank_lines: int, indent_spaces: int) -> str:
    """Prepend `blank_lines` empty lines, then add `indent_spaces` leading
    spaces to every nonblank line. A blank line stays blank (no indent
    added to nothing)."""
    lines = source.split("\n")
    widened = [(" " * indent_spaces + line) if line.strip() else line for line in lines]
    return ("\n" * blank_lines) + "\n".join(widened)


def location_of(response: dict, category_filter: set[str] | None = None) -> tuple[int, int]:
    """Extract the (line, column) the response's diagnostics attribute to
    the offending site. Per the I1 change plan, every diagnostic carries a
    location with line/column (and a structural path)."""
    diagnostics = response.get("diagnostics") or []
    if category_filter is not None:
        diagnostics = [d for d in diagnostics if d.get("category") in category_filter]
    assert diagnostics, f"no diagnostics to extract a location from: {response}"
    location = diagnostics[0].get("location") or {}
    line = location.get("line")
    column = location.get("column")
    assert isinstance(line, int) and isinstance(column, int), (
        f"diagnostic location missing an integer line/column: {diagnostics[0]}"
    )
    return line, column


# --- Reserve-branch hidden type error (I1.S5.P2 / I1.S5.P3) ---------------

RESERVE_OLD = "(Outcome (Reservation (+ (.reserved current) 1)) true)"
RESERVE_BUG_MARKER = "(+ true 1)"
RESERVE_BUG = (
    "(Outcome (Reservation (if (= (.reserved current) 1) "
    f"{RESERVE_BUG_MARKER} (+ (.reserved current) 1))) true)"
)
RESERVE_FIX = (
    "(Outcome (Reservation (if (= (.reserved current) 1) "
    "(+ (.reserved current) 1) (+ (.reserved current) 1))) true)"
)

# Declared examples that pass through the Reserve accepted arm: only
# (0, Reserve). The (2, Reserve) example takes the rejected arm. Neither
# reaches the injected nested `if`'s `true`-branch, which only fires when
# `(.reserved current) = 1` -- a fresh valid input never in step's own
# examples, though present in SPEC's six-row transition table.
RESERVE_DECLARED_INPUTS = [0, 2]
RESERVE_FRESH_INPUT = 1


def reserve_bug_source() -> str:
    source = protected_source()
    assert source.count(RESERVE_OLD) == 1
    return source.replace(RESERVE_OLD, RESERVE_BUG, 1)


def reserve_fix_source() -> str:
    source = protected_source()
    assert source.count(RESERVE_OLD) == 1
    return source.replace(RESERVE_OLD, RESERVE_FIX, 1)


def reserve_bug_hits_branch(count: int) -> bool:
    """Independent re-derivation of whether a given Reserve input reaches
    the Reserve accepted arm at all, and within it, the injected branch."""
    takes_accepted_arm = count < 2
    return takes_accepted_arm and count == 1


assert not any(reserve_bug_hits_branch(c) for c in RESERVE_DECLARED_INPUTS)
assert reserve_bug_hits_branch(RESERVE_FRESH_INPUT)


# --- Release-branch hidden type error (I1.S5.P2 / I1.S5.P3) ---------------

RELEASE_OLD = "(Outcome (Reservation (- (.reserved current) 1)) true)"
RELEASE_BUG_MARKER = "(- true 1)"
RELEASE_BUG = (
    "(Outcome (Reservation (if (= (.reserved current) 2) "
    f"{RELEASE_BUG_MARKER} (- (.reserved current) 1))) true)"
)
RELEASE_FIX = (
    "(Outcome (Reservation (if (= (.reserved current) 2) "
    "(- (.reserved current) 1) (- (.reserved current) 1))) true)"
)

# Declared examples through the Release accepted arm: only (1, Release).
# The (0, Release) example takes the rejected arm. Neither reaches the
# injected branch, which only fires when `(.reserved current) = 2`.
RELEASE_DECLARED_INPUTS = [1, 0]
RELEASE_FRESH_INPUT = 2


def release_bug_source() -> str:
    source = protected_source()
    assert source.count(RELEASE_OLD) == 1
    return source.replace(RELEASE_OLD, RELEASE_BUG, 1)


def release_fix_source() -> str:
    source = protected_source()
    assert source.count(RELEASE_OLD) == 1
    return source.replace(RELEASE_OLD, RELEASE_FIX, 1)


def release_bug_hits_branch(count: int) -> bool:
    takes_accepted_arm = count > 0
    return takes_accepted_arm and count == 2


assert not any(release_bug_hits_branch(c) for c in RELEASE_DECLARED_INPUTS)
assert release_bug_hits_branch(RELEASE_FRESH_INPUT)


# --- `initial` unbound-name defect (I1.S5.P4 / I1.S5.P5) ------------------

INIT_OLD = "  (examples (example (initial) => (Reservation 0)))\n  (Reservation 0))\n"
INIT_BUG = "  (examples (example (initial) => (Reservation 0)))\n  (Reservation missing-count))\n"
UNBOUND_NAME = "missing-count"

# Every top-level function/type name and every binder in scope at
# `initial`'s body: `initial` has no parameters and no `let`. `missing-count`
# spells none of the program's declared names, so it cannot resolve.
_DECLARED_TOP_LEVEL_NAMES = {"Reservation", "Event", "Outcome", "valid-state", "initial", "step"}
assert UNBOUND_NAME not in _DECLARED_TOP_LEVEL_NAMES


def unbound_bug_source() -> str:
    source = protected_source()
    assert source.count(INIT_OLD) == 1
    return source.replace(INIT_OLD, INIT_BUG, 1)


def unbound_fix_source() -> str:
    return protected_source()


# --- Combined-defect matrix (I1.S5.P5) ------------------------------------


def combined_source(*, reserve_defect: bool, unbound_defect: bool) -> str:
    source = protected_source()
    if reserve_defect:
        assert source.count(RESERVE_OLD) == 1
        source = source.replace(RESERVE_OLD, RESERVE_BUG, 1)
    if unbound_defect:
        assert source.count(INIT_OLD) == 1
        source = source.replace(INIT_OLD, INIT_BUG, 1)
    return source


def literal(type_name: str, n: int) -> str:
    """A literal of `type_name` (Bool, Int or Unit), varied by `n`."""
    if type_name == "Bool":
        return "true" if n % 2 == 0 else "false"
    if type_name == "Int":
        return str(n)
    return "()"
