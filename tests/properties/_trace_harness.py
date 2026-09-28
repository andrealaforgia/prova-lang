"""Execution-tracing launcher for I1 property tests.

Not a test module. Run as `python _trace_harness.py TRACE_FILE ENTRY` with the
request on stdin. ENTRY is `prova` (the real public command's own entry
point, `prova.__main__.main`) or the path of a control script, which is run
under module name `__control__` so its functions are traced like candidate
functions. Before any candidate code is imported it installs

* a `sys.addaudithook` hook that records every process-spawn event and every
  filesystem-mutating event (write/create/truncate open, mkdir, remove,
  rename, rmdir, chmod, symlink, copy/move/rmtree ...) with its paths, and
* a `sys.setprofile`/`threading.setprofile` hook that records every Python
  function entered in `prova*` or `__control__` modules from the moment the
  entry point is invoked (package import at start-up is not recorded),

so a create-then-delete, a write-then-restore or an entry into work that is
later concealed is still recorded, however briefly it lasted. The trace is
written as JSON to TRACE_FILE; stdin/stdout/stderr and the exit code of the
entry point pass through unchanged.

Coverage limit: only Python-level function entries and CPython audit events
are seen. Native code that mutates files without raising an audit event is
not observed; child processes are not followed but their creation is an
audit event, so any use of one is recorded.
"""

from __future__ import annotations

import json
import os
import runpy
import sys
import threading

TRACE_FILE = sys.argv[1]
ENTRY = sys.argv[2]

MUTATING_EVENTS = {
    "os.mkdir", "os.remove", "os.rename", "os.rmdir", "os.chmod", "os.chown",
    "os.truncate", "os.symlink", "os.link", "os.utime", "os.mkfifo", "os.mknod",
    "shutil.copyfile", "shutil.copymode", "shutil.copystat", "shutil.copytree",
    "shutil.rmtree", "shutil.move", "shutil.chown", "shutil.unpack_archive",
    "os.setxattr", "os.removexattr",
}
SPAWN_EVENTS = {
    "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn",
    "os.fork", "os.forkpty", "ctypes.dlopen",
}
WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND

events: list[list] = []
calls: set[tuple[str, str]] = set()
recording = True


def _as_path(value):
    if isinstance(value, bytes):
        return os.path.abspath(os.fsdecode(value))
    if isinstance(value, (str, os.PathLike)):
        return os.path.abspath(os.fspath(value))
    return None


def _audit(event, args):
    if not recording:
        return
    if event == "open":
        path, mode, flags = args
        writes = isinstance(flags, int) and bool(flags & WRITE_FLAGS)
        if isinstance(mode, str) and any(c in mode for c in "wax+"):
            writes = True
        if writes and _as_path(path):
            events.append(["open-write", [_as_path(path)]])
    elif event in MUTATING_EVENTS:
        events.append([event, [p for p in map(_as_path, args) if p]])
    elif event in SPAWN_EVENTS:
        events.append([event, []])


def _profile(frame, kind, arg):
    if kind == "call":
        module = frame.f_globals.get("__name__", "")
        if module.startswith("prova") or module == "__control__":
            calls.add((module, frame.f_code.co_qualname))


def main() -> int:
    global recording
    sys.addaudithook(_audit)
    code = 0
    try:
        if ENTRY == "prova":
            # Importing the package is start-up, not request handling: function
            # entries are recorded from the moment the entry point is invoked.
            import prova.__main__ as entry
            sys.setprofile(_profile)
            threading.setprofile(_profile)
            entry.main()
        else:
            sys.setprofile(_profile)
            threading.setprofile(_profile)
            runpy.run_path(ENTRY, run_name="__control__")
    except SystemExit as stop:
        code = stop.code if isinstance(stop.code, int) else (0 if stop.code is None else 1)
    finally:
        sys.setprofile(None)
        threading.setprofile(None)
        recording = False
        with open(TRACE_FILE, "w", encoding="utf-8") as out:
            json.dump({"calls": sorted(calls), "events": events}, out)
    return code


if __name__ == "__main__":
    sys.exit(main())
