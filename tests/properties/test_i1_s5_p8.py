"""I1.S5.P8 / I1.S5.B5: missing-examples rejection stays controlled across
every optional-contract combination, body shape, declaration placement and
operation (108 generated cases), including multi-function programs whose
evaluate request selects the valid helper rather than the malformed `f`.
"""

from __future__ import annotations

import pytest

from _i1_s5_b5_fixtures import (
    BODIES,
    CONTRACTS,
    OPERATIONS,
    PLACEMENTS,
    assert_missing_examples_rejection,
    call,
    case_id,
    declaration,
    matrix,
    place,
    request,
)

CASES = matrix()


def test_p8_generator_covers_the_declared_domain_and_omits_only_examples():
    assert len(CASES) == 4 * 3 * 3 * 3 == 108
    assert len(set(CASES)) == 108
    for contract, body, _placement, _op in CASES:
        broken = declaration(contract, body, with_examples=False)
        repaired = declaration(contract, body, with_examples=True)
        assert "examples" not in broken
        if len(CONTRACTS[contract]) == 2:
            assert broken.index("(requires") < broken.index("(ensures")
        # the repair inserts the examples clause and changes nothing else
        assert repaired.replace(" (examples (example (f 0) => %d))" % BODIES[body][1], "") == broken


@pytest.mark.parametrize("case", CASES, ids=case_id)
def test_p8_missing_examples_rejected_in_every_combination(case):
    contract, body, placement, operation = case
    source = place(declaration(contract, body, with_examples=False), placement)
    outcome = call(request(operation, source, placement))
    assert_missing_examples_rejection(operation, *outcome, where=case_id(case))
