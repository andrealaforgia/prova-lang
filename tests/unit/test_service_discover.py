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
        "parse": "unavailable",
        "format": "unavailable",
        "verify": "unavailable",
        "build": "unavailable",
    }


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


def test_discover_makes_no_verification_proof_or_build_claim():
    text = json.dumps(service.handle(DISCOVER)).lower()

    for word in ("verified", "proved", "built", "holds"):
        assert word not in text
