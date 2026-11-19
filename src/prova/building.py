"""One artefact of a program that was shown whole: the text of a Python
module that computes what the program computes, and where it may be
written.

SPEC.md lines 484-496 ask for a build that runs fresh inputs, invokes the
entry function its metadata names, and refuses to publish anything while
verification is incomplete. docs/ROADMAP.md D2 fixes the target as
generated Python and D3 fixes the values at its boundary as the
s-expression text a program is written with.

Three things live here and nowhere else:

* `Certified`, which cannot be built for a program whose aggregate does
  not say verified, so no caller can reach an artefact without the
  evidence behind it;
* `Destination`, the one thing in this tool that opens a file for
  writing, and only where nothing stands yet;
* `Translation`, which turns a checked core-0 program into the text of a
  module. It reads the same tree the evaluator runs and writes the same
  decisions: an artefact that answered differently would be a second
  meaning of the language.

The artefact carries a small reader and writer of values of its own.
That is deliberate: it must answer on a machine where neither this
compiler nor the solver is installed, so it can import nothing of this
package. The one differential property test holds the two to the same
answers over the inputs it reads.
"""

from __future__ import annotations

import json
import os
import pathlib
import pprint
import tempfile
from dataclasses import dataclass

from prova import formatter, provenance, syntax, verdict

# The categories a build refuses the destination with. Each is declared
# in checker.DIAGNOSTIC_KINDS, where a client reads what it carries.
OUTPUT_DIRECTORY_ABSENT = "output_directory_absent"
OUTPUT_FILE_EXISTS = "output_file_exists"
NOT_SHOWN_WHOLE = "not_shown_whole"

# The line between what this build recorded about one source and the
# program it translated. Everything after it is the same text for two
# sources that differ only in what their examples claim, which is how a
# reader sees that no example answer reached the computation.
THE_PROGRAM_BEGINS = "# --- the program, translated ---"

# The format of the artefact, written into it so a reader of an older
# file knows which shape they hold.
ARTEFACT_FORMAT = "prova-core-0-python-1"


@dataclass(frozen=True)
class Unwritable:
    """Why a build may not write where it was asked to.

    Carried rather than raised: the destination is read beside the
    evidence, so a request that is wrong in both ways is told about both
    at once.
    """

    category: str
    reason: str


@dataclass(frozen=True)
class NotShownWhole:
    """Why no artefact may be published for a program: the aggregate
    over it does not say verified, and this is what it named."""

    reason: str

    def refusal(self) -> Unwritable:
        return Unwritable(NOT_SHOWN_WHOLE, self.reason)


@dataclass(frozen=True)
class Destination:
    """The one file a build may write, known to stand in a directory
    that exists and to hold nothing yet.

    Built only by `at`, which refuses the two cases this slice does not
    write in and names the path in its refusal. Nothing else in this
    tool opens a file for writing, so a refusal decided before one of
    these is built is a refusal that wrote nothing.
    """

    path: pathlib.Path

    @classmethod
    def at(cls, written: str) -> "Destination | Unwritable":
        path = pathlib.Path(written)
        directory = path.parent
        if not directory.is_dir():
            return Unwritable(
                OUTPUT_DIRECTORY_ABSENT,
                f"this tool writes an artefact into a directory that already "
                f"exists and the directory {str(directory)!r} of the "
                f"'output_file' field is not one: {_what_is_there(directory)}. "
                "The artefact is written as a temporary file inside that "
                "directory and then given its name, so there is nowhere to "
                "write it. Nothing was written. Create that directory, or "
                "send an 'output_file' inside one that exists, and ask for "
                "the build again",
            )
        if path.exists():
            return Unwritable(
                OUTPUT_FILE_EXISTS,
                f"this tool never writes over a file that is already there "
                f"and {str(path)!r}, the 'output_file' field of the request, "
                "is already there. An artefact the Owner holds is the one "
                "thing a build must not replace without being asked. Nothing "
                "was written. Send an 'output_file' naming a path that holds "
                "nothing, or move that file aside first, and ask for the "
                "build again",
            )
        return cls(path)

    def publish(self, text: str) -> "Unwritable | None":
        """Put `text` at this destination, or say why it could not be.

        The text is written into a temporary file in the same directory
        and the destination is then made a name for it, which is the one
        step that either happens or does not: a reader of the directory
        sees no half-written artefact, and a file that appeared at the
        path while this build ran is not replaced. The temporary file is
        removed whatever happens, so a destination that holds nothing
        after a refusal holds nothing at all.
        """
        handle, temporary = tempfile.mkstemp(
            dir=str(self.path.parent), prefix=".prova-build-", suffix=".py"
        )
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as writing:
                writing.write(text)
            try:
                os.link(temporary, str(self.path))
            except FileExistsError:
                return Unwritable(
                    OUTPUT_FILE_EXISTS,
                    f"a file appeared at {str(self.path)!r} while this build "
                    "was running, and this tool never writes over one. The "
                    "artefact was not published and nothing at that path was "
                    "changed. Send an 'output_file' naming a path that holds "
                    "nothing and ask for the build again",
                )
        finally:
            os.unlink(temporary)
        return None


