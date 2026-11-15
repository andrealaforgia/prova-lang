"""F11.B3 -- an agent writes a program without guessing: `discover`
names every type core-0 has and every operator, with the types each
operator takes and the type it answers (SPEC.md lines 98, 132, 178-189
and line 475).

Drives only the `prova` command's real JSON stdin/stdout surface. Every
expected signature is read by hand from SPEC.md's operator table in the
fixtures, never from the answer under observation.

still passes if: the published signatures were decoration nobody
enforces. tests/properties/test_f11_manifest_laws.py builds a program
per operator out of the published signature and shows the tool checks
it, and refuses the same program with an operand of another type.
"""

from __future__ import annotations

from _f11_manifest_fixtures import (
    THE_OPERATORS_AND_THEIR_TYPES,
    THE_TYPES_CORE_0_HAS,
    published_language,
)


def test_every_type_core_0_has_is_named_with_what_it_is():
    """Given the manifest, then the 3 type names core-0 has are there,
    each saying what its values are."""
    types = published_language().get("types")

    assert isinstance(types, dict) and set(types) == set(THE_TYPES_CORE_0_HAS), (
        f"the manifest names the types {sorted(types or {})}, and SPEC.md "
        f"line 98 gives core-0 {sorted(THE_TYPES_CORE_0_HAS)}. An agent that "
        "cannot read the types from the tool writes a signature by guessing."
    )
    for name, described in types.items():
        assert isinstance(described.get("what"), str) and described["what"].strip(), (
            f"the type {name!r} is named with nothing that says what it is: "
            f"{described}."
        )


def test_every_operator_is_named_with_the_types_it_takes_and_answers():
    """Given the manifest, then all 11 operators are there: `+` takes
    two `Int` and answers `Int`, `not` takes one `Bool` and answers
    `Bool`, and `=` takes two values of one and the same type."""
    operators = published_language().get("operators")
    expected = {name: (args, answer) for name, args, answer in THE_OPERATORS_AND_THEIR_TYPES}

    assert isinstance(operators, dict) and set(operators) == set(expected), (
        f"the manifest names the operators {sorted(operators or {})}, and "
        f"SPEC.md lines 178-189 give core-0 {sorted(expected)}. An operator "
        "an agent cannot look up is an undocumented API it must guess."
    )
    for name, (argument_types, answer_type) in expected.items():
        published = operators[name]
        assert published.get("result") == answer_type, (
            f"the manifest says {name!r} answers "
            f"{published.get('result')!r} and SPEC.md lines 178-189 say "
            f"{answer_type!r}."
        )
        arguments = published.get("arguments")
        assert isinstance(arguments, list), (
            f"the manifest gives {name!r} the arguments {arguments!r}, which "
            "is not a list of the types it takes, one per argument."
        )
        if argument_types is not None:
            assert arguments == list(argument_types), (
                f"the manifest says {name!r} takes {arguments} and SPEC.md "
                f"lines 178-189 say {list(argument_types)}."
            )
            continue
        assert len(arguments) == 2 and arguments[0] == arguments[1], (
            f"the manifest says {name!r} takes {arguments}, and SPEC.md line "
            "182 says two values of the same core type, so both places carry "
            "one and the same name."
        )
        assert arguments[0] not in THE_TYPES_CORE_0_HAS, (
            f"the manifest fixes both arguments of {name!r} to "
            f"{arguments[0]!r}, and SPEC.md line 182 allows any core type as "
            "long as both are the same."
        )
        where = published.get("where") or {}
        assert arguments[0] in where and where[arguments[0]].strip(), (
            f"the manifest writes the arguments of {name!r} as "
            f"{arguments[0]!r} and says nowhere what that name stands for: "
            f"{published}. An agent reading it has to guess."
        )


def test_no_operator_is_published_over_a_type_the_manifest_never_names():
    """Given the published operators, then every fixed type name in a
    signature is one of the 3 types the manifest names."""
    language = published_language()
    types = set(language.get("types") or {})

    for name, published in (language.get("operators") or {}).items():
        where = published.get("where") or {}
        for place in list(published.get("arguments") or []) + [published.get("result")]:
            assert place in types or place in where, (
                f"the operator {name!r} is published over the type "
                f"{place!r}, which is neither one of the types the manifest "
                f"names ({sorted(types)}) nor a name it explains. A "
                "signature over a type an agent cannot look up cannot be "
                "written down."
            )
