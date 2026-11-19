"""What SPEC.md says a manifest must describe, and the one way F11's
acceptance tests talk to the tool.

Not a test module (no `test_` prefix); pytest will not collect it.
Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova: every table below is read by hand from SPEC.md,
never from the answer under observation.
"""

from __future__ import annotations

import pathlib
import tempfile

import json
import subprocess

# SPEC.md lines 467-468: "Initial operation categories are discovery,
# parsing, formatting, checking, verification, examples and building."
# Seven of them, written here in SPEC.md's own words. Which operation
# name the tool gives each category is the tool's own choice and is read
# from the manifest; that each category is there, and says whether it can
# be used, is SPEC.md's requirement.
THE_CATEGORIES_SPEC_NAMES = (
    "discovery",
    "parsing",
    "formatting",
    "checking",
    "verification",
    "examples",
    "building",
)

# SPEC.md line 98 and line 132: the three type names core-0 has, with
# what line 132 says each of them is.
THE_TYPES_CORE_0_HAS = ("Unit", "Bool", "Int")

# SPEC.md lines 178-189, the operator table, written out by hand: the
# types of the arguments each operator takes and the type of its answer.
# `=` is the one operator whose argument types are not fixed type names
# ("Two values of the same core type"), so its arguments are written as
# `None` here and read as "one type standing for any core type, the same
# in both places".
THE_OPERATORS_AND_THEIR_TYPES = (
    ("+", ("Int", "Int"), "Int"),
    ("-", ("Int", "Int"), "Int"),
    ("*", ("Int", "Int"), "Int"),
    ("<", ("Int", "Int"), "Bool"),
    ("<=", ("Int", "Int"), "Bool"),
    (">", ("Int", "Int"), "Bool"),
    (">=", ("Int", "Int"), "Bool"),
    ("=", None, "Bool"),
    ("and", ("Bool", "Bool"), "Bool"),
    ("or", ("Bool", "Bool"), "Bool"),
    ("not", ("Bool",), "Bool"),
)

# The two words SPEC.md lines 469-470 give an operation: an operation the
# tool answers, and one it advertises as unavailable and refuses.
AVAILABILITY_WORDS = ("available", "unavailable")

# A program with one function per core type, used as the body of a
# request that matches a published request shape. Written here by hand.
A_PROGRAM = """\
(defn twice
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (ensures (= result (* n 2)))
  (examples (example (twice 2) => 4))
  (* n 2))
"""


# The smallest machine a request can be about: a counter that counts up
# and accepts every count, and the descriptor naming its eight parts.
# Written here by hand, like the program above, because the `machine`
# operation takes two fields that must agree with each other -- a
# descriptor names what its program declares -- so a request built from
# the published shape needs both.
A_MACHINE_PROGRAM = """\
(deftype Counter (record (held Int)))
(deftype Event (union (Count)))
(deftype Outcome (record (state Counter) (accepted Bool)))

(defn sound
  (sig ((current Counter)) -> Bool ! pure)
  (examples (example (sound (Counter 0)) => true))
  (>= (.held current) 0))

(defn empty-counter
  (sig () -> Counter ! pure)
  (examples (example (empty-counter) => (Counter 0)))
  (Counter 0))

(defn count-one
  (sig ((current Counter) (event Event)) -> Outcome ! pure)
  (examples (example (count-one (Counter 0) (Count)) => (Outcome (Counter 1) true)))
  (match event ((Count) (Outcome (Counter (+ (.held current) 1)) true))))

(defn counted-state
  (sig ((produced Outcome)) -> Counter ! pure)
  (examples (example (counted-state (Outcome (Counter 1) true)) => (Counter 1)))
  (.state produced))

(defn any-count
  (sig ((current Counter) (event Event)) -> Bool ! pure)
  (examples (example (any-count (Counter 0) (Count)) => true))
  true)
"""
A_MACHINE_DESCRIPTOR = {
    "schema": "machine-descriptor/1",
    "types": {"state": "Counter", "event": "Event", "outcome": "Outcome"},
    "roles": {
        "init": "empty-counter",
        "step": "count-one",
        "state-of": "counted-state",
        "admissible": "any-count",
        "invariant": "sound",
    },
    "assumptions": ["One count at a time, over one authoritative counter."],
}

# The operations that take a descriptor: a descriptor names what its
# program declares, so a request built out of every field one of these
# publishes must be about the machine program above. `verify` is one of
# them since it takes a descriptor it may leave out.
OPERATIONS_ABOUT_A_MACHINE = ("machine", "verify")


