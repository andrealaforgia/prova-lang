"""F15.B2 -- the canonical text carries every comment the reader wrote,
once each, in the order they were written, over the declaration that
follows them or at the end when none does.

SPEC.md lines 62-63 say a formatter must preserve the text and order of
comments, attaching each to the following syntax node or to the document
end. The prose a reader writes about a program is the part a tool is
most tempted to drop, so it is stated here on its own.

still passes if: the tool had written the comments in a block of its own
at the top. The last assertion reads where each comment stands relative
to the declaration it is about, so a tool that gathered them all in one
place fails.
"""

from __future__ import annotations

from _f15_format_fixtures import (
    ask_for_the_tree,
    ask_to_format,
    canonical_text,
    comments_of,
)

# A program whose 3 comments stand in 3 different places: above the
# first declaration, above the second, and inside the body of the last
# one, where no declaration follows them.
THREE_COMMENTS = """; what this program counts with
(deftype Counter (record (held Int)))
; how much it holds
(defn held-of (sig ((counter Counter)) -> Int ! pure)
  (examples (example (held-of (Counter 1)) => 1))
  ; nothing follows this one
  (.held counter))
"""

WRITTEN_IN_THIS_ORDER = (
    "; what this program counts with",
    "; how much it holds",
    "; nothing follows this one",
)


def test_every_comment_is_written_once_and_in_the_order_it_was_written():
    canonical = canonical_text(ask_to_format(THREE_COMMENTS))

    assert isinstance(canonical, str), (
        f"a program carrying 3 comments was not answered with text: "
        f"{ask_to_format(THREE_COMMENTS)}. Comments change neither typing nor "
        "execution, so a program that carries them is still accepted"
    )
    for written in WRITTEN_IN_THIS_ORDER:
        standing = [line.strip() for line in canonical.splitlines()].count(written)
        assert standing == 1, (
            f"the comment {written!r} stands {standing} time(s) in the "
            f"canonical text:\n{canonical}\nA reader wrote it once, so a "
            "second copy invents prose and none loses it; hand each comment "
            "to exactly one place in the text"
        )

    answered = ask_for_the_tree(canonical)
    assert comments_of(answered["result"]["tree"]) == list(WRITTEN_IN_THIS_ORDER), (
        f"the canonical text carries its comments in the order "
        f"{comments_of(answered['result']['tree'])} and the reader wrote them "
        f"in the order {list(WRITTEN_IN_THIS_ORDER)}:\n{canonical}\nProse "
        "read out of order says the wrong thing about the wrong "
        "declaration; keep the order the source wrote"
    )


def test_a_comment_stands_over_the_declaration_it_was_written_over():
    canonical = canonical_text(ask_to_format(THREE_COMMENTS))
    lines = [line.strip() for line in canonical.splitlines()]

    first_comment = lines.index("; what this program counts with")
    counter = next(i for i, line in enumerate(lines) if line.startswith("(deftype"))
    second_comment = lines.index("; how much it holds")
    held_of = next(i for i, line in enumerate(lines) if line.startswith("(defn"))

    assert first_comment < counter < second_comment < held_of, (
        f"the canonical text puts its comments at lines {first_comment}, "
        f"{second_comment} and its declarations at lines {counter}, "
        f"{held_of}:\n{canonical}\nA comment says something about the "
        "declaration written under it, so moving it away from that "
        "declaration changes what it says; write each comment over the "
        "declaration that follows it"
    )


def test_a_comment_that_no_declaration_follows_stands_at_the_end():
    canonical = canonical_text(ask_to_format(THREE_COMMENTS))
    lines = [line.strip() for line in canonical.splitlines() if line.strip()]

    assert lines[-1] == "; nothing follows this one", (
        f"the last line carrying anything is {lines[-1]!r}:\n{canonical}\n"
        "SPEC.md line 63 sends a comment no syntax node follows to the "
        "document end; write it after the last declaration"
    )
