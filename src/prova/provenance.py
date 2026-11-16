"""What this tool is made of, as an answer reports it.

An answer says which text it is about and which tool read it. This
module owns the second half of that: the digest over a text, and, beside
it, what stands behind an answer.

It reads nothing of a program and decides nothing about one: a client
compares what two answers stand on, and two answers that agree here were
read by the same tool from the same language.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
from dataclasses import dataclass

from prova import encoding, solving


@dataclass(frozen=True)
class Digest:
    """The SHA-256 of one text, written as the hexadecimal a client
    recomputes for itself.

    Built only by hashing a text, so nothing hands a client a digest it
    did not compute from characters. One place writes the algorithm: the
    revision of a submitted source and the digest over this tool's own
    description are then spelled the same way, and a client comparing
    the two never has to ask which spelling it holds.
    """

    hexadecimal: str

    @classmethod
    def of(cls, text: str) -> "Digest":
        return cls(hashlib.sha256(text.encode("utf-8")).hexdigest())

    def rendered(self) -> str:
        return self.hexadecimal


# The four things SPEC.md lines 270-284 ask an answer to name beside its
# claim: what read the program, what turned an obligation into the
# language of a solver, what tried to settle it, and what ran the result.
COMPILER = "compiler"
ENCODING = "encoding"
SOLVER = "solver"
RUNTIME = "runtime"
THE_FOUR = (COMPILER, ENCODING, SOLVER, RUNTIME)

# How an answer says that one of the four is behind nothing here.
DOES_NOT_APPLY = "not applicable:"


@dataclass(frozen=True)
class Version:
    """One of the four things behind an answer, and what this tool says
    about it.

    Built two ways and no other: as something this tool used, with the
    version it is at, or as something that does not apply, with the
    reason there is none. A version that is both, or a name with nothing
    beside it, cannot be built, so a client reading one of the four is
    never left with a name and no word about it.
    """

    name: str
    said: str

    @classmethod
    def used(cls, name: str, what: str, number: str) -> "Version":
        cls._refuse_nothing_said(name, number, "the version it is at")
        return cls(name, f"{what} {number}")

    @classmethod
    def does_not_apply(cls, name: str, reason: str) -> "Version":
        cls._refuse_nothing_said(name, reason, "the reason there is none")
        return cls(name, f"{DOES_NOT_APPLY} {reason}")

    @staticmethod
    def _refuse_nothing_said(name: str, said: str, owed: str) -> None:
        if said and said.strip():
            return
        raise ValueError(
            f"WHAT: the version {name!r} is being built with nothing said "
            f"about it. "
            f"WHY: a client reading an answer compares what stands behind "
            f"it; a name with nothing beside it says neither that this tool "
            f"used it nor that there is none. "
            f"HOW: build it with {owed}."
        )

    def written_into(self, named: dict) -> None:
        named[self.name] = self.said


@dataclass(frozen=True)
class SolverStanding:
    """What one answer says about the solver behind it: the one it asked
    with the version that answered, or the reason it asked none.

    Built only by the two constructors below, so a standing that both
    names a solver and gives a reason there is none -- or neither --
    cannot be built, and no answer can report a solver it did not ask.
    """

    name: str | None = None
    version: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if (self.name is None) != (self.reason is None):
            return
        raise ValueError(
            "WHAT: a solver standing is being built naming "
            f"{self.name!r} and giving {self.reason!r} as the reason there is "
            "none. "
            "WHY: an answer says either which solver answered it or why none "
            "did; both at once reports a solver nobody asked, and neither "
            "leaves a reader unable to tell a trusted result from one this "
            "tool reached alone. "
            "HOW: build it with SolverStanding.asked or "
            "SolverStanding.asked_none."
        )

    @classmethod
    def asked(cls, name: str, version: str) -> "SolverStanding":
        return cls(name=name, version=version)

    @classmethod
    def asked_none(cls, reason: str) -> "SolverStanding":
        return cls(reason=reason)

    def text(self) -> "str | None":
        """The solver and its version as one text, or nothing when none
        was asked. One place writes it: the versions an answer stands on
        and the trust it discloses read the same characters."""
        if self.name is None:
            return None
        return f"{self.name} {self.version}"

    def solver_row(self) -> "Version":
        if self.name is None:
            return Version.does_not_apply(SOLVER, self.reason)
        return Version.used(SOLVER, self.name, self.version)

    def encoding_row(self) -> "Version":
        if self.name is None:
            return Version.does_not_apply(
                ENCODING,
                "this answer turned no obligation into the language of a "
                "solver, so no translation stands behind it",
            )
        return Version.used(ENCODING, "core-0-to-smt", encoding.VERSION)


# What an operation that asks no solver says about one. Every operation
# but verify reads a program and answers about it without turning an
# obligation into the language of a solver.
NO_SOLVER_IN_THIS_ANSWER = SolverStanding.asked_none(
    "this operation asks no solver: it reads a program and answers about it "
    "without turning any obligation into the language of one"
)


@dataclass(frozen=True)
class Versions:
    """Exactly the four things SPEC.md asks an answer to name, and
    nothing else.

    A collection of another set of names refuses to be built, so an
    answer can neither drop one of the four quietly nor name a fifth
    thing a client cannot look up.
    """

    versions: tuple[Version, ...]

    def __post_init__(self) -> None:
        named = {}
        for version in self.versions:
            version.written_into(named)
        if tuple(named) == THE_FOUR:
            return
        raise ValueError(
            f"WHAT: these versions name {tuple(named)} and an answer names "
            f"{THE_FOUR}. "
            "WHY: a client comparing two answers looks for each of the four "
            "in both; one missing reads as a tool that did not use it, and "
            "one added cannot be looked up anywhere. "
            "HOW: name all four, in that order, each either as used or as "
            "not applicable."
        )

    @classmethod
    def of_this_tool(cls, standing: SolverStanding) -> "Versions":
        """The four behind the answer being built: the tool and the
        runtime that produced it, and the translation and the solver as
        this answer used them."""
        return cls(
            (
                Version.used(COMPILER, "prova", _this_tools_version()),
                standing.encoding_row(),
                standing.solver_row(),
                Version.used(
                    RUNTIME,
                    platform.python_implementation().lower(),
                    platform.python_version(),
                ),
            )
        )

    def published(self) -> dict:
        named: dict = {}
        for version in self.versions:
            version.written_into(named)
        return named


@dataclass(frozen=True)
class Provenance:
    """What a completed answer stands on: the digest of this tool and of
    the language it reads, and the versions behind both.

    A client keeps an answer and compares the two digests later: the
    revision of its own source against the one the answer names, and
    this digest against the one the tool publishes now. An answer whose
    source has changed since, or whose tool has, is then seen for what
    it is rather than read as a statement about what the client holds.

    An answer carries this under the name `stands_on`. The word
    provenance says the concept best and names this module, but it
    carries `proven` inside it, and an answer of this tool is read by
    callers that refuse any answer whose text says something was proven.
    """

    dependency_digest: Digest
    versions: Versions

    @classmethod
    def of(
        cls, profile: dict, language: dict, standing: SolverStanding
    ) -> "Provenance":
        """What one answer stands on.

        The digest is taken over the tool itself -- the profile, the
        language and the components this tool is built of -- and not over
        what this one answer used, so every answer of one installation
        carries the same digest and a client can compare a kept answer
        with the manifest it reads later. Which of those components this
        answer really asked is said beside it, under `versions`.
        """
        described = json.dumps(
            {
                "profile": profile,
                "language": language,
                "components": the_components(),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return cls(Digest.of(described), Versions.of_this_tool(standing))

    def published(self) -> dict:
        return {
            "dependency_digest": self.dependency_digest.rendered(),
            "versions": self.versions.published(),
        }


def the_components() -> dict:
    """What this installation of the tool is built of, whichever answer
    is being built: the tool, the translation, the solver it is pinned to
    and the runtime.

    The solver is read from the installed package's metadata rather than
    by loading the solver itself, so naming it costs no answer the time
    of loading a solver it never asks.
    """
    return {
        "compiler": f"prova {_this_tools_version()}",
        "encoding": f"core-0-to-smt {encoding.VERSION}",
        "solver": _the_solver_it_is_pinned_to(),
        "runtime": (
            f"{platform.python_implementation().lower()} "
            f"{platform.python_version()}"
        ),
    }


def the_solver_it_requires() -> dict:
    """What this tool requires of a solver, as the manifest publishes it.

    Read from the installed package's own metadata, so the one place the
    version is pinned is pyproject.toml and a client reading the manifest
    is reading that pin. Naming it costs no answer the time of loading a
    solver: what an answer really asked is said under `stands_on`.
    """
    return {
        "name": solving.SOLVER,
        "package": solving.PACKAGE,
        "required": _the_requirement(),
        "installed": _the_solver_it_is_pinned_to(),
    }


def _the_requirement() -> str:
    """The exact requirement this tool declares for its solver."""
    try:
        required = importlib.metadata.requires("prova") or []
    except importlib.metadata.PackageNotFoundError:
        return "the metadata of this tool is not installed, so the "\
            "requirement it declares cannot be read"
    for requirement in required:
        if requirement.startswith(solving.PACKAGE):
            return requirement[len(solving.PACKAGE):] or "any version"
    return (
        f"this tool declares no requirement on {solving.PACKAGE!r}, so no "
        "version of it is pinned"
    )


def _the_solver_it_is_pinned_to() -> str:
    try:
        return f"{solving.PACKAGE} {importlib.metadata.version(solving.PACKAGE)}"
    except importlib.metadata.PackageNotFoundError:
        return f"{solving.PACKAGE} is not installed beside this tool"


def _this_tools_version() -> str:
    """The version of this tool, read from the metadata of the installed
    package, so the one number lives in pyproject.toml and nowhere else.

    A package whose metadata cannot be read is a failure of the tool, not
    an answer: an answer naming no version of the thing that produced it
    could not be compared with any other.
    """
    try:
        return importlib.metadata.version("prova")
    except importlib.metadata.PackageNotFoundError as missing:
        raise ValueError(
            "WHAT: the version of this tool cannot be read: its package "
            "metadata is not installed. "
            "WHY: every answer names the version that produced it, and an "
            "answer that cannot name it cannot be compared with another. "
            "HOW: install the package (uv sync, or pip install -e .) and "
            "send the request again."
        ) from missing