def _what_is_there(directory: pathlib.Path) -> str:
    """What a reader will find where a directory was expected, so the
    refusal tells them which of the two things to repair: a path with
    nothing at it, or a path with a file at it."""
    if not directory.exists():
        return "nothing stands at that path"
    return "what stands there is not a directory"


@dataclass(frozen=True)
class Evidence:
    """What certified one program: the word over the whole of it and the
    inventory that word rests on, with the digest a reader recomputes
    over exactly those characters.
    """

    recorded: dict

    @classmethod
    def of(cls, aggregate: dict, inventory: dict) -> "Evidence":
        return cls({"aggregate": aggregate, "inventory": inventory})

    def canonical_text(self) -> str:
        return json.dumps(self.recorded, sort_keys=True, separators=(",", ":"))

    def digest(self) -> str:
        return provenance.Digest.of(self.canonical_text()).rendered()


@dataclass(frozen=True)
class Certified:
    """A program that was shown whole, beside the characters that were
    shown, their revision and the evidence that certified them.

    Built only by `shown`, and only from a verdict whose word is
    verified. There is no constructor that takes the word, so no caller
    anywhere can reach an artefact of a program this tool was not shown.
    """

    program: syntax.Program
    source: str
    revision: str
    evidence: Evidence

    @classmethod
    def shown(
        cls,
        over: verdict.Verdict,
        program: syntax.Program,
        source: str,
        revision: str,
        inventory: dict,
    ) -> "Certified | NotShownWhole":
        published = over.published()
        if over.result != verdict.VERIFIED:
            return NotShownWhole(
                f"no artefact was published, because the program this request "
                f"carries was not shown whole: {over.reason}. The word over "
                "the whole of a program rests on every obligation of its "
                "inventory being discharged, on every example it declares "
                "having been run and passed, and on the static checks "
                "passing; a build publishes nothing while any of the three is "
                "missing (SPEC.md line 290). Nothing was written. Ask the "
                "'verify' operation about the same source to read the whole "
                "inventory, repair what is named here, and ask for the build "
                "again"
            )
        return cls(program, source, revision, Evidence.of(published, inventory))


@dataclass(frozen=True)
class Entry:
    """The function a build invokes, known to be declared by the program
    it was certified with."""

    function: syntax.Function

    @classmethod
    def of(cls, named: str, program: syntax.Program) -> "Entry | None":
        function = program.functions.get(named)
        return None if function is None else cls(function)

    @property
    def name(self) -> str:
        return self.function.name


@dataclass(frozen=True)
class PythonNames:
    """The one map from the names a core-0 program declares to the
    identifiers the generated module uses.

    An identifier carries the place of its declaration, so two names of
    one program can never become one identifier whatever they are
    spelled with, and no name of a program can collide with a keyword of
    Python or with a name the artefact uses for itself: every generated
    identifier of a declaration begins `_fn`, and every generated
    identifier of a binding begins `v`.
    """

    functions: dict

    @classmethod
    def of(cls, program: syntax.Program) -> "PythonNames":
        named = {}
        for place, function in enumerate(
            declared
            for declared in program.in_source_order()
            if isinstance(declared, syntax.Function)
        ):
            named[function.name] = f"_fn{place}_{_spelled(function.name)}"
        return cls(named)

    def function(self, name: str) -> str:
        return self.functions[name]


