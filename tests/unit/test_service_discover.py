"""`discover` answers with the tool's manifest: profile, per-operation
availability, the diagnostic categories it can emit and its resource limits.
It makes no verification, proof or build claim, and every operation it
advertises as available is one the service actually answers.
"""

from __future__ import annotations

import json

from prova import service

DISCOVER = {"prova": "i1", "operation": "discover"}


def test_discover_reports_partial_core_0_profile():
    response = service.handle(DISCOVER)

    assert response["operation"] == "discover"
    assert response["status"] == "completed"
    assert response["result"]["profile"] == {"name": "core-0", "coverage": "partial"}


def test_discover_reports_each_operation_availability():
    operations = service.handle(DISCOVER)["result"]["operations"]

    assert operations == {
        "check": "available",
        "examples": "available",
        "evaluate": "available",
        "discover": "available",
        "verify": "available",
        "parse": "available",
        "format": "available",
        "build": "unavailable",
    }


def test_discover_says_what_an_available_verify_answers():
    """`verify` is advertised as available because it answers the inventory
    of obligations a program owes -- and the manifest says so, so that
    "available" is not read as a claim that the obligations were attempted.
    """
    documentation = service.handle(DISCOVER)["result"]["documentation"]

    assert "verify" in documentation, documentation
    text = documentation["verify"].lower()
    assert "not_attempted" in text and "inventory" in text, documentation["verify"]


def test_advertised_availability_matches_what_the_service_answers():
    operations = service.handle(DISCOVER)["result"]["operations"]

    for name, availability in operations.items():
        status = service.handle({"prova": "i1", "operation": name, "source": ""})["status"]
        assert (status == "unavailable") == (availability == "unavailable"), name


def test_discover_lists_diagnostic_categories_and_resource_limits():
    result = service.handle(DISCOVER)["result"]

    assert {"syntax", "precondition_violation", "unknown_operation"} <= set(
        result["diagnostic_categories"]
    )
    assert "resource_limits" in result


def test_discover_makes_no_verification_or_build_claim():
    """The manifest still claims no program verified and none built.

    Superseded in part by F18: the manifest now has to describe the four
    words an obligation can stand as, one of which is `proved`, so the
    word itself can no longer be forbidden outright. The claim it was
    there to catch is not the word but the assertion -- that this tool
    verified a program, that it built one, or that something holds -- so
    the two words naming those stay forbidden, and `proved` is allowed
    only where the manifest also says what it rests on.
    """
    manifest_text = json.dumps(service.handle(DISCOVER)).lower()

    for word in ("verified", "built", "holds"):
        assert word not in manifest_text, (
            f"WHAT: the manifest contains {word!r}. "
            "WHY: this tool verifies no program as a whole and builds none, "
            "so a reader of the manifest must not be told otherwise. "
            "HOW: reword the entry that says it."
        )

    published = service.handle(DISCOVER)["result"]["operation_schemas"]["verify"][
        "response"
    ]["fields"]
    assert "trust" in published, (
        f"WHAT: the manifest uses the word 'proved' and the fields it "
        f"publishes for a verify answer are {sorted(published)}. "
        "WHY: a reader who meets 'proved' must be able to look up what it "
        "rests on -- the solver's word, or a rule of core-0 -- before sending "
        "a single request, and the field carrying that is read from the "
        "published shape rather than found somewhere in the text. "
        "HOW: describe the field in manifest.py beside the others."
    )
