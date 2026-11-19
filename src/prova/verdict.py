"""Whether the whole of a program was shown, in one word.

SPEC.md, "Results and evidence scope": "An aggregate verified result
requires a complete inventory of required obligations, all discharged,
plus passing examples and static checks for the selected profile. The
inventory identifies structurally discharged checks as well as solver
checks. No unsupported function or missing dependency may erase
unrelated obligations. Incomplete verification must never produce an
artefact labelled verified."

So the word is produced in one place, by one function of three things:
what became of every obligation, what the declared examples did when
they were run, and the evidence that the static checks passed. It asks
no solver, runs no program, reads no clock and no file: handed the same
three things twice it answers the same way twice.

The three are not three branches a caller could forget. The evidence
that the static checks passed can be built only from a checker's answer
with nothing in it, and this module's one entry point takes it as an
argument, so no caller anywhere can reach a verdict for a program the
checker refused. A run of the declared examples that does not cover
every one of them refuses to be built as a complete run. And an
obligation that says `proved` beside an attempt that did not complete --
a pair no constructor of `discharge.Finding` builds -- is refused here
rather than counted as discharged, because only a completed justified
result may be `proved`.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import discharge

# The two words the whole may stand as. `verified` is written here and
# nowhere else in this tool.
VERIFIED = "verified"
NOT_VERIFIED = "not_verified"

# The one execution status that means nothing went wrong.
COMPLETED = "completed"

# Which execution status an answer carries when the attempts behind it
# ended in several ways, most serious first. A failure of this tool
# outranks a limit this tool stopped at, which outranks a question it
# declined to translate, which outranks an attempt that finished: a
# reader is told the worst thing that happened to the verification, not
# the commonest. SPEC.md lines 280-284 name all seven, and this order is
# over those seven and no other word.
THE_MOST_SERIOUS_FIRST = (
    "tool_failure",
    "invalid_input",
    "resource_exhausted",
    "cancelled",
    "timed_out",
    "unsupported",
    COMPLETED,
)


@dataclass(frozen=True)
class StaticChecksPassed:
    """The evidence that the checker accepted a program.

    Built only by `of`, and only from an answer of the checker with
    nothing in it. The verdict takes this evidence as an argument, so a
    program the checker refused cannot have a verdict computed for it in
    any caller: the third condition of the word is kept by construction
    and not by a branch somebody could forget.
    """

    @classmethod
    def of(cls, diagnostics) -> "StaticChecksPassed | None":
        if diagnostics:
            return None
        return cls()

    def published(self) -> dict:
        return {"passed": True, "diagnostics": 0}


@dataclass(frozen=True)
class ExamplesRun:
    """What the examples a program declares did when they were run.

    Two kinds of run, and no third: one that saw every declared example,
    and one a limit of this tool stopped part way, which carries what it
    had seen and the status that stopped it. The second never reports a
    pass it did not see: the examples it never reached are counted as
    not run, and a run that did not see them all cannot be built as a
    complete one.
    """

    outcomes: tuple
    declared: int
    stopped_with: str | None = None
    stopped_because: str | None = None

    @classmethod
    def of(cls, entries, declared: int) -> "ExamplesRun":
        seen = cls._read(entries)
        if len(seen) != declared:
            raise ValueError(
                f"WHAT: a complete run of the declared examples reports "
                f"{len(seen)} outcomes for the {declared} examples the "
                "program declares. "
                "WHY: a run that lost one example would be read as a run in "
                "which every example passed, and the word 'verified' rests "
                "on that reading. "
                "HOW: report one outcome per declared example, or build the "
                "run with 'stopped_at' and say which limit stopped it."
            )
        return cls(seen, declared)

    @classmethod
    def stopped_at(
        cls, entries, declared: int, execution_status: str, reason: str
    ) -> "ExamplesRun":
        return cls(cls._read(entries), declared, execution_status, reason)

    @staticmethod
    def _read(entries) -> tuple:
        return tuple(
            (entry["function"], entry["ordinal"], bool(entry["passed"]))
            for entry in entries
        )

    def what_happened(self) -> str:
        return self.stopped_with or COMPLETED

    def why_the_word_is_withheld(self) -> str | None:
        """What to tell a reader about the examples, or nothing when
        they say nothing against the word."""
        failed = self._that_did_not_pass()
        said = []
        if failed:
            said.append(
                f"{len(failed)} of the {self.declared} examples this program "
                "declares did not pass: "
                + ", ".join(f"{name} example {ordinal}" for name, ordinal in failed)
            )
        if self.stopped_with is not None:
            said.append(
                f"the run of the declared examples was stopped with "
                f"{self._never_run()} of {self.declared} never run: "
                f"{self.stopped_because}"
            )
        return "; ".join(said) or None

    def published(self) -> dict:
        failed = self._that_did_not_pass()
        entry = {
            "of": self.declared,
            "passed": len(self.outcomes) - len(failed),
            "failed": [
                {"function": name, "ordinal": ordinal} for name, ordinal in failed
            ],
            "not_run": self._never_run(),
        }
        if self.stopped_because is not None:
            entry["stopped_because"] = self.stopped_because
        return entry

    def _never_run(self) -> int:
        """How many declared examples this run never reached.

        One place states the number: the count an answer publishes and
        the sentence that explains it are read from here, so they cannot
        say two different things.
        """
        return self.declared - len(self.outcomes)

    def _that_did_not_pass(self) -> tuple:
        return tuple(
            (name, ordinal) for name, ordinal, passed in self.outcomes if not passed
        )


@dataclass(frozen=True)
class Obligations:
    """Every obligation of one program beside what became of it, counted.

    Holds the findings and nothing else. Every one of them is counted:
    an obligation the translation declined is undischarged, not absent,
    which is how an unsupported function withholds the word over the
    whole without removing anything from the rest of the program.
    """

    findings: tuple

    @classmethod
    def of(cls, findings: dict) -> "Obligations":
        for identity, finding in findings.items():
            cls._refuse_a_pair_nothing_builds(identity, finding)
        return cls(tuple(findings.items()))

    @staticmethod
    def _refuse_a_pair_nothing_builds(identity: str, finding) -> None:
        settled = (discharge.PROVED, discharge.DISPROVED)
        if finding.result in settled and finding.execution_status != COMPLETED:
            raise ValueError(
                f"WHAT: the obligation {identity!r} stands as "
                f"{finding.result!r} beside an attempt that ended "
                f"{finding.execution_status!r}. "
                "WHY: only a completed justified result may be 'proved', and "
                "an aggregate that believed this pair would say 'verified' "
                "over a proof that never finished (SPEC.md lines 280-284). "
                "HOW: no constructor of prova.discharge.Finding builds that "
                "pair; fix the caller that built it by hand."
            )

    def undischarged(self) -> list:
        return [
            identity
            for identity, finding in self.findings
            if finding.result != discharge.PROVED
        ]

    def what_happened(self) -> tuple:
        return tuple(finding.execution_status for _, finding in self.findings)

    def why_the_word_is_withheld(self) -> str | None:
        if not self.findings:
            return (
                "this program owes no obligation at all, so nothing about it "
                "was shown"
            )
        left = self.undischarged()
        if not left:
            return None
        return (
            f"{len(left)} of the {len(self.findings)} obligations this program "
            "owes are not discharged: " + ", ".join(left)
        )

    def published(self) -> dict:
        left = self.undischarged()
        return {
            "of": len(self.findings),
            "discharged": len(self.findings) - len(left),
            "undischarged": left,
            "by": self._by_the_way_they_were_discharged(),
        }

    def _by_the_way_they_were_discharged(self) -> dict:
        return {
            way: len(
                [
                    identity
                    for identity, finding in self.findings
                    if finding.result == discharge.PROVED
                    and finding.discharged_by == way
                ]
            )
            for way in (discharge.BY_THE_SOLVER, discharge.BY_A_RULE_OF_THE_PROFILE)
        }


@dataclass(frozen=True)
class Attempts:
    """What happened to the attempts behind one answer, and which of
    them the answer as a whole carries."""

    statuses: tuple

    def most_serious(self) -> str:
        for status in THE_MOST_SERIOUS_FIRST:
            if status in self.statuses:
                return status
        return COMPLETED


@dataclass(frozen=True)
class Verdict:
    """Where a whole program stands, and what happened to the attempt.

    Built only by `over`. The word is produced there and in no other
    place in this tool, and this value has no constructor a caller can
    hand a word of its own to.

    It holds more than the two words because it carries the evidence
    they rest on: a reader told 'not_verified' is told which obligations
    are not discharged and which examples did not pass, and a reader
    told 'verified' is told how much of it rests on a solver's word.
    That makes it the answer's own record, which is what the fields of
    an answer are allowed to be.
    """

    result: str
    execution_status: str
    reason: str | None
    obligations: Obligations
    examples: ExamplesRun
    static_checks: StaticChecksPassed

    @classmethod
    def over(
        cls,
        findings: dict,
        examples: ExamplesRun,
        static_checks: StaticChecksPassed,
    ) -> "Verdict":
        """The word over a whole program, from what became of every
        obligation, what its declared examples did, and the evidence
        that the static checks passed."""
        if static_checks is None:
            raise ValueError(
                "WHAT: a verdict was asked for without the evidence that the "
                "static checks passed. "
                "WHY: the word rests on that evidence, and a program the "
                "checker refused has none, so there is nothing to aggregate "
                "for it. "
                "HOW: build it with prova.verdict.StaticChecksPassed.of over "
                "the checker's own answer, and answer the refusal instead "
                "where there is none."
            )
        owed = Obligations.of(findings)
        attempts = Attempts(owed.what_happened() + (examples.what_happened(),))
        withheld = [
            said
            for said in (
                owed.why_the_word_is_withheld(),
                examples.why_the_word_is_withheld(),
            )
            if said is not None
        ]
        if not withheld:
            return cls(
                VERIFIED,
                attempts.most_serious(),
                None,
                owed,
                examples,
                static_checks,
            )
        return cls(
            NOT_VERIFIED,
            attempts.most_serious(),
            "this program is not verified: " + "; ".join(withheld),
            owed,
            examples,
            static_checks,
        )

    def published(self) -> dict:
        entry = {"result": self.result, "execution_status": self.execution_status}
        if self.reason is not None:
            entry["reason"] = self.reason
        entry["obligations"] = self.obligations.published()
        entry["examples"] = self.examples.published()
        entry["static_checks"] = self.static_checks.published()
        return entry
