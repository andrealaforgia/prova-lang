"""Laws every answer of this tool obeys about what it stands on, for any
request, not only the ones F17's acceptance tests send.

LAW1 a completed answer carries the dependency digest this tool
     publishes, and an answer that completed nothing carries no
     provenance at all.
LAW2 the revision an answer carries is the SHA-256 of exactly the
     characters that were sent, so 2 texts that differ never share one.
LAW3 every one of the 4 versions an answer names is either a version
     with a digit in it or a sentence saying it does not apply.

Drives the `prova` command over its JSON stdin/stdout surface, as the
other property tests here do. No imports from src/prova. The manifest is
read once per process: it is a constant of the shipped tool, and each
case then sends its own request.

Derandomised with a bounded example count so the verdict does not depend
on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

import hashlib
import json
import subprocess

from hypothesis import given, settings
from hypothesis import strategies as st

THE_OPERATIONS_THAT_READ_A_PROGRAM = ("check", "examples", "verify", "parse", "format")
THE_VERSIONS_AN_ANSWER_NAMES = ("compiler", "encoding", "solver", "runtime")
DOES_NOT_APPLY = "not applicable:"

A_PROGRAM = """\
(defn twice
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (ensures (= result (* n 2)))
  (examples (example (twice 2) => 4))
  (* n 2))
"""
EVERY_KIND_OF_SOURCE = (
    A_PROGRAM,
    "",
    "(defn",
    "(defn f (sig ((n Int)) -> Int ! pure) (examples (example (f 1) => 1)) (+ n true))",
    "(deftype T (record (f T)))",
)

_MANIFEST: list = []
_DIGESTS: dict = {}


def _ask(request: dict) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=20.0,
    )
    assert proc.returncode == 0, (
        f"the tool exited {proc.returncode} for {request!r} instead of "
        f"answering: {proc.stderr[-500:]!r}"
    )
    return json.loads(proc.stdout)


def _manifest() -> dict:
    if not _MANIFEST:
        _MANIFEST.append(_ask({"operation": "discover"}))
    return _MANIFEST[0]


def _published_dependency_digest() -> str:
    stands_on = _manifest().get("stands_on") or {}
    digest = stands_on.get("dependency_digest")
    assert isinstance(digest, str) and digest, (
        f"the manifest publishes no dependency digest: {stands_on}. A client "
        "cannot tell whether a kept answer still stands on this tool."
    )
    return digest


def _program_answering(factor: int) -> str:
    return (
        "(defn multiplied\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        f"  (examples (example (multiplied 2) => {2 * factor}))\n"
        f"  (* n {factor}))\n"
    )


@given(
    operation=st.sampled_from(THE_OPERATIONS_THAT_READ_A_PROGRAM + ("discover",)),
    source=st.sampled_from(EVERY_KIND_OF_SOURCE),
)
@settings(max_examples=12, deadline=None, derandomize=True)
def test_every_completed_answer_says_what_it_stands_on(operation, source):
    """LAW1: a completed answer stands on the dependency digest this tool
    publishes; an answer that completed nothing stands on nothing."""
    answer = _ask({"operation": operation, "source": source})
    stands_on = answer.get("stands_on")

    if answer["status"] != "completed":
        assert stands_on is None, (
            f"the {operation!r} answer with status {answer['status']!r} "
            f"carries {stands_on}: nothing was read through, so the answer "
            "stands on nothing and must not appear to."
        )
        return

    assert isinstance(stands_on, dict), (
        f"the completed {operation!r} answer does not say what it stands on: "
        f"{sorted(answer)}. A reader cannot tell which tool and which "
        "revision are behind it."
    )
    assert stands_on.get("dependency_digest") == _published_dependency_digest(), (
        f"the completed {operation!r} answer stands on "
        f"{stands_on.get('dependency_digest')!r} and this tool publishes "
        f"{_published_dependency_digest()!r}: two digests for one tool leave "
        "a client unable to decide whether a kept answer is still current."
    )


@given(factor=st.integers(min_value=2, max_value=10**6))
@settings(max_examples=12, deadline=None, derandomize=True)
def test_two_sources_never_share_one_revision(factor):
    """LAW2: the revision an answer carries is the SHA-256 of the
    characters that were sent, so two texts that differ never share
    one."""
    source = _program_answering(factor)
    expected = hashlib.sha256(source.encode("utf-8")).hexdigest()

    answer = _ask({"operation": "check", "source": source})

    assert answer["status"] == "completed", (
        f"a program multiplying by {factor} was answered "
        f"{answer['status']!r}: {answer}"
    )
    assert answer["source_digest"] == expected, (
        f"the answer is about {answer['source_digest']!r} and the text sent "
        f"is {expected!r}: an answer naming another revision certifies a text "
        "nobody sent."
    )
    seen = _DIGESTS.setdefault(answer["source_digest"], source)
    assert seen == source, (
        f"the texts multiplying by {factor} and the one kept before share the "
        f"revision {answer['source_digest']!r}: two different programs would "
        "be told apart by nothing."
    )


@given(
    operation=st.sampled_from(THE_OPERATIONS_THAT_READ_A_PROGRAM + ("discover",)),
    source=st.sampled_from(EVERY_KIND_OF_SOURCE),
)
@settings(max_examples=12, deadline=None, derandomize=True)
def test_every_version_is_a_version_or_says_it_does_not_apply(operation, source):
    """LAW3: each of the 4 versions a completed answer names is a version
    with a digit in it or a sentence saying it does not apply."""
    answer = _ask({"operation": operation, "source": source})
    if answer["status"] != "completed":
        return
    named = (answer.get("stands_on") or {}).get("versions")

    assert isinstance(named, dict) and sorted(named) == sorted(
        THE_VERSIONS_AN_ANSWER_NAMES
    ), (
        f"the completed {operation!r} answer names {named}: a reader "
        f"comparing two answers has to find each of "
        f"{sorted(THE_VERSIONS_AN_ANSWER_NAMES)} in both."
    )
    for version, said in named.items():
        assert isinstance(said, str) and (
            said.startswith(DOES_NOT_APPLY)
            or any(character.isdigit() for character in said)
        ), (
            f"the completed {operation!r} answer says {said!r} about "
            f"{version!r}: that is neither a version a reader can compare nor "
            f"a sentence saying it does not apply."
        )
