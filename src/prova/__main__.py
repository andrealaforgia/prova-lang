"""Reads one JSON request from stdin (or --request FILE), writes one JSON
response to stdout."""

from __future__ import annotations

import json
import os
import pathlib
import sys

from prova import service
from prova.budgets import Budgets, UnreadableBudget


def main() -> None:
    args = sys.argv[1:]
    budgets = Budgets.from_environment(os.environ)
    if isinstance(budgets, UnreadableBudget):
        print(json.dumps(service.budgets_refused(budgets)))
        sys.exit(0)

    try:
        request_text = _read_at_most(args, budgets.request_ceiling() + 1)
    except UnicodeDecodeError as error:
        print(json.dumps(_unreadable_bytes(error).response_for(None)))
        sys.exit(0)

    too_long = budgets.request_exhausted_by(request_text)
    if too_long is not None:
        print(json.dumps(service.budget_response(None, too_long)))
        sys.exit(0)

    try:
        request = json.loads(request_text)
    except json.JSONDecodeError as error:
        print(json.dumps(_unreadable_text(error).response_for(None)))
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