# The program a request for `operation` is about: the machine for the
# operations whose other field names what its program declares, and the
# program above for every other.
def a_program_for(operation: str) -> str:
    if operation in OPERATIONS_ABOUT_A_MACHINE:
        return A_MACHINE_PROGRAM
    return A_PROGRAM


def ask(request: dict, timeout: float = 20.0) -> dict:
    """The answer the `prova` command gives to one request."""
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    assert proc.returncode == 0, (
        f"the tool exited {proc.returncode} for {request!r}, so it reported "
        f"a failure of itself rather than answering: {proc.stderr[-800:]!r}. "
        "Every request this tool reads is answered with one JSON object."
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError(
            f"the tool answered {proc.stdout[:400]!r}, which is not one JSON "
            f"object ({error}). A client reads one answer per request."
        ) from None


def manifest() -> dict:
    """The `result` block of the tool's answer to `discover`."""
    answer = ask({"operation": "discover"})
    assert answer.get("status") == "completed", (
        f"`discover` answered {answer.get('status')!r}: {answer}. The one "
        "operation an agent starts from must answer."
    )
    result = answer.get("result")
    assert isinstance(result, dict), (
        f"`discover` carried no manifest: {sorted(answer)}. An agent reads "
        "what it may call from this answer and has nowhere else to look."
    )
    return result


def part_of_the_manifest(name: str, what_for: str) -> dict:
    """One named part of the manifest, or a refusal saying what an agent
    cannot do without it."""
    result = manifest()
    part = result.get(name)
    assert isinstance(part, dict) and part, (
        f"the manifest carries no {name!r}: it carries {sorted(result)}. "
        f"Without it an agent cannot {what_for}, and SPEC.md line 475 says "
        "agents must discover signatures and bindings without guessing "
        "undocumented APIs; publish it under {name!r} in the `discover` "
        "answer."
    )
    return part


def published_operation_shapes() -> dict:
    return part_of_the_manifest(
        "operation_schemas",
        "write a request for an operation or read the answer it gets back",
    )


def published_categories() -> dict:
    return part_of_the_manifest(
        "categories",
        "tell which of SPEC.md's operation categories this tool can be used "
        "for",
    )


def published_language() -> dict:
    return part_of_the_manifest(
        "language",
        "write a program without guessing which types and operators core-0 "
        "has",
    )


def availability_of_each_operation() -> dict:
    result = manifest()
    operations = result.get("operations")
    assert isinstance(operations, dict) and operations, (
        f"the manifest names no operations: {sorted(result)}."
    )
    return operations


def wrong_kind_for(kind: str) -> object:
    """A value of a kind the published shape does not name for a field.

    One wrong value per published kind of field, chosen so that the
    value is wrong for that field and for no other reason: a number
    where a text is named, and a text where a list of texts is named.
    """
    return "not a list" if "list" in kind else 7

# The values a request built from a published shape carries. A text
# field takes "3" unless the shape names a field that must be a name of
# the program or a place in the filesystem: `build` invokes the function
# its 'entry' names and writes to the file its 'output_file' names, so a
# request built from its shape with "3" in both would be refused for
# reasons that say nothing about the shape. The destination stands in
# one directory per test session and is a path nothing is at.
THE_FUNCTION_THE_PROGRAM_DECLARES = "twice"

# Where a build asked for out of a published shape writes. One directory
# per test process, removed when the process ends, so a run of the suite
# leaves nothing behind it and no two runs meet at one path.
_WHERE_A_BUILD_MAY_WRITE = tempfile.TemporaryDirectory(
    prefix="prova-published-shape-"
)
_DESTINATIONS = [0]


def a_destination() -> str:
    """A path in an existing directory that nothing stands at, for a
    request built from the published shape of `build`."""
    _DESTINATIONS[0] += 1
    return str(
        pathlib.Path(_WHERE_A_BUILD_MAY_WRITE.name)
        / f"artefact-{_DESTINATIONS[0]}.py"
    )


def a_value_matching(operation: str, field: str, described: dict) -> object:
    """The value a request built only from a published shape carries for
    one field of it.

    One place answers it for every operation, so an operation added with
    a field of its own is filled here and not in each test that reads a
    published shape.
    """
    if field == "source":
        return a_program_for(operation)
    if field == "descriptor":
        return A_MACHINE_DESCRIPTOR
    if field in ("function", "entry"):
        return THE_FUNCTION_THE_PROGRAM_DECLARES
    if field == "output_file":
        return a_destination()
    if "list" in described["kind"]:
        return ["3"]
    return "3"
