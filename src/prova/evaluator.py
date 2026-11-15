"""Call-by-value evaluator for core-0, with contract checking on every
user call, entry and nested, including calls inside contracts."""

from __future__ import annotations

from dataclasses import dataclass

from prova import syntax
from prova.values import UNIT, ConstructorValue, Unit


class EvaluationTooDeep(Exception):
    """Running the program needed more evaluation steps standing inside
    one another than this tool takes.

    The program breaks no rule of core-0: a chain of functions that each
    call the next is perfectly well formed, and the checker already
    refuses the one thing that would make it endless, a cycle. This says
    only how far this tool follows such a chain.
    """

    def __init__(self, message: str, line: int, column: int, limit: int, reached: int):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.limit = limit
        self.reached = reached


@dataclass(frozen=True)
class EvaluationDepthLimit:
    """How many evaluation steps this tool lets stand inside one
    another, and the name a caller reads that number under.

    One number covers every way the evaluator stands inside itself: a
    call to a function whose body calls the next, an expression written
    inside an expression, and any mixture of the two. Counting calls
    alone would leave the mixture unbounded, because the expression
    written inside each call is still standing on the same stack when
    the next call is made.
    """

    maximum: int
    name: str = "evaluation_depth"

    def passed_by(self, depth: int) -> bool:
        return depth > self.maximum

    def reason(self) -> str:
        return (
            f"each evaluation step standing inside another costs 2 interpreter "
            f"frames, so {self.maximum} steps cost about "
            f"{2 * self.maximum + 20} of the 1000 frames Python allows by "
            "default, and the refusal is reached with room to spare however "
            "deep the caller's own stack already is. One number covers calls "
            "and nested expressions together, because a program mixing them "
            "stands on one stack: a chain of calls each holding a deeply "
            "written expression costs the sum of the two, not the larger. "
            "The cost is that a chain of more than "
            f"{self.maximum} calls is refused, far more than a person writes "
            "and far fewer than a generator can emit."
        )

    def refusal_at(self, depth: int, line: int, column: int) -> EvaluationTooDeep:
        return EvaluationTooDeep(
            f"running this program reached {depth} evaluation steps standing "
            f"inside one another and this tool takes {self.maximum}: it runs a "
            "step inside another by calling itself, and declares a maximum so "
            "that it refuses here instead of exhausting the interpreter stack "
            "and answering nothing at all; shorten the chain of calls, or "
            "write the inner expressions as separate 'let' bindings, so that "
            f"no more than {self.maximum} steps stand inside one another, and "
            f"read {self.maximum} from the {self.name!r} entry of the resource "
            "limits the 'discover' operation publishes",
            line,
            column,
            self.maximum,
            depth,
        )


# How far this tool follows one evaluation step standing inside another.
EVALUATION_LIMIT = EvaluationDepthLimit(160)


def _place_of(expr: object) -> tuple[int, int]:
    """Where `expr` stands, counted from 1.

    A node built without a place carries zeros, which is no place in any
    text; a refusal about it stands at the start of the text instead, so
    a reader of it always has a line to open.
    """
    return (max(1, getattr(expr, "line", 0)), max(1, getattr(expr, "column", 0)))


class MalformedValue(Exception):
    """An argument value has no shape any declared type recognizes: an
    unknown constructor, or a known constructor applied to the wrong
    number of fields for its own declaration."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class IllTypedValue(Exception):
    """An argument value is well-formed on its own terms but does not
    match the type declared at this position."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def check_value_type(value: object, type_name: str, program: syntax.Program, where: str) -> None:
    """Raise `MalformedValue` or `IllTypedValue` when `value` does not
    match `type_name`, recursing into constructor fields. Silent when it
    matches."""
    if type_name == "Unit":
        if not isinstance(value, Unit):
            raise IllTypedValue(f"{where} expects Unit, got {value!r}")
        return
    if type_name == "Bool":
        if not isinstance(value, bool):
            raise IllTypedValue(f"{where} expects Bool, got {value!r}")
        return
    if type_name == "Int":
        if isinstance(value, bool) or not isinstance(value, int):
            raise IllTypedValue(f"{where} expects Int, got {value!r}")
        return

    if not isinstance(value, ConstructorValue):
        raise IllTypedValue(f"{where} expects {type_name!r}, got {value!r}")

    declared = syntax.DeclaredConstructor.of(value.constructor, program)
    if declared is None:
        raise MalformedValue(f"{where}: no record type or union variant named {value.constructor!r}")
    if declared.disagrees_with(len(value.fields)):
        raise MalformedValue(
            f"{where}: constructor {value.constructor!r} takes {declared.takes()} field(s), "
            f"got {len(value.fields)}"
        )
    if declared.owner != type_name:
        raise IllTypedValue(
            f"{where} expects {type_name!r}, got {declared.owner!r} value {value.constructor!r}"
        )

    for (field_name, field_type), field_value in zip(declared.fields, value.fields):
        check_value_type(field_value, field_type, program, f"{where} field {field_name!r}")


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
    fields = syntax.resolve_constructor_fields(constructor, program)
    if fields is None:
        raise ValueError(f"no record type or union variant named {constructor!r}")
    return fields


