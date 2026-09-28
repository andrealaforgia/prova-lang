"""Whole-program static checking, positive path.

I1.S1 introduces this module to accept the reservation source; it checks
that every referenced type and called function exists, with correct
arity. Nominal type inference, exhaustiveness and full diagnostic
reporting are S5's scope.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import syntax
from prova.values import ConstructorValue

BUILTIN_TYPES = {"Unit", "Bool", "Int"}


@dataclass(frozen=True)
class Diagnostic:
    category: str
    reason: str


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
        for expr in (*function.requires, *function.ensures, function.body):
            _check_expr(expr, program, function.name, diagnostics)
        for ordinal, example in enumerate(function.examples):
            where = f"function {function.name!r} example {ordinal}"
            for arg in example.args:
                _check_value(arg, program, where, diagnostics)
            _check_value(example.expected, program, where, diagnostics)

    return diagnostics


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


def _check_expr(expr: object, program: syntax.Program, function_name: str, diagnostics: list[Diagnostic]) -> None:
    if isinstance(expr, syntax.Call):
        callee = program.functions.get(expr.name)
        if callee is None:
            diagnostics.append(
                Diagnostic("unbound_name", f"call to undeclared function {expr.name!r} in {function_name!r}")
            )
        elif len(expr.args) != len(callee.signature.params):
            diagnostics.append(
                Diagnostic(
                    "arity_mismatch",
                    f"call to {expr.name!r} in {function_name!r} passes {len(expr.args)} "
                    f"argument(s), expected {len(callee.signature.params)}",
                )
            )
        for arg in expr.args:
            _check_expr(arg, program, function_name, diagnostics)
    elif isinstance(expr, (syntax.ConstructorCall, syntax.OperatorCall)):
        for arg in expr.args:
            _check_expr(arg, program, function_name, diagnostics)
    elif isinstance(expr, syntax.FieldAccess):
        _check_expr(expr.target, program, function_name, diagnostics)
    elif isinstance(expr, syntax.Let):
        for _, bound_expr in expr.bindings:
            _check_expr(bound_expr, program, function_name, diagnostics)
        _check_expr(expr.body, program, function_name, diagnostics)
    elif isinstance(expr, syntax.If):
        _check_expr(expr.condition, program, function_name, diagnostics)
        _check_expr(expr.then_branch, program, function_name, diagnostics)
        _check_expr(expr.else_branch, program, function_name, diagnostics)
    elif isinstance(expr, syntax.Match):
        _check_expr(expr.scrutinee, program, function_name, diagnostics)
        for clause in expr.clauses:
            _check_expr(clause.body, program, function_name, diagnostics)
