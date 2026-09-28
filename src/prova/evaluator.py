"""Call-by-value evaluator for core-0, with contract checking on every
user call, entry and nested, including calls inside contracts."""

from __future__ import annotations

from prova import syntax
from prova.values import UNIT, ConstructorValue, Unit


class PreconditionViolation(Exception):
    def __init__(self, function_name: str):
        super().__init__(f"precondition violated calling {function_name!r}")
        self.function_name = function_name


class PostconditionViolation(Exception):
    def __init__(self, function_name: str):
        super().__init__(f"postcondition violated calling {function_name!r}")
        self.function_name = function_name


def values_equal(left: object, right: object) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, int) and isinstance(right, int):
        return left == right
    if isinstance(left, Unit) and isinstance(right, Unit):
        return True
    if isinstance(left, ConstructorValue) and isinstance(right, ConstructorValue):
        return (
            left.constructor == right.constructor
            and len(left.fields) == len(right.fields)
            and all(values_equal(a, b) for a, b in zip(left.fields, right.fields))
        )
    return False


def _fields_of(constructor: str, program: syntax.Program) -> tuple[tuple[str, str], ...]:
    """Field declarations for a constructor's owning type: either a record
    type of the same name, or the variant of that name inside some union
    type (a union variant's constructor name is the variant's own name,
    not the union type's name it is keyed under in `program.types`)."""
    type_decl = program.types.get(constructor)
    if isinstance(type_decl, syntax.RecordType):
        return type_decl.fields
    for type_decl in program.types.values():
        if isinstance(type_decl, syntax.UnionType):
            for variant in type_decl.variants:
                if variant.name == constructor:
                    return variant.fields
    raise ValueError(f"no record type or union variant named {constructor!r}")


def call_function(function: syntax.Function, args: tuple[object, ...], program: syntax.Program) -> object:
    env = dict(zip((name for name, _ in function.signature.params), args))

    for requirement in function.requires:
        if eval_expr(requirement, env, program) is not True:
            raise PreconditionViolation(function.name)

    result = eval_expr(function.body, env, program)

    if function.ensures:
        env_with_result = dict(env)
        env_with_result["result"] = result
        for ensurance in function.ensures:
            if eval_expr(ensurance, env_with_result, program) is not True:
                raise PostconditionViolation(function.name)

    return result


def eval_expr(expr: object, env: dict[str, object], program: syntax.Program) -> object:
    if isinstance(expr, syntax.IntLit):
        return expr.value
    if isinstance(expr, syntax.BoolLit):
        return expr.value
    if isinstance(expr, syntax.UnitLit):
        return UNIT
    if isinstance(expr, syntax.NameRef):
        return env[expr.name]

    if isinstance(expr, syntax.Let):
        local_env = dict(env)
        for name, bound_expr in expr.bindings:
            local_env[name] = eval_expr(bound_expr, local_env, program)
        return eval_expr(expr.body, local_env, program)

    if isinstance(expr, syntax.If):
        if eval_expr(expr.condition, env, program):
            return eval_expr(expr.then_branch, env, program)
        return eval_expr(expr.else_branch, env, program)

    if isinstance(expr, syntax.Match):
        scrutinee = eval_expr(expr.scrutinee, env, program)
        for clause in expr.clauses:
            bindings = _match_pattern(clause.pattern, scrutinee)
            if bindings is not None:
                clause_env = dict(env)
                clause_env.update(bindings)
                return eval_expr(clause.body, clause_env, program)
        raise ValueError(f"no match clause covered value {scrutinee!r}")

    if isinstance(expr, syntax.FieldAccess):
        target = eval_expr(expr.target, env, program)
        assert isinstance(target, ConstructorValue)
        field_names = [name for name, _ in _fields_of(target.constructor, program)]
        return target.fields[field_names.index(expr.field_name)]

    if isinstance(expr, syntax.OperatorCall):
        return _eval_operator(expr, env, program)

    if isinstance(expr, syntax.ConstructorCall):
        args = tuple(eval_expr(a, env, program) for a in expr.args)
        return ConstructorValue(expr.name, args)

    if isinstance(expr, syntax.Call):
        function = program.functions[expr.name]
        args = tuple(eval_expr(a, env, program) for a in expr.args)
        return call_function(function, args, program)

    raise TypeError(f"unrecognised expression node: {expr!r}")


def _eval_operator(expr: syntax.OperatorCall, env: dict[str, object], program: syntax.Program) -> object:
    op = expr.operator
    if op == "and":
        left = eval_expr(expr.args[0], env, program)
        return left and eval_expr(expr.args[1], env, program)
    if op == "or":
        left = eval_expr(expr.args[0], env, program)
        return left or eval_expr(expr.args[1], env, program)
    if op == "not":
        return not eval_expr(expr.args[0], env, program)

    left = eval_expr(expr.args[0], env, program)
    right = eval_expr(expr.args[1], env, program)
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "<":
        return left < right
    if op == "<=":
        return left <= right
    if op == ">":
        return left > right
    if op == ">=":
        return left >= right
    if op == "=":
        return values_equal(left, right)
    raise ValueError(f"unknown operator {op!r}")


def _match_pattern(pattern: object, value: object) -> dict[str, object] | None:
    if isinstance(pattern, syntax.PatWildcard):
        return {}
    if isinstance(pattern, syntax.PatVar):
        return {pattern.name: value}
    if isinstance(pattern, syntax.PatInt):
        return {} if isinstance(value, int) and not isinstance(value, bool) and value == pattern.value else None
    if isinstance(pattern, syntax.PatBool):
        return {} if isinstance(value, bool) and value == pattern.value else None
    if isinstance(pattern, syntax.PatUnit):
        return {} if isinstance(value, Unit) else None
    if isinstance(pattern, syntax.PatConstructor):
        if not isinstance(value, ConstructorValue) or value.constructor != pattern.name:
            return None
        if len(pattern.subpatterns) != len(value.fields):
            return None
        bindings: dict[str, object] = {}
        for subpattern, field_value in zip(pattern.subpatterns, value.fields):
            sub_bindings = _match_pattern(subpattern, field_value)
            if sub_bindings is None:
                return None
            bindings.update(sub_bindings)
        return bindings
    raise TypeError(f"unrecognised pattern node: {pattern!r}")