def _spelled(name: str) -> str:
    """`name` written with the characters a Python identifier takes.

    Readability only: what keeps two identifiers apart is the number
    before this part, so a spelling that happens to collide with another
    cannot make one identifier out of two names.
    """
    written = "".join(
        character if character.isalnum() else "_" for character in name
    )
    return written or "it"


class Scope:
    """The identifiers the bindings standing around one expression are
    reached by.

    A binding of an inner expression is added to a copy, because one
    spelling may be bound again in another clause of the same function
    (core-0 refuses only a binding that hides another one standing
    around it).
    """

    def __init__(self, bound: dict | None = None, counted: list | None = None):
        self._bound = dict(bound or {})
        self._counted = counted if counted is not None else [0]

    def of(self, name: str) -> str:
        return self._bound[name]

    def binding(self, name: str) -> "tuple[Scope, str]":
        self._counted[0] += 1
        identifier = f"v{self._counted[0]}_{_spelled(name)}"
        inner = Scope(self._bound, self._counted)
        inner._bound[name] = identifier
        return inner, identifier


class Lines:
    """The lines of the module being written, each at its indentation."""

    def __init__(self) -> None:
        self._written: list[str] = []
        self._temporaries = 0

    def write(self, depth: int, text: str) -> None:
        self._written.append(("    " * depth) + text)

    def blank(self) -> None:
        self._written.append("")

    def temporary(self) -> str:
        self._temporaries += 1
        return f"_t{self._temporaries}"

    def text(self) -> str:
        return "\n".join(self._written) + "\n"


