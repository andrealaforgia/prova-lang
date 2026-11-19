"""A build refuses a destination that is not a regular file without
reading it.

What stood under the name was read before it was refused, and reading a
named pipe waits for a writer that never comes: a build into an
existing pipe printed nothing at all, answered nothing, and was still
blocked long after the budget the caller lowered had passed. A pipe is
not the only name that cannot be read as a file -- a directory, a
socket, a device are others -- and none of them is an artefact this
tool may replace, so what stands there is now inspected by its kind and
refused without being opened.

Every case drives the real command with a bounded timeout, so a
destination that blocks again fails these tests instead of hanging
them. The pair of each refusal is a build into a free name, and one
over a regular file the request authorises replacing, which must still
be written.
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import socket

import pytest

from _f22_fixtures import ask
from _f24_fixtures import FILE_EXISTS, REFUSED, categories_of, reasons_of

# Long enough for a build of the program below, which takes about a
# second, and far short of a wait for a writer that never comes.
A_BOUNDED_WAIT = 30.0

A = "=>"

CONSTANT_ZERO = (
    "(defn zero\n"
    "  (sig () -> Int ! pure)\n"
    f"  (examples (example (zero) {A} 0))\n"
    "  0)\n"
)

THE_NAME = "generated.py"


def _build_into(directory: pathlib.Path, replace: object = None) -> dict:
    request = {
        "operation": "build",
        "source": CONSTANT_ZERO,
        "entry": "zero",
        "output_directory": str(directory),
        "output_name": THE_NAME,
    }
    if replace is not None:
        request["replace"] = replace
    return ask(request, timeout=A_BOUNDED_WAIT)


@pytest.fixture
def directory(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path


def _a_pipe_at(directory: pathlib.Path) -> pathlib.Path:
    path = directory / THE_NAME
    os.mkfifo(path)
    return path


def test_a_pipe_at_the_name_is_refused_instead_of_read(directory):
    pipe = _a_pipe_at(directory)

    answer = _build_into(directory)

    assert answer["status"] == REFUSED, answer
    assert categories_of(answer) == {FILE_EXISTS}, answer
    assert pipe.is_fifo(), "the pipe itself was changed by a refused build"
    assert sorted(p.name for p in directory.iterdir()) == [THE_NAME], list(
        directory.iterdir()
    )


def test_a_pipe_the_request_authorises_replacing_is_refused_too(directory):
    pipe = _a_pipe_at(directory)

    answer = _build_into(directory, replace=True)

    assert answer["status"] == REFUSED, answer
    assert categories_of(answer) == {FILE_EXISTS}, answer
    assert "replac" in reasons_of(answer), answer
    assert pipe.is_fifo(), "the pipe itself was changed by a refused build"


def test_the_refusal_says_what_stands_there(directory):
    _a_pipe_at(directory)

    answer = _build_into(directory)

    assert THE_NAME in reasons_of(answer), answer
    assert "Nothing was written" in reasons_of(answer), answer


def test_a_directory_at_the_name_is_refused_as_well(directory):
    (directory / THE_NAME).mkdir()

    answer = _build_into(directory)

    assert answer["status"] == REFUSED, answer
    assert categories_of(answer) == {FILE_EXISTS}, answer
    assert (directory / THE_NAME).is_dir(), "the directory was changed"


def test_a_socket_at_the_name_is_refused_as_well(directory):
    bound = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    stood_in = os.getcwd()
    try:
        # Bound under its plain name from inside the directory: the
        # whole path of a temporary directory is longer than a socket
        # name may be.
        os.chdir(directory)
        bound.bind(THE_NAME)
        os.chdir(stood_in)

        answer = _build_into(directory)
    finally:
        os.chdir(stood_in)
        bound.close()

    assert answer["status"] == REFUSED, answer
    assert categories_of(answer) == {FILE_EXISTS}, answer


def test_a_free_name_in_the_same_directory_is_still_written(directory):
    answer = _build_into(directory)

    assert answer["status"] == "completed", answer
    written = (directory / THE_NAME).read_text(encoding="utf-8")
    assert "def zero" in written or "zero" in written, written[:200]


def test_a_regular_file_the_request_authorises_replacing_is_still_replaced(directory):
    standing = directory / THE_NAME
    standing.write_text("what stood here before\n", encoding="utf-8")
    before = hashlib.sha256(standing.read_bytes()).hexdigest()

    answer = _build_into(directory, replace=True)

    assert answer["status"] == "completed", answer
    assert before in str(answer["result"]), answer
    assert standing.read_text(encoding="utf-8") != "what stood here before\n"
