"""I1.S6.P6: syntax-aware comparison of the protected reservation source.

Complements the whitespace-collapsing comparison of the whole section:
here the code block itself is read as tokens with `;` comments removed
(comments carry no semantics), so only token content and order matter, and
the source the S6 checks execute (P7/P8) is shown to be that same protected
source at the baseline, not something regenerated from the candidate.
"""

from __future__ import annotations

import re

from _i1_s6_fixtures import (
    BASELINE_SHA,
    load_reservation_source,
    spec_text_at,
)
from _prova_client import _extract_reservation_source, _tokenize


def _tokens_without_comments(source: str) -> list[str]:
    # A quoted string is matched first so a ';' inside it is kept.
    return _tokenize(re.sub(r'("(?:[^"\\]|\\.)*")|;[^\n]*', lambda m: m.group(1) or "", source))


def _table_rows(section: str) -> list[list[str]]:
    return [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in section.splitlines()
        if line.strip().startswith("|")
    ]


def test_p6_baseline_source_has_the_expected_shape():
    # Positive control: the baseline is non-trivial, so an equality check on
    # it cannot pass vacuously on two empty extractions.
    tokens = _tokens_without_comments(_extract_reservation_source(spec_text_at(BASELINE_SHA)))
    assert len(tokens) > 100
    assert tokens.count("defn") >= 3
    assert "step" in tokens and "Reservation" in tokens


def test_p6_candidate_source_tokens_equal_baseline_tokens():
    baseline = _tokens_without_comments(_extract_reservation_source(spec_text_at(BASELINE_SHA)))
    candidate = _tokens_without_comments(load_reservation_source())
    assert candidate == baseline


def test_p6_executed_source_is_the_baseline_source_ignoring_formatting():
    executed = _tokens_without_comments(load_reservation_source())
    baseline = _tokens_without_comments(_extract_reservation_source(spec_text_at(BASELINE_SHA)))
    assert executed == baseline, "P7/P8 exercise a reservation source that differs from the protected example"


def test_p6_transition_table_cells_equal_baseline_cells():
    from _i1_s6_fixtures import protected_region, working_tree_spec_text

    baseline = _table_rows(protected_region(spec_text_at(BASELINE_SHA)))
    candidate = _table_rows(protected_region(working_tree_spec_text()))
    assert len(baseline) >= 7, "expected a header, separator and six transition rows"
    assert candidate == baseline
