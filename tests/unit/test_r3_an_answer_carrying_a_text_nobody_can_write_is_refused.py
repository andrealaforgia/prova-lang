"""The last place an answer becomes the characters a caller reads
refuses to print a text that cannot be written as UTF-8.

Every field a request carries is already read by a rule that refuses
half a character by name, so this stands behind all of them: if any
text ever reached an answer unchecked, a client that wrote the answer
out would fail where the tool did not. It is exercised here directly,
because no request the command accepts reaches it.
"""

from __future__ import annotations

import json
import sys

import pytest

from prova import service, values


def test_an_answer_holding_half_a_character_is_refused_before_it_is_printed():
    """Given an answer that somehow carries half a character, when it is
    turned into the text a caller reads, then what is printed is a
    refusal instead, and every text in it can be written as UTF-8.
    """
    printed = service.printable_answer(
        {"operation": "\ud800check", "status": "unavailable", "diagnostics": []}
    )

    answer = json.loads(printed)
    assert answer["status"] == "invalid_input", (
        f"the tool printed {printed[:300]!r}: an answer carrying a text that "
        "cannot be written is refused, not sent on to a client that cannot "
        "write it either."
    )
    assert answer["diagnostics"][0]["category"] == "malformed_request", answer
    assert "\ud800" not in json.dumps(answer, ensure_ascii=False), (
        f"the refusal carries the text it refused: {answer}. A refusal about a "
        "text nobody can write never copies it."
    )


def test_an_ordinary_answer_is_written_exactly_as_json():
    """Given an ordinary answer, when it is turned into the text a
    caller reads, then it is that answer, written as 1 JSON object.
    """
    answer = {"operation": "check", "status": "completed", "diagnostics": []}

    printed = service.printable_answer(answer)

    assert json.loads(printed) == answer, (
        f"an answer that holds only writable text came back as {printed[:300]!r}: "
        "the check in front of printing refuses nothing else."
    )


def test_a_value_this_interpreter_will_not_write_is_refused_by_the_number_that_stopped_it():
    """Given a process whose caller lowered the digits its interpreter
    writes to 640, below the 4000 this tool declares, when a value of
    700 digits is written, then the tool refuses and names the 640 that
    really stopped it, instead of breaking on the way out.
    """
    written_before = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(640)
    try:
        with pytest.raises(values.TooLargeToWrite) as refused:
            values.render(10**699)
    finally:
        sys.set_int_max_str_digits(written_before)

    assert "640" in refused.value.message, (
        f"the refusal says {refused.value.message[:200]!r}: a caller reading "
        "the 4000 this tool declares would look for a result it is already "
        "under, so the refusal names the number its own interpreter writes."
    )
    assert values.render(10**699).endswith("0"), (
        "a value of 700 digits is written again once the interpreter is back "
        "to the digits it writes by default."
    )
