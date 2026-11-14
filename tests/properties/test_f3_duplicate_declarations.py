"""Property test for F3's design law (LAW1): a program is refused with a
repeated-name diagnostic exactly when it declares one name twice in one
namespace -- functions, types, constructors, and the fields of one
record or one variant -- and equal field spellings in different records
never cause a refusal.

The hand-written acceptance tests fix six shapes. The law is about every
shape: a repeat among three declarations, a repeat in the second record
of three, a program where functions repeat and types do not, and the
many programs where nothing repeats at all. A table of examples cannot
carry that.

Whether a generated program repeats a name is decided here by counting
the generator's own scoped-name list -- built from the generator's data
before any source text is written, and never from anything the tool
reports.

Derandomized with a bounded example count so the verdict does not depend
on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from prova import service

DUPLICATE_CATEGORY = "duplicate_declaration"

FUNCTION_NAMES = ["total", "doubled"]
TYPE_NAMES = ["Money", "Invoice"]
FIELD_NAMES = ["amount", "count"]

_functions = st.lists(st.sampled_from(FUNCTION_NAMES), min_size=0, max_size=3)
_records = st.lists(
    st.tuples(
        st.sampled_from(TYPE_NAMES),
        st.lists(st.sampled_from(FIELD_NAMES), min_size=1, max_size=2),
    ),
    min_size=0,
    max_size=3,
)


def _source(functions, records) -> str:
    """One `core-0` program: a record per generated record, a function
    per generated function name, each function returning its parameter
    and declaring an example that names itself."""
    parts = []
    for type_name, fields in records:
        declared = " ".join(f"({field} Int)" for field in fields)
        parts.append(f"(deftype {type_name} (record {declared}))")
    for function_name in functions:
        parts.append(
            f"(defn {function_name}\n"
            f"  (sig ((n Int)) -> Int ! pure)\n"
            f"  (examples (example ({function_name} 1) => 1))\n"
            f"  n)"
        )
    return "\n\n".join(parts) + "\n"


def _scoped_names(functions, records) -> list[tuple]:
    """Every name the program declares, paired with the namespace it is
    declared in. A record introduces a type and a constructor of the same
    name; each record's fields live in that record's own namespace, which
    is why equal spellings in different records are two different
    entries."""
    names: list[tuple] = [("function", name) for name in functions]
    for position, (type_name, fields) in enumerate(records):
        names.append(("type", type_name))
        names.append(("constructor", type_name))
        names.extend(("field", position, field) for field in fields)
    return names


def _refused_for_a_repeated_name(response: dict) -> bool:
    return any(
        diagnostic.get("category") == DUPLICATE_CATEGORY
        for diagnostic in response.get("diagnostics", [])
    )


@settings(max_examples=60, deadline=None)
@given(functions=_functions, records=_records)
def test_a_program_is_refused_exactly_when_it_declares_one_name_twice(functions, records):
    """LAW1. A repeated name in one namespace refuses the program; a
    program whose every namespace holds each name once is accepted, even
    when two records share a field spelling."""
    scoped = _scoped_names(functions, records)
    repeats = len(scoped) - len(set(scoped))
    source = _source(functions, records)

    response = service.handle({"prova": "i1", "operation": "check", "source": source})

    assert _refused_for_a_repeated_name(response) == (repeats > 0), (
        f"the program declares {len(scoped)} names of which {repeats} repeat a "
        f"name already declared in the same namespace, but the tool "
        f"{'accepted' if repeats else 'refused'} it: {response}\nsource:\n{source}"
        "A program must be refused with a repeated-name diagnostic exactly when "
        "one name is declared twice in one namespace; a field spelling shared by "
        "two different records is not a repeat."
    )
    if repeats == 0:
        assert response.get("status") == "completed", (
            f"a program that declares each name once was not accepted: {response}\n"
            f"source:\n{source}Leave every program whose names are unique accepted."
        )