@dataclass(frozen=True)
class Translation:
    """The text of the program, translated: one Python function per
    function the program declares, with its contracts as checks of the
    run and its body as the computation.

    Nothing of the examples a program declares is read here. What an
    example claims is evidence about the program and never part of it,
    so two programs that differ only in an example translate to the same
    characters (SPEC.md line 491).
    """

    program: syntax.Program
    names: PythonNames

    @classmethod
    def of(cls, program: syntax.Program) -> "Translation":
        return cls(program, PythonNames.of(program))

    def text(self) -> str:
        lines = Lines()
        lines.write(0, f"_FIELDS = {_fields_of(self.program)!r}")
        lines.blank()
        for declared in self.program.in_source_order():
            if isinstance(declared, syntax.Function):
                self._function(declared, lines)
        lines.write(0, "_FUNCTIONS = {")
        for name in self.names.functions:
            lines.write(1, f"{name!r}: {self.names.function(name)},")
        lines.write(0, "}")
        return lines.text()

    def _function(self, function: syntax.Function, lines: Lines) -> None:
        scope = Scope()
        parameters = []
        for parameter in function.signature.params:
            scope, identifier = scope.binding(parameter.name)
            parameters.append(identifier)
        lines.write(
            0,
            f"def {self.names.function(function.name)}"
            f"({', '.join(parameters)}):",
        )
        lines.write(
            1,
            f'"""{function.name}: '
            f'({", ".join(p.type_name for p in function.signature.params)}) '
            f'-> {function.signature.return_type}."""',
        )
        for requirement in function.requires:
            self._contract(function, "precondition", requirement, scope, lines)
        answered = self._expression(function.body, scope, lines, 1)
        lines.write(1, f"_result = {answered}")
        if function.ensures:
            after, identifier = scope.binding("result")
            lines.write(1, f"{identifier} = _result")
            for ensurance in function.ensures:
                self._contract(function, "postcondition", ensurance, after, lines)
        lines.write(1, "return _result")
        lines.blank()

    def _contract(
        self,
        function: syntax.Function,
        kind: str,
        condition: object,
        scope: Scope,
        lines: Lines,
    ) -> None:
        held = self._expression(condition, scope, lines, 1)
        written = formatter.expression_text(condition)
        lines.write(1, f"if not _truth({held}):")
        lines.write(
            2,
            f"raise _ContractFailed({function.name!r}, {kind!r}, "
            f"{written!r})",
        )

    def _expression(
        self, expr: object, scope: Scope, lines: Lines, depth: int
    ) -> str:
        """The text of one Python expression answering what `expr`
        answers, with whatever statements it needs written first.

        Every node is written the way the evaluator runs it: the branch
        not taken is not computed, a conjunction stops at a false left
        operand, and a match tries its clauses in the order the source
        writes them.
        """
        if isinstance(expr, syntax.IntLit):
            return repr(expr.value)
        if isinstance(expr, syntax.BoolLit):
            return "True" if expr.value else "False"
        if isinstance(expr, syntax.UnitLit):
            return "_UNIT"
        if isinstance(expr, syntax.NameRef):
            return scope.of(expr.name)
        if isinstance(expr, syntax.Let):
            inner = scope
            for binding in expr.bindings:
                value = self._expression(binding.value, inner, lines, depth)
                inner, identifier = inner.binding(binding.name)
                lines.write(depth, f"{identifier} = {value}")
            return self._expression(expr.body, inner, lines, depth)
        if isinstance(expr, syntax.If):
            answer = lines.temporary()
            condition = self._expression(expr.condition, scope, lines, depth)
            lines.write(depth, f"if {condition}:")
            taken = self._expression(expr.then_branch, scope, lines, depth + 1)
            lines.write(depth + 1, f"{answer} = {taken}")
            lines.write(depth, "else:")
            otherwise = self._expression(expr.else_branch, scope, lines, depth + 1)
            lines.write(depth + 1, f"{answer} = {otherwise}")
            return answer
        if isinstance(expr, syntax.Match):
            return self._match(expr, scope, lines, depth)
        if isinstance(expr, syntax.FieldAccess):
            target = self._expression(expr.target, scope, lines, depth)
            return f"_field({target}, {expr.field_name!r})"
        if isinstance(expr, syntax.OperatorCall):
            return self._operator(expr, scope, lines, depth)
        if isinstance(expr, syntax.ConstructorCall):
            written = [
                self._expression(argument, scope, lines, depth)
                for argument in expr.args
            ]
            return f"_make({expr.name!r}, {', '.join(written)})"
        if isinstance(expr, syntax.Call):
            written = [
                self._expression(argument, scope, lines, depth)
                for argument in expr.args
            ]
            return f"{self.names.function(expr.name)}({', '.join(written)})"
        raise TypeError(
            f"WHAT: the expression {expr!r} is of a kind this translation does "
            "not write. "
            "WHY: every node the checker accepts must reach the artefact, or "
            "a program this tool accepted could not be built. "
            "HOW: write that node in prova.building.Translation._expression."
        )

    def _operator(
        self, expr: syntax.OperatorCall, scope: Scope, lines: Lines, depth: int
    ) -> str:
        operator = expr.operator
        if operator in ("and", "or"):
            left = self._expression(expr.args[0], scope, lines, depth)
            answer = lines.temporary()
            # The right operand is computed only when the left one does
            # not already settle the answer, as the evaluator does: its
            # statements stand inside the branch that needs them.
            lines.write(depth, f"{answer} = {left}")
            lines.write(
                depth, f"if {'' if operator == 'and' else 'not '}{answer}:"
            )
            right = self._expression(expr.args[1], scope, lines, depth + 1)
            lines.write(depth + 1, f"{answer} = {right}")
            return answer
        written = [
            self._expression(argument, scope, lines, depth)
            for argument in expr.args
        ]
        if operator == "not":
            return f"(not {written[0]})"
        if operator == "=":
            return f"_equal({written[0]}, {written[1]})"
        return f"({written[0]} {operator} {written[1]})"

    def _match(
        self, expr: syntax.Match, scope: Scope, lines: Lines, depth: int
    ) -> str:
        subject = lines.temporary()
        answer = lines.temporary()
        lines.write(
            depth,
            f"{subject} = {self._expression(expr.scrutinee, scope, lines, depth)}",
        )
        opening = "if"
        for clause in expr.clauses:
            tests: list[str] = []
            bound: list[tuple[str, str]] = []
            inner = _pattern(clause.pattern, subject, scope, tests, bound)
            lines.write(
                depth, f"{opening} {' and '.join(tests) if tests else 'True'}:"
            )
            for identifier, reached in bound:
                lines.write(depth + 1, f"{identifier} = {reached}")
            taken = self._expression(clause.body, inner, lines, depth + 1)
            lines.write(depth + 1, f"{answer} = {taken}")
            opening = "elif"
        lines.write(depth, "else:")
        lines.write(depth + 1, f"raise _NoClauseCovered({subject})")
        return answer