def call_function(
    function: syntax.Function,
    args: tuple[object, ...],
    program: syntax.Program,
    standing: int = 0,
) -> object:
    env = dict(zip((name for name, _ in function.signature.params), args))

    for requirement in function.requires:
        if eval_expr(requirement, env, program, standing) is not True:
            raise PreconditionViolation(function.name)

    result = eval_expr(function.body, env, program, standing)

    if function.ensures:
        env_with_result = dict(env)
        env_with_result["result"] = result
        for ensurance in function.ensures:
            if eval_expr(ensurance, env_with_result, program, standing) is not True:
                raise PostconditionViolation(function.name)

    return result


def eval_expr(
    expr: object,
    env: dict[str, object],
    program: syntax.Program,
    enclosing: int = 0,
) -> object:
    """The value of `expr`, with `enclosing` evaluation steps already
    standing around it.

    The one place the evaluator stands inside itself, so the one place
    the depth is counted. Counting it here rather than at a call alone
    covers a chain of calls, an expression written inside an expression
    and any mixture of them with one number, because all three stand on
    the same stack.
    """
    standing = enclosing + 1
    if EVALUATION_LIMIT.passed_by(standing):
        line, column = _place_of(expr)
        raise EVALUATION_LIMIT.refusal_at(standing, line, column)

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
            local_env[name] = eval_expr(bound_expr, local_env, program, standing)
        return eval_expr(expr.body, local_env, program, standing)

    if isinstance(expr, syntax.If):
        if eval_expr(expr.condition, env, program, standing):
            return eval_expr(expr.then_branch, env, program, standing)
        return eval_expr(expr.else_branch, env, program, standing)

    if isinstance(expr, syntax.Match):
        scrutinee = eval_expr(expr.scrutinee, env, program, standing)
        for clause in expr.clauses:
            bindings = _match_pattern(clause.pattern, scrutinee)
            if bindings is not None:
                clause_env = dict(env)
                clause_env.update(bindings)
                return eval_expr(clause.body, clause_env, program, standing)
        raise ValueError(f"no match clause covered value {scrutinee!r}")

    if isinstance(expr, syntax.FieldAccess):
        target = eval_expr(expr.target, env, program, standing)
        assert isinstance(target, ConstructorValue)
        field_names = [name for name, _ in _fields_of(target.constructor, program)]
        return target.fields[field_names.index(expr.field_name)]

    if isinstance(expr, syntax.OperatorCall):
        return _eval_operator(expr, env, program, standing)

    if isinstance(expr, syntax.ConstructorCall):
        args = tuple(eval_expr(a, env, program, standing) for a in expr.args)
        return ConstructorValue(expr.name, args)

    if isinstance(expr, syntax.Call):
        function = program.functions[expr.name]
        args = tuple(eval_expr(a, env, program, standing) for a in expr.args)
        return call_function(function, args, program, standing)

    raise TypeError(f"unrecognised expression node: {expr!r}")


def _eval_operator(
    expr: syntax.OperatorCall,
    env: dict[str, object],
    program: syntax.Program,
    standing: int = 0,
) -> object:
    op = expr.operator
    if op == "and":
        left = eval_expr(expr.args[0], env, program, standing)
        return left and eval_expr(expr.args[1], env, program, standing)
    if op == "or":
        left = eval_expr(expr.args[0], env, program, standing)
        return left or eval_expr(expr.args[1], env, program, standing)
    if op == "not":
        return not eval_expr(expr.args[0], env, program, standing)

    left = eval_expr(expr.args[0], env, program, standing)
    right = eval_expr(expr.args[1], env, program, standing)
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
