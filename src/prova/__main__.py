"""Reads one JSON request from stdin (or --request FILE), writes one JSON
response to stdout."""

from __future__ import annotations

import json
import pathlib
import sys

from prova import service


def main() -> None:
    args = sys.argv[1:]
    if len(args) >= 2 and args[0] == "--request":
        request_text = pathlib.Path(args[1]).read_text(encoding="utf-8")
    else:
        request_text = sys.stdin.read()

    try:
        request = json.loads(request_text)
    except json.JSONDecodeError as error:
        print(json.dumps({"status": "tool_failure", "reason": str(error)}))
        sys.exit(1)

    response = service.handle(request)
    print(json.dumps(response))
    sys.exit(0)


if __name__ == "__main__":
    main()