def _pattern(
    pattern: object,
    reached: str,
    scope: Scope,
    tests: list,
    bound: list,
) -> Scope:
    """What must hold for `pattern` to cover the value at `reached`, and
    the bindings it makes, read in the order the evaluator reads them:
    the test of a part stands after the test of the whole it is part of,
    so a part is never looked at before its constructor is known.
    """
    if isinstance(pattern, syntax.PatWildcard):
        return scope
    if isinstance(pattern, syntax.PatVar):
        inner, identifier = scope.binding(pattern.name)
        bound.append((identifier, reached))
        return inner
    if isinstance(pattern, syntax.PatInt):
        tests.append(f"_is_int({reached}, {pattern.value!r})")
        return scope
    if isinstance(pattern, syntax.PatBool):
        tests.append(f"_is_bool({reached}, {pattern.value!r})")
        return scope
    if isinstance(pattern, syntax.PatUnit):
        tests.append(f"_is_unit({reached})")
        return scope
    if isinstance(pattern, syntax.PatConstructor):
        tests.append(
            f"_is({reached}, {pattern.name!r}, {len(pattern.subpatterns)})"
        )
        inner = scope
        for place, subpattern in enumerate(pattern.subpatterns):
            inner = _pattern(
                subpattern, f"{reached}.fields[{place}]", inner, tests, bound
            )
        return inner
    raise TypeError(
        f"WHAT: the pattern {pattern!r} is of a kind this translation does not "
        "write. "
        "WHY: every pattern the checker accepts must reach the artefact. "
        "HOW: write that pattern in prova.building._pattern."
    )


def _fields_of(program: syntax.Program) -> dict:
    """The field names of every constructor the program declares, read
    the way the evaluator reads them: by the name of the constructor a
    value carries."""
    named: dict = {}
    for declared in program.types.values():
        if isinstance(declared, syntax.RecordType):
            named[declared.name] = tuple(name for name, _ in declared.fields)
        elif isinstance(declared, syntax.UnionType):
            for variant in declared.variants:
                named[variant.name] = tuple(name for name, _ in variant.fields)
    return named


