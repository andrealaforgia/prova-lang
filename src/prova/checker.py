"""Whole-program static checking: declarations, scope and nominal typing.

Reports every referenced type, constructor and name as it resolves them,
and infers the nominal type of every expression (including both branches
of an `if` and every `match` clause, reached or not) to catch a type
error anywhere in the program, not only ones a call happens to exercise.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import syntax
from prova.values import ConstructorValue

BUILTIN_TYPES = {"Unit", "Bool", "Int"}
NUMERIC_OPERATORS = {"+", "-", "*"}
COMPARISON_OPERATORS = {"<", "<=", ">", ">="}
BOOLEAN_OPERATORS = {"and", "or", "not"}


@dataclass(frozen=True)
class Diagnostic:
    category: str
    reason: str
    location: tuple[int, int] | None = None


def check_program(program: syntax.Program) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    known_types = BUILTIN_TYPES | set(program.types)

    def check_type_name(type_name: str, where: str) -> None:
        if type_name not in known_types:
            diagnostics.append(
                Diagnostic("unbound_type", f"unknown type {type_name!r} in {where}")
            )

    for type_decl in program.types.values():
        if isinstance(type_decl, syntax.RecordType):
            for field_name, field_type in type_decl.fields:
                check_type_name(field_type, f"record {type_decl.name!r} field {field_name!r}")
        elif isinstance(type_decl, syntax.UnionType):
            for variant in type_decl.variants:
                for field_name, field_type in variant.fields:
                    check_type_name(
                        field_type,
                        f"union {type_decl.name!r} variant {variant.name!r} field {field_name!r}",
                    )

    for function in program.functions.values():
        for param_name, param_type in function.signature.params:
            check_type_name(param_type, f"function {function.name!r} parameter {param_name!r}")
        check_type_name(function.signature.return_type, f"function {function.name!r} return type")

        params_env = {name: type_ for name, type_ in function.signature.params}
        for clause_expr in function.requires:
            _check_contract_clause_is_bool(clause_expr, params_env, program, diagnostics)

        return_type = function.signature.return_type
        body_type = _infer(function.body, params_env, program, diagnostics)
        if body_type is not None and body_type != return_type:
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    f"function {function.name!r} body has type {body_type}, "
                    f"declared return type {return_type}",
                    (function.body.line, function.body.column),
                )
            )

        result_env = dict(params_env)
        result_env["result"] = return_type
        for clause_expr in function.ensures:
            _check_contract_clause_is_bool(clause_expr, result_env, program, diagnostics)

        for ordinal, example in enumerate(function.examples):
            where = f"function {function.name!r} example {ordinal}"
            for arg in example.args:
                _check_value(arg, program, where, diagnostics)
            _check_value(example.expected, program, where, diagnostics)

    return diagnostics


def _check_contract_clause_is_bool(
    expr: object, env: dict[str, str], program: syntax.Program, diagnostics: list[Diagnostic]
) -> None:
    clause_type = _infer(expr, env, program, diagnostics)
    if clause_type is not None and clause_type != "Bool":
        diagnostics.append(
            Diagnostic(
                "type_mismatch",
                f"contract clause expects Bool, got {clause_type}",
                (expr.line, expr.column),
            )
        )


def _check_value(value: object, program: syntax.Program, where: str, diagnostics: list[Diagnostic]) -> None:
    if not isinstance(value, ConstructorValue):
        return
    if syntax.resolve_constructor_fields(value.constructor, program) is None:
        diagnostics.append(
            Diagnostic("unbound_constructor", f"unknown constructor {value.constructor!r} in {where}")
        )
        return
    for field_value in value.fields:
        _check_value(field_value, program, where, diagnostics)


def _field_type(type_name: str, field_name: str, program: syntax.Program) -> str | None:
    type_decl = program.types.get(type_name)
    if isinstance(type_decl, syntax.RecordType):
        fields = type_decl.fields
    elif isinstance(type_decl, syntax.UnionType):
        fields = [f for variant in type_decl.variants for f in variant.fields]
    else:
        return None
    for name, field_type in fields:
        if name == field_name:
            return field_type
    return None


_LITERAL_PATTERN_TYPES = {
    syntax.PatInt: "Int",
    syntax.PatBool: "Bool",
    syntax.PatUnit: "Unit",
}


def _constructor_signature(type_name: str, program: syntax.Program) -> dict[str, list[str]] | None:
    """Constructor key -> field types for a finitely-inhabited-by-constructors
    type; `None` for `Int` and for types with no known constructors."""
    if type_name == "Bool":
        return {"true": [], "false": []}
    if type_name == "Unit":
        return {"()": []}
    type_decl = program.types.get(type_name)
    if isinstance(type_decl, syntax.RecordType):
        return {type_decl.name: [t for _, t in type_decl.fields]}
    if isinstance(type_decl, syntax.UnionType):
        return {v.name: [t for _, t in v.fields] for v in type_decl.variants}
    return None


def _pattern_key(pattern: object) -> str | None:
    if isinstance(pattern, syntax.PatBool):
        return "true" if pattern.value else "false"
    if isinstance(pattern, syntax.PatUnit):
        return "()"
    if isinstance(pattern, syntax.PatConstructor):
        return pattern.name
    return None


def _is_wild(pattern: object) -> bool:
    return isinstance(pattern, (syntax.PatWildcard, syntax.PatVar))


def _covers(rows: list[tuple], types: list[str], program: syntax.Program) -> bool:
    """True when the pattern rows match every value of the column types."""
    if not types:
        return bool(rows)
    head_type, rest_types = types[0], types[1:]
    signature = _constructor_signature(head_type, program)
    if signature is None:
        return _covers([row[1:] for row in rows if _is_wild(row[0])], rest_types, program)
    for key, field_types in signature.items():
        specialised = []
        for row in rows:
            head = row[0]
            if _is_wild(head):
                specialised.append((syntax.PatWildcard(),) * len(field_types) + row[1:])
            elif _pattern_key(head) == key:
                sub = head.subpatterns if isinstance(head, syntax.PatConstructor) else ()
                specialised.append(tuple(sub) + row[1:])
        if not _covers(specialised, field_types + rest_types, program):
            return False
    return True


def _pattern_bindings(
    pattern: object,
    scrutinee_type: str | None,
    program: syntax.Program,
    diagnostics: list[Diagnostic],
    location: tuple[int, int],
) -> dict[str, str]:
    if isinstance(pattern, syntax.PatVar):
        return {pattern.name: scrutinee_type} if scrutinee_type is not None else {}
    literal_type = _LITERAL_PATTERN_TYPES.get(type(pattern))
    if literal_type is not None:
        if scrutinee_type is not None and scrutinee_type != literal_type:
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    f"{literal_type} literal pattern against scrutinee of type {scrutinee_type}",
                    location,
                )
            )
        return {}
    if isinstance(pattern, syntax.PatConstructor):
        resolved = syntax.resolve_constructor(pattern.name, program)
        if resolved is None:
            diagnostics.append(
                Diagnostic(
                    "unbound_constructor",
                    f"unknown constructor {pattern.name!r} in match pattern",
                    location,
                )
            )
            for subpattern in pattern.subpatterns:
                _pattern_bindings(subpattern, None, program, diagnostics, location)
            return {}
        owning_type, fields = resolved
        if scrutinee_type is not None and owning_type != scrutinee_type:
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    f"match pattern {pattern.name!r} has type {owning_type}, "
                    f"scrutinee has type {scrutinee_type}",
                    location,
                )
            )
        if len(fields) != len(pattern.subpatterns):
            diagnostics.append(
                Diagnostic(
                    "arity_mismatch",
                    f"match pattern {pattern.name!r} takes {len(fields)} field(s), "
                    f"got {len(pattern.subpatterns)}",
                    location,
                )
            )
        bindings: dict[str, str] = {}
        for (field_name, field_type), subpattern in zip(fields, pattern.subpatterns):
            bindings.update(_pattern_bindings(subpattern, field_type, program, diagnostics, location))
        return bindings
    return {}


def _infer(
    expr: object, env: dict[str, str], program: syntax.Program, diagnostics: list[Diagnostic]
) -> str | None:
    if isinstance(expr, syntax.IntLit):
        return "Int"
    if isinstance(expr, syntax.BoolLit):
        return "Bool"
    if isinstance(expr, syntax.UnitLit):
        return "Unit"

    if isinstance(expr, syntax.NameRef):
        if expr.name in env:
            return env[expr.name]
        diagnostics.append(
            Diagnostic("unbound_name", f"unbound name {expr.name!r}", (expr.line, expr.column))
        )
        return None

    if isinstance(expr, syntax.Let):
        local_env = dict(env)
        for name, bound_expr in expr.bindings:
            local_env[name] = _infer(bound_expr, local_env, program, diagnostics)
        return _infer(expr.body, local_env, program, diagnostics)

    if isinstance(expr, syntax.If):
        condition_type = _infer(expr.condition, env, program, diagnostics)
        if condition_type is not None and condition_type != "Bool":
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    f"'if' condition expects Bool, got {condition_type}",
                    (expr.line, expr.column),
                )
            )
        then_type = _infer(expr.then_branch, env, program, diagnostics)
        else_type = _infer(expr.else_branch, env, program, diagnostics)
        if then_type is not None and else_type is not None and then_type != else_type:
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    f"'if' branches disagree: {then_type} vs {else_type}",
                    (expr.line, expr.column),
                )
            )
            return None
        return then_type if then_type is not None else else_type

    if isinstance(expr, syntax.Match):
        scrutinee_type = _infer(expr.scrutinee, env, program, diagnostics)
        result_type: str | None = None
        disagreement = False
        diagnostics_before_patterns = len(diagnostics)
        for clause in expr.clauses:
            clause_env = dict(env)
            clause_env.update(
                _pattern_bindings(
                    clause.pattern, scrutinee_type, program, diagnostics, (expr.line, expr.column)
                )
            )
            clause_type = _infer(clause.body, clause_env, program, diagnostics)
            if clause_type is None:
                continue
            if result_type is None:
                result_type = clause_type
            elif result_type != clause_type:
                disagreement = True
        patterns_well_formed = len(diagnostics) == diagnostics_before_patterns
        if (
            scrutinee_type is not None
            and patterns_well_formed
            and not _covers([(c.pattern,) for c in expr.clauses], [scrutinee_type], program)
        ):
            diagnostics.append(
                Diagnostic(
                    "non_exhaustive_match",
                    f"'match' does not cover every value of type {scrutinee_type}",
                    (expr.line, expr.column),
                )
            )
        if disagreement:
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    "'match' clauses disagree on result type",
                    (expr.line, expr.column),
                )
            )
            return None
        return result_type

    if isinstance(expr, syntax.FieldAccess):
        target_type = _infer(expr.target, env, program, diagnostics)
        if target_type is None:
            return None
        field_type = _field_type(target_type, expr.field_name, program)
        if field_type is None:
            diagnostics.append(
                Diagnostic(
                    "unbound_field",
                    f"type {target_type!r} has no field {expr.field_name!r}",
                    (expr.line, expr.column),
                )
            )
        return field_type

    if isinstance(expr, syntax.OperatorCall):
        arg_types = [_infer(arg, env, program, diagnostics) for arg in expr.args]
        return _check_operator(expr, arg_types, diagnostics)

    if isinstance(expr, syntax.ConstructorCall):
        fields = syntax.resolve_constructor_fields(expr.name, program)
        if fields is None:
            diagnostics.append(
                Diagnostic(
                    "unbound_constructor",
                    f"unknown constructor {expr.name!r}",
                    (expr.line, expr.column),
                )
            )
            for arg in expr.args:
                _infer(arg, env, program, diagnostics)
            return None
        if len(fields) != len(expr.args):
            diagnostics.append(
                Diagnostic(
                    "arity_mismatch",
                    f"constructor {expr.name!r} takes {len(fields)} field(s), got {len(expr.args)}",
                    (expr.line, expr.column),
                )
            )
        for (field_name, field_type), arg in zip(fields, expr.args):
            arg_type = _infer(arg, env, program, diagnostics)
            if arg_type is not None and arg_type != field_type:
                diagnostics.append(
                    Diagnostic(
                        "type_mismatch",
                        f"constructor {expr.name!r} field {field_name!r} expects "
                        f"{field_type}, got {arg_type}",
                        (expr.line, expr.column),
                    )
                )
        for arg in expr.args[len(fields):]:
            _infer(arg, env, program, diagnostics)
        return syntax.resolve_constructor(expr.name, program)[0]

    if isinstance(expr, syntax.Call):
        callee = program.functions.get(expr.name)
        if callee is None:
            diagnostics.append(
                Diagnostic(
                    "unbound_name",
                    f"call to undeclared function {expr.name!r}",
                    (expr.line, expr.column),
                )
            )
            for arg in expr.args:
                _infer(arg, env, program, diagnostics)
            return None
        params = callee.signature.params
        if len(expr.args) != len(params):
            diagnostics.append(
                Diagnostic(
                    "arity_mismatch",
                    f"call to {expr.name!r} passes {len(expr.args)} argument(s), "
                    f"expected {len(params)}",
                    (expr.line, expr.column),
                )
            )
        for (param_name, param_type), arg in zip(params, expr.args):
            arg_type = _infer(arg, env, program, diagnostics)
            if arg_type is not None and arg_type != param_type:
                diagnostics.append(
                    Diagnostic(
                        "type_mismatch",
                        f"call to {expr.name!r} argument {param_name!r} expects "
                        f"{param_type}, got {arg_type}",
                        (expr.line, expr.column),
                    )
                )
        for arg in expr.args[len(params):]:
            _infer(arg, env, program, diagnostics)
        return callee.signature.return_type

    raise TypeError(f"unrecognised expression node: {expr!r}")


def _check_operator(
    expr: syntax.OperatorCall, arg_types: list[str | None], diagnostics: list[Diagnostic]
) -> str:
    op = expr.operator
    if op in NUMERIC_OPERATORS:
        for arg_type in arg_types:
            if arg_type is not None and arg_type != "Int":
                diagnostics.append(
                    Diagnostic(
                        "type_mismatch",
                        f"operator {op!r} expects Int operands, got {arg_type}",
                        (expr.line, expr.column),
                    )
                )
        return "Int"
    if op in COMPARISON_OPERATORS:
        for arg_type in arg_types:
            if arg_type is not None and arg_type != "Int":
                diagnostics.append(
                    Diagnostic(
                        "type_mismatch",
                        f"operator {op!r} expects Int operands, got {arg_type}",
                        (expr.line, expr.column),
                    )
                )
        return "Bool"
    if op == "=":
        known = [t for t in arg_types if t is not None]
        if len(set(known)) > 1:
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    f"'=' operands have different types: {known}",
                    (expr.line, expr.column),
                )
            )
        return "Bool"
    if op in BOOLEAN_OPERATORS:
        for arg_type in arg_types:
            if arg_type is not None and arg_type != "Bool":
                diagnostics.append(
                    Diagnostic(
                        "type_mismatch",
                        f"operator {op!r} expects Bool operands, got {arg_type}",
                        (expr.line, expr.column),
                    )
                )
        return "Bool"
    raise ValueError(f"unknown operator {op!r}")
