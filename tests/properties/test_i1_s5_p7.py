"""I1.S5.P7 / I1.S5.B5: both explicitly specified declarations that omit the
mandatory `examples` clause are rejected by `check`, `examples` and
`evaluate` through the public `prova` command, as well-formed JSON with a
structured diagnostic naming the missing examples clause, no traceback, a
non-crash exit and no successful result.
"""

from __future__ import annotations

import pytest

from _i1_s5_b5_fixtures import (
    OPERATIONS,
    P7_ENSURES,
    P7_PLAIN,
    assert_missing_examples_rejection,
    call,
    request,
)

SOURCES = {"plain": P7_PLAIN, "ensures-no-examples": P7_ENSURES}


@pytest.mark.parametrize("operation", OPERATIONS)
@pytest.mark.parametrize("name", SOURCES)
def test_p7_missing_examples_is_a_structured_rejection(name, operation):
    req = request(operation, SOURCES[name], "sole", arg=0)
    outcome = call(req)
    assert_missing_examples_rejection(operation, *outcome, where=f"{name}/{operation}")
