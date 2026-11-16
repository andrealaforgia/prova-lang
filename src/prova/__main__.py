"""Reads one JSON request from stdin (or --request FILE), writes one JSON
response to stdout."""

from __future__ import annotations

import json
import os
import pathlib
import sys

from prova import service
from prova.budgets import Budgets, UnreadableBudget
from prova.reader import LITERAL_DIGITS


def main() -> None:
    args = sys.argv[1:]
    unwritable = service.unwritable_budget_variable(os.environ)
    if unwritable is not None:
        print(service.printable_answer(unwritable.response_for(None)))
        sys.exit(0)

    budgets = Budgets.from_environment(os.environ)
    if isinstance(budgets, UnreadableBudget):
        print(service.printable_answer(service.budgets_refused(budgets)))
        sys.exit(0)

    try:
        request_text = _read_at_most(args, budgets.request_ceiling() + 1)
    except UnicodeDecodeError as error:
        print(service.printable_answer(_unreadable_bytes(error).response_for(None)))
        sys.exit(0)

    too_long = budgets.request_exhausted_by(request_text)
    if too_long is not None:
        print(service.printable_answer(service.budget_response(None, too_long)))
        sys.exit(0)

    # Counted before the text is read as JSON, because the reader that
    # reads it calls itself once per array and once per object: a
    # request written to nest thousands deep would exhaust the
    # interpreter in there, with nothing printed and nothing said.
    too_deep = service.REQUEST_NESTING.refusal_for(request_text)
    if too_deep is not None:
        print(service.printable_answer(too_deep.response_for(None)))
        sys.exit(0)

    try:
        request = json.loads(request_text)
    except json.JSONDecodeError as error:
        print(service.printable_answer(_unreadable_text(error).response_for(None)))
        sys.exit(0)
    except ValueError as error:
        print(service.printable_answer(_unreadable_number(error).response_for(None)))
        sys.exit(0)

    print(service.answer_text(request, budgets))
    sys.exit(0)


def _read_at_most(args: list[str], characters_wanted: int) -> str:
    """At most `characters_wanted` characters of the request, from the
    file named on the command line or from standard input.

    Bounded here, at the one place a request enters this tool, so that a
    request too large to answer is never held in memory whole to be
    refused afterwards. A character is one byte or more, so reading one
    character past what this tool reads in bytes is always enough to
    know that a request is too long.
    """
    if len(args) >= 2 and args[0] == "--request":
        with pathlib.Path(args[1]).open(encoding="utf-8") as sent:
            return sent.read(characters_wanted)
    return sys.stdin.read(characters_wanted)


def _unreadable_bytes(error: UnicodeDecodeError) -> service.MalformedRequest:
    """The answer to bytes this command cannot read as text at all.

    Answered rather than reported as a failure of the tool, for the same
    reason text that is not JSON is: a client that sent bytes of another
    encoding wrote a bad request and is owed the place they stop being
    readable.
    """
    return service.MalformedRequest.not_readable_as_json(
        f"the bytes sent are not UTF-8 text ({error.reason})",
        f" at byte {error.start}",
    )


def _unreadable_number(error: ValueError) -> service.MalformedRequest:
    """The answer to a request whose own JSON writes a number longer
    than the reader that reads the request turns into a number.

    Answered rather than reported as a failure of the tool, for the same
    reason text that is not JSON is. It is a refusal of its own and not
    the one a program's over-long literal gets: that one stands at a
    line and column of the source, and this number is written in the
    request around the source, which has no lines of its own to open.
    The caller is told what this command reads, and not what the
    interpreter suggests doing about it.
    """
    return service.MalformedRequest.about(
        "request",
        "the text sent to this tool writes a number with more digits than "
        "this command reads as one number: it reads its request with a JSON "
        "reader that turns every number in the text into a number, and the "
        f"interpreter it runs on reads at most {sys.get_int_max_str_digits()} "
        "digits as one; write every number of the request itself with fewer "
        "digits than that, and write a program's own long integers inside "
        "the 'source' field, as the text of a program, where this tool reads "
        f"an integer literal of up to {LITERAL_DIGITS.maximum} digits",
    )


def _unreadable_text(error: json.JSONDecodeError) -> service.MalformedRequest:
    """The answer to text this command cannot read as a request.

    The command answers it rather than reporting that the tool failed:
    a client that sent nothing, or stopped partway, wrote a bad request
    and is owed the place its text stopped at, not the news that the
    tool is broken. The answer carries the same category every other
    unreadable field carries, built in the one place that builds it.
    """
    return service.MalformedRequest.not_readable_as_json(
        error.msg, f" at line {error.lineno} column {error.colno}"
    )


if __name__ == "__main__":
    main()
