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
    if len(args) >= 2 and args[0] == "--request":
        request_text = pathlib.Path(args[1]).read_text(encoding="utf-8")
    else:
        request_text = sys.stdin.read()

    budgets = Budgets.from_environment(os.environ)
    if isinstance(budgets, UnreadableBudget):
        print(json.dumps(service.budgets_refused(budgets)))
        sys.exit(0)

    try:
        request = json.loads(request_text)
    except json.JSONDecodeError as error:
        print(json.dumps(_unreadable_text(error).response_for(None)))
        sys.exit(0)

    print(service.answer_text(request, budgets))
    sys.exit(0)


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