# The part of every artefact that is the same in all of them: the values
# of core-0, their reader and their writer, and the refusals. Written as
# one text because it is one thing -- what the artefact is made of --
# and because a reader of a generated file must be able to read it.
THE_RUNTIME = '''
class _Unit:
    """The sole value of type Unit, written ()."""

    __slots__ = ()

    def __eq__(self, other):
        return isinstance(other, _Unit)

    def __hash__(self):
        return hash(_Unit)


_UNIT = _Unit()


class _Constructed:
    """A record or union-variant value: the name of its constructor and
    its field values, in the order the program declares them."""

    __slots__ = ("constructor", "fields")

    def __init__(self, constructor, fields):
        self.constructor = constructor
        self.fields = fields


class _Refused(Exception):
    """The input this artefact was run over is not input it can answer."""


class _ContractFailed(Exception):
    """A contract of the program did not hold for this run."""

    def __init__(self, function, kind, condition):
        super().__init__(
            "WHAT: the " + kind + " of " + repr(function) + " did not hold "
            "for this input: " + condition + ". "
            "WHY: the program promises nothing where its " + kind + " does "
            "not hold, so this artefact answers nothing there either; a "
            "postcondition that does not hold is an assurance failure of a "
            "program that was verified and never an answer. "
            "HOW: run the entry over input the program accepts, or ask the "
            "compiler about the same source with the 'evaluate' operation to "
            "see the same refusal."
        )


class _NoClauseCovered(Exception):
    """No clause of a match covered the value: the checker refuses a
    match that leaves a case out, so this says the artefact was handed a
    value of a shape the program cannot have."""

    def __init__(self, value):
        super().__init__(
            "WHAT: no clause of a match in this program covered the value "
            + _write_value(value) + ". "
            "WHY: the compiler refuses a match that leaves a case out, so "
            "this value is not one the declared types hold. "
            "HOW: run the entry over values of the declared types."
        )


def _make(name, *fields):
    return _Constructed(name, tuple(fields))


def _truth(value):
    """Whether a condition held, read as the evaluator reads it: only the
    value true is true, and nothing else counts as it."""
    return value is True


def _equal(left, right):
    """Whether two values of core-0 are the same value, as the evaluator
    decides it: a flag is never a number, and two constructed values
    agree only on the same constructor and the same fields."""
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, int) and isinstance(right, int):
        return left == right
    if isinstance(left, _Unit) and isinstance(right, _Unit):
        return True
    if isinstance(left, _Constructed) and isinstance(right, _Constructed):
        return (
            left.constructor == right.constructor
            and len(left.fields) == len(right.fields)
            and all(_equal(a, b) for a, b in zip(left.fields, right.fields))
        )
    return False


def _field(value, name):
    if not isinstance(value, _Constructed) or value.constructor not in _FIELDS:
        raise _Refused(
            "WHAT: the field " + repr(name) + " was read from "
            + _write_value(value) + ", which is not a value of a type this "
            "program declares. "
            "WHY: only a record or a union variant has fields to read. "
            "HOW: run the entry over values of the types its signature "
            "declares."
        )
    declared = _FIELDS[value.constructor]
    if name not in declared:
        raise _Refused(
            "WHAT: the constructor " + repr(value.constructor) + " has no "
            "field " + repr(name) + "; it has " + repr(declared) + ". "
            "WHY: a field is read by the name its declaration gives it. "
            "HOW: run the entry over values of the declared types."
        )
    return value.fields[declared.index(name)]


def _is(value, name, count):
    return (
        isinstance(value, _Constructed)
        and value.constructor == name
        and len(value.fields) == count
    )


def _is_int(value, number):
    return isinstance(value, int) and not isinstance(value, bool) and value == number


def _is_bool(value, flag):
    return isinstance(value, bool) and value == flag


def _is_unit(value):
    return isinstance(value, _Unit)


def _write_value(value):
    """One value as the text a program writes it with, which is the text
    the compiler writes it with too."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, _Unit):
        return "()"
    if isinstance(value, _Constructed):
        if not value.fields:
            return "(" + value.constructor + ")"
        return (
            "("
            + value.constructor
            + " "
            + " ".join(_write_value(field) for field in value.fields)
            + ")"
        )
    return repr(value)


def _read_value(text, about):
    """The one value `text` writes, or the refusal to read one.

    The same small syntax the compiler reads a value in: a whole number,
    true or false, () for unit, and a constructor with its fields inside
    brackets.
    """
    forms, rest = _read_form(text, 0, about)
    if _skipped(rest, text) != len(text):
        raise _Refused(
            "WHAT: " + about + " carries more than one value: " + repr(text)
            + ". "
            "WHY: one argument of the entry is one value. "
            "HOW: send one value per argument, as \\"(Clock 12)\\" or \\"7\\"."
        )
    return forms


def _skipped(at, text):
    while at < len(text) and text[at].isspace():
        at += 1
    return at


def _read_form(text, at, about):
    at = _skipped(at, text)
    if at >= len(text):
        raise _Refused(
            "WHAT: " + about + " carries no value at all: " + repr(text) + ". "
            "WHY: the entry of this program takes one value per argument. "
            "HOW: send the value the way a program writes it, as "
            "\\"(Clock 12)\\" or \\"7\\"."
        )
    if text[at] == "(":
        at = _skipped(at + 1, text)
        if at < len(text) and text[at] == ")":
            return _UNIT, at + 1
        name, at = _read_word(text, at, about)
        fields = []
        while True:
            at = _skipped(at, text)
            if at < len(text) and text[at] == ")":
                at += 1
                break
            if at >= len(text):
                raise _Refused(
                    "WHAT: " + about + " stops before the value is closed: "
                    + repr(text) + ". "
                    "WHY: a constructed value is written inside one pair of "
                    "brackets. "
                    "HOW: close the value, as \\"(Clock 12)\\"."
                )
            field, at = _read_form(text, at, about)
            fields.append(field)
        if name not in _FIELDS:
            raise _Refused(
                "WHAT: " + about + " names the constructor " + repr(name)
                + ", which this program does not declare; it declares "
                + repr(tuple(sorted(_FIELDS))) + ". "
                "WHY: a value of this program is built by one of its own "
                "constructors. "
                "HOW: send a value of a type the entry declares."
            )
        if len(fields) != len(_FIELDS[name]):
            raise _Refused(
                "WHAT: " + about + " gives the constructor " + repr(name) + " "
                + str(len(fields)) + " field(s) and it takes "
                + str(len(_FIELDS[name])) + " "
                + repr(_FIELDS[name]) + ". "
                "WHY: a value carries every field its declaration names. "
                "HOW: write one value per field, in the declared order."
            )
        return _Constructed(name, tuple(fields)), at
    word, at = _read_word(text, at, about)
    if word == "true":
        return True, at
    if word == "false":
        return False, at
    try:
        return int(word), at
    except ValueError:
        raise _Refused(
            "WHAT: " + about + " writes " + repr(word) + ", which is not a "
            "value of core-0. "
            "WHY: a value is a whole number, true, false, () or a "
            "constructor of this program with its fields. "
            "HOW: send one of those."
        ) from None


def _read_word(text, at, about):
    start = at
    while at < len(text) and not text[at].isspace() and text[at] not in "()":
        at += 1
    if at == start:
        raise _Refused(
            "WHAT: " + about + " carries nothing where a name or a number "
            "was expected: " + repr(text) + ". "
            "WHY: a constructed value opens with the name of its "
            "constructor. "
            "HOW: write the value as \\"(Clock 12)\\"."
        )
    return text[start:at], at


def certifies(source_text):
    """Whether the evidence this artefact carries is about `source_text`.

    The one question a reader holding two versions of a file has to ask.
    It is answered by the revision this artefact records and by nothing
    else, so an artefact never says it stands for a source it was not
    built from.
    """
    return (
        hashlib.sha256(source_text.encode("utf-8")).hexdigest()
        == ARTEFACT["source_revision"]
    )


def _refuse_a_header_that_is_not_about_this_program():
    """The artefact refuses to answer at all when the source it carries
    is not the source its revision names: the header and the program in
    this file stand for one thing or the file is not usable."""
    if certifies(SOURCE):
        return
    sys.stderr.write(
        "WHAT: this artefact records the source revision "
        + repr(ARTEFACT["source_revision"])
        + " and the source written in it has the revision "
        + repr(hashlib.sha256(SOURCE.encode("utf-8")).hexdigest())
        + ". "
        "WHY: the evidence recorded here certifies one text; a file whose "
        "header and whose program are not that one text claims evidence it "
        "does not have. "
        "HOW: build the artefact again from the source you hold; do not "
        "edit a generated artefact by hand.\\n"
    )
    raise SystemExit(4)


def main(argv):
    """One run of this artefact: each argument is the text of a value,
    the answer is the text of one value on standard output, and a
    refusal is words on the error channel with a status of its own."""
    _refuse_a_header_that_is_not_about_this_program()
    try:
        if len(argv) != len(PARAMETERS):
            raise _Refused(
                "WHAT: this artefact was run over " + str(len(argv))
                + " argument(s) and its entry " + repr(ARTEFACT["entry"])
                + " takes " + str(len(PARAMETERS)) + ": "
                + repr(PARAMETERS) + ". "
                "WHY: every parameter of the entry is given one value. "
                "HOW: run it again with one argument per parameter, each the "
                "text of a value."
            )
        values = []
        for place, written in enumerate(argv):
            values.append(
                _read_value(
                    written,
                    "argument " + str(place + 1) + " ("
                    + PARAMETERS[place][0] + " " + PARAMETERS[place][1] + ")",
                )
            )
        answered = _ENTRY(*values)
    except _Refused as refusal:
        sys.stderr.write(str(refusal) + "\\n")
        return 2
    except _ContractFailed as failure:
        sys.stderr.write(str(failure) + "\\n")
        return 3
    except _NoClauseCovered as failure:
        sys.stderr.write(str(failure) + "\\n")
        return 3
    except RecursionError:
        sys.stderr.write(
            "WHAT: this artefact ran out of stack answering that input. "
            "WHY: a chain of calls deeper than the interpreter takes cannot "
            "be answered, and an artefact never ends in a traceback. "
            "HOW: run it over a smaller input.\\n"
        )
        return 4
    except Exception as failure:  # the artefact, not the input
        sys.stderr.write(
            "WHAT: this artefact failed inside itself: "
            + type(failure).__name__ + ": " + str(failure) + ". "
            "WHY: this is a failure of the generated program, not a "
            "statement about any input; an artefact never ends in a "
            "traceback. "
            "HOW: report it with the source revision this artefact records.\\n"
        )
        return 4
    sys.stdout.write(_write_value(answered) + "\\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''


@dataclass(frozen=True)
class Artefact:
    """One artefact: the text of a module that computes what one
    certified program computes, with what certified it recorded in it as
    data.

    Built only from a `Certified` and an `Entry` of that same program,
    so the header and the program in it are always about one source.
    """

    text: str
    recorded: dict

    @classmethod
    def of(
        cls, certified: Certified, entry: Entry, configuration: dict
    ) -> "Artefact":
        recorded = {
            "artefact_format": ARTEFACT_FORMAT,
            "source_revision": certified.revision,
            "entry": entry.name,
            "configuration": configuration,
            "evidence_digest": certified.evidence.digest(),
        }
        translation = Translation.of(certified.program)
        parameters = tuple(
            (parameter.name, parameter.type_name)
            for parameter in entry.function.signature.params
        )
        written = [
            '"""One program of core-0, built by the Prova compiler.',
            "",
            "What certified this program stands in ARTEFACT below, as data: "
            "the revision",
            "of the source it was built from, the entry it invokes, the "
            "configuration it",
            "was verified under and the digest of that evidence. The source "
            "itself is in",
            "SOURCE, and `certifies(text)` answers whether this evidence is "
            "about a text",
            "a reader holds.",
            "",
            "Run it with one argument per parameter of the entry, each the "
            "text of a value",
            "the way a program writes it. It answers the text of one value, "
            "or refuses in",
            "words: 2 for input it cannot answer, 3 for a contract of the "
            "program that did",
            "not hold, 4 for a failure of this file itself. It imports "
            "nothing but the",
            "standard library, so it answers where neither the compiler nor "
            "the solver is",
            'installed.',
            '"""',
            "",
            "import hashlib",
            "import sys",
            "",
            "ARTEFACT = "
            + pprint.pformat(recorded, indent=1, width=74, sort_dicts=True),
            "",
            f"SOURCE = {certified.source!r}",
            "",
            f"PARAMETERS = {parameters!r}",
            "",
            THE_PROGRAM_BEGINS,
            "",
            translation.text(),
            f"_ENTRY = _FUNCTIONS[{entry.name!r}]",
            THE_RUNTIME.strip("\n"),
            "",
        ]
        return cls("\n".join(written), recorded)

    def published(self, destination: Destination) -> dict:
        """What the answer records about the artefact that was written:
        the same record the artefact carries, beside the path it is at.
        One place writes both, so the two cannot disagree."""
        return {"path": str(destination.path), **self.recorded}
