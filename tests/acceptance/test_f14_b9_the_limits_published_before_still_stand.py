"""F14.B9 -- the two limits R1 published are unchanged, and the four
budgets stand beside them in the same block.

A caller that already reads the nesting limit and the evaluation depth
from the resource limits finds them where they were, with the numbers
they had. The budgets join them rather than replacing them or being
published somewhere else of their own.

still passes if: the budgets were published with no number in them. The
tests of F14.B1 read every number and require each one.
"""

from __future__ import annotations

from _f14_budget_fixtures import BUDGET_NAMES, RESOURCE_EXHAUSTED, discover


def test_the_nesting_and_evaluation_limits_are_what_they_were():
    """Given a caller that read the nesting limit of 128 forms and the
    evaluation depth of 160 steps before this change, when it reads the
    manifest now, then both are still there with the same numbers, the
    same categories and the same status.
    """
    limits = discover()["result"]["resource_limits"]["limits"]

    assert limits["expression_nesting"]["maximum"] == 128, (
        f"the nesting limit is now "
        f"{limits['expression_nesting'].get('maximum')!r}, and callers sized "
        "their generators against 128: a limit that moves without being asked "
        "for breaks every caller that read it."
    )
    assert limits["expression_nesting"]["category"] == "nesting_limit_exceeded", limits
    assert limits["evaluation_depth"]["maximum"] == 160, (
        f"the evaluation depth is now "
        f"{limits['evaluation_depth'].get('maximum')!r}, and callers sized "
        "their programs against 160."
    )
    assert limits["evaluation_depth"]["category"] == "evaluation_depth_exceeded", limits
    for name in ("expression_nesting", "evaluation_depth"):
        assert limits[name]["status"] == RESOURCE_EXHAUSTED, (
            f"the {name!r} limit says a text past it is answered "
            f"{limits[name].get('status')!r}: {limits[name]}. Every budget and "
            "every limit this tool declares is answered with one status."
        )


def test_the_budgets_stand_in_the_same_block_as_the_limits():
    """Given a caller reading the resource limits, when it looks for
    what this tool declares, then it finds the 2 limits and the 4
    budgets of every operation in that one block, and the block still
    says it is enforced.
    """
    resource_limits = discover()["result"]["resource_limits"]

    assert resource_limits.get("enforced") is True, (
        f"the resource limits say enforced={resource_limits.get('enforced')!r}: "
        "a caller reading that nothing is enforced has no number to stay "
        "under."
    )
    assert sorted(resource_limits["limits"]) == [
        "evaluation_depth",
        "expression_nesting",
    ], resource_limits["limits"]
    budgets = resource_limits.get("budgets") or {}
    assert budgets, (
        f"the resource limits carry no budgets: {sorted(resource_limits)}. The "
        "input, time, memory and answer budgets are read from the same block "
        "as the nesting limit and the evaluation depth, so a caller reads "
        "everything this tool declares in one place."
    )
    for operation, stated in sorted(budgets.items()):
        assert sorted(stated) == sorted(BUDGET_NAMES), (
            f"the {operation!r} operation states {sorted(stated)} beside the "
            f"limits, expected {sorted(BUDGET_NAMES)}."
        )
