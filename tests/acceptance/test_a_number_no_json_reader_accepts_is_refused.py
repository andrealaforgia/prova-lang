"""A request carrying a number JSON cannot write is refused, and no
answer this tool prints carries one.

`1e999` is a number a JSON reader accepts and turns into infinity, which
JSON itself cannot write back: the tool used to echo it into its answer
and print `{"operation": Infinity, ...}`, which a strict reader of the
answer rejects, so a caller that sent one readable request got back text
it could not read at all.

Every case drives the real command over its stdin and stdout and reads
the answer with a strict JSON reader -- one that refuses `Infinity`,
`-Infinity` and `NaN`, as a reader in another language does -- because
the defect is exactly a text Python's own reader accepts and other
readers do not. Each refusal is paired with the finite number beside it,
which must still be answered as it always was.
"""

from __future__ import annotations

import json

from _r1_robustness_fixtures import run, run_text

MALFORMED_REQUEST = "malformed_request"
INVALID_INPUT = "invalid_input"

PROGRAM = "(defn f (sig () -> Int ! pure) (examples (example (f) => 1)) 1)"

# The three texts a JSON reader of another language refuses outright and
# Python's own reader turns into a float, and the two arithmetic texts
# that overflow to the same values while being ordinary JSON numbers.
NOT_A_JSON_NUMBER = ("Infinity", "-Infinity", "NaN", "1e999", "-1e999")


def _strictly_read(written: str, why: str) -> dict:
    def refuse(constant: str) -> object:
        raise AssertionError(
            f"the answer to {why} carries {constant}, which JSON has no "
            f"number for: a caller reading the answer with any reader that "
            f"holds to JSON gets no outcome at all. The answer was {written!r}"
        )

    return json.loads(written, parse_constant=refuse)


def _refused(sent: str, why: str) -> dict:
    outcome = run_text(sent)
    assert outcome.exit_code == 0, (outcome.exit_code, outcome.stderr[-400:])
    assert outcome.stderr.strip() == "", outcome.stderr[-400:]
    answer = _strictly_read(outcome.stdout, why)
    assert answer["status"] == INVALID_INPUT, answer
    assert [d["category"] for d in answer["diagnostics"]] == [MALFORMED_REQUEST], answer
    return answer


def test_the_operation_field_holding_a_number_json_cannot_write_is_refused():
    for written in NOT_A_JSON_NUMBER:
        answer = _refused(
            '{"operation": %s}' % written, f"an operation field holding {written}"
        )
        assert answer["operation"] is None, answer
        assert "operation" in answer["diagnostics"][0]["reason"], answer


def test_a_finite_number_in_the_operation_field_is_answered_as_before():
    outcome = run({"prova": "i1", "operation": 5})
    answer = outcome.assert_answered("an operation field holding 5")

    assert answer == {
        "operation": 5,
        "status": "unavailable",
        "diagnostics": [
            {
                "category": "unknown_operation",
                "reason": "operation 5 is not recognized",
            }
        ],
    }, answer


def test_every_field_of_a_request_is_read_for_such_a_number():
    positions = {
        "source": '{"operation": "check", "source": 1e999}',
        "function": '{"operation": "evaluate", "source": "%s", '
        '"function": 1e999, "arguments": []}' % PROGRAM,
        "arguments": '{"operation": "evaluate", "source": "%s", '
        '"function": "f", "arguments": [1e999]}' % PROGRAM,
        "budgets": '{"operation": "check", "source": "%s", '
        '"budgets": {"operation_time": 1e999}}' % PROGRAM,
        "entry": '{"operation": "build", "source": "%s", "entry": NaN}' % PROGRAM,
        "a field this tool has no name for": '{"operation": "check", '
        '"source": "%s", "whatever": [[{"deep": -1e999}]]}' % PROGRAM,
    }
    for field, sent in positions.items():
        answer = _refused(sent, f"a number JSON cannot write in {field}")
        reason = answer["diagnostics"][0]["reason"]
        assert "JSON" in reason, (field, reason)


def test_the_same_requests_with_finite_numbers_are_not_refused_for_this():
    settled = run_text(
        '{"operation": "check", "source": "%s", "budgets": {"operation_time": 10000}}'
        % PROGRAM
    ).assert_answered("a request whose numbers are finite")

    assert settled["status"] == "completed", settled
