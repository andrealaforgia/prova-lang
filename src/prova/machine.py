"""What a machine descriptor says, and whether the program it is about
says the same.

SPEC.md lines 348-360 describe a machine as eight named parts: the state,
event and outcome types, and the five role functions `init`, `step`,
`state-of`, `admissible` and `invariant`. A descriptor is a separate
versioned JSON document naming those eight parts and the assumptions its
runtime makes; SPEC.md line 350 says `machine-0` adds no syntax, so the
program a descriptor is about is ordinary core-0 and this module reads it
exactly as the checker left it.

This module owns the document and the roles, and nothing else: it reads
no file, no field of a request and no clock, builds no answer and writes
no refusal of its own -- it answers with the refusals of the two
categories checker.py declares for it.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import checker, syntax

# The one version of the descriptor shape this tool reads. The shape of a
# descriptor is fixed per version, so a document written in another
# version is refused rather than read by guesswork.
SCHEMA_VERSION = "machine-descriptor/1"

# The four fields of the document, named once: the reader looks each one
# up under these names, the refusals name them, and the manifest
# publishes them, so what an agent reads is what the reader reads.
SCHEMA = "schema"
TYPES = "types"
ROLES = "roles"
ASSUMPTIONS = "assumptions"

# The name a refusal about a field of the descriptor carries, so an Owner
# is sent to the place in the document to repair rather than to the
# request that carried it.
FIELD = "descriptor"

# The two categories a refusal about a role carries, read from the table
# that declares what each of them carries: this module builds refusals of
# those categories and declares none of its own.
UNRESOLVED_ROLE = checker.UNRESOLVED_ROLE
ROLE_PRECONDITION_RESTRICTED = checker.ROLE_PRECONDITION_RESTRICTED

# The type core-0 gives a predicate's result. Written as the one name
# core-0 spells it with, because a role whose result is a truth value
# reads it from core-0 and not from the descriptor.
BOOL = "Bool"


@dataclass(frozen=True)
class DocumentField:
    """One field of the descriptor document: its name, the kind of value
    it carries and what it is for.

    Every field of a descriptor must be sent: the document names a whole
    machine, and a part of it left out is a part nothing could be said
    about.
    """

    name: str
    kind: str
    what: str

    def published(self) -> dict:
        return {"kind": self.kind, "presence": "required", "what": self.what}


THE_DOCUMENT = (
    DocumentField(
        SCHEMA,
        "text",
        f"the version of the descriptor shape this document is written "
        f"in, which this tool reads as {SCHEMA_VERSION!r} and in no other "
        f"version",
    ),
    DocumentField(
        TYPES,
        "object",
        "the three types of the machine, each under the role it fills: "
        "'state', 'event' and 'outcome', and each naming a type the "
        "submitted program declares",
    ),
    DocumentField(
        ROLES,
        "object",
        "the five role functions of the machine, each under the role it "
        "fills: 'init', 'step', 'state-of', 'admissible' and 'invariant', "
        "and each naming a function the submitted program declares with "
        "the shape its role needs",
    ),
    DocumentField(
        ASSUMPTIONS,
        "list of texts",
        "the assumptions the machine's runtime makes, as sentences, at "
        "least one. They are carried into the answer as stated: this tool "
        "reads them and checks none of them",
    ),
)
THE_DOCUMENT_FIELDS = tuple(field.name for field in THE_DOCUMENT)


@dataclass(frozen=True)
class RoleShape:
    """The parameters and the result a role's function must declare,
    written over the roles of the descriptor's own types.

    A parameter or a result is either one of the type roles -- 'state',
    'event', 'outcome' -- or a type core-0 has, which is written as
    itself. So the shape says what it needs both before a descriptor is
    read, which is what the manifest publishes, and against one
    descriptor, which is what a refusal and an accepted answer say.
    """

    parameters: tuple[str, ...]
    result: str

    def published(self) -> str:
        return self._written(lambda role: f"<{role}>")

    def written_for(self, types: "NamedRoles") -> str:
        return self._written(types.name_of)

    def needs(self, type_role: str) -> bool:
        return type_role in (*self.parameters, self.result)

    def _written(self, name_of) -> str:
        written = ", ".join(self._name(parameter, name_of) for parameter in self.parameters)
        return f"({written}) -> {self._name(self.result, name_of)}"

    @staticmethod
    def _name(part: str, name_of) -> str:
        if part == BOOL:
            return BOOL
        return name_of(part)


@dataclass(frozen=True)
class ResolvedRole:
    """What one role of a descriptor resolved to: the name the descriptor
    gave it and the shape that name turned out to have."""

    role: str
    named: str
    shape: str

    def published(self) -> dict:
        return {"named": self.named, "shape": self.shape}


class TypeRole:
    """One of the three types a descriptor names: it resolves to a type
    the submitted program declares.

    A core type such as Int is not one: the machines SPEC.md describes
    declare their state, event and outcome types, and a core type carries
    no machine of its own. An agent reads that from the published shape.
    """

    def __init__(self, name: str, what_it_is: str) -> None:
        self._name = name
        self._what_it_is = what_it_is

    @property
    def name(self) -> str:
        return self._name

    def stands_in(self) -> str:
        return TYPES

    def published(self) -> dict:
        return {
            "stands_in": TYPES,
            "resolves_to": "type",
            "shape": "a type the submitted program declares, a record or a union",
            "what_it_is": self._what_it_is,
            "precondition": "not applicable: a type declares no contract",
        }

    def resolve(self, named: str, program: syntax.Program, types: "NamedRoles"):
        declared = program.types.get(named)
        if declared is None:
            return checker.Diagnostic(
                UNRESOLVED_ROLE,
                f"WHAT: the {self._name!r} role of the descriptor names the "
                f"type {named!r}, and the submitted program declares no type "
                f"of that name. WHY: {self._what_it_is}, and a machine's "
                "state, event and outcome types are types its program "
                "declares, so a name nothing declares leaves the roles that "
                f"need it -- {checker.listed(_roles_needing(self._name))} -- "
                "unresolved, and they were not read. HOW: declare that type "
                "in the program with deftype, or name a type it declares; "
                "the 'parse' operation lists what a program declares",
                about=checker.AboutARole(self._name, named),
            )
        return ResolvedRole(self._name, named, _written_kind_of(declared))


class FunctionRole:
    """One of the five roles a descriptor names a function for: it
    resolves to a function the program declares with the shape the role
    needs.

    Four of the five must also be valid for every input of their declared
    types (SPEC.md lines 359-360). This tool establishes that for a
    precondition that asks for nothing and for no other, so a function
    whose precondition asks something of its input cannot stand in one of
    those four. The step is not one of them: SPEC.md lines 360-361 let it
    require an invariant state.
    """

    def __init__(self, name: str, shape: RoleShape, valid_for_every_input: bool) -> None:
        self._name = name
        self._shape = shape
        self._valid_for_every_input = valid_for_every_input

    @property
    def name(self) -> str:
        return self._name

    def stands_in(self) -> str:
        return ROLES

    def needs(self, type_role: str) -> bool:
        """Whether this role's shape is written over `type_role`."""
        return self._shape.needs(type_role)

    def published(self) -> dict:
        return {
            "stands_in": ROLES,
            "resolves_to": "function",
            "shape": self._shape.published(),
            "what_it_is": (
                "a function the submitted program declares, with exactly the "
                "parameters and the result written above, where <state>, "
                "<event> and <outcome> are the types this descriptor names"
            ),
            "precondition": self._published_precondition(),
        }

    def resolve(self, named: str, program: syntax.Program, types: "NamedRoles"):
        declared = program.functions.get(named)
        if declared is None:
            return self._absent(named)
        written = _shape_of(declared)
        wanted = self._shape.written_for(types)
        if written != wanted:
            return self._of_another_shape(declared, named, written, wanted)
        restricted = self._restricted_precondition(declared, named, program)
        if restricted is not None:
            return restricted
        return ResolvedRole(self._name, named, written)

    def _absent(self, named: str) -> checker.Diagnostic:
        return checker.Diagnostic(
            UNRESOLVED_ROLE,
            f"WHAT: the {self._name!r} role of the descriptor names "
            f"{named!r}, and the submitted program declares no function of "
            "that name. WHY: a role is confirmed only against a function the "
            "submitted program declares, because the shape it must have is "
            "read from that declaration. HOW: declare that function in the "
            "program, or name one the program declares; the 'check' "
            "operation reports every function a program declares, and the "
            "'discover' operation publishes the shape this role needs, "
            f"{self._shape.published()}",
            about=checker.AboutARole(self._name, named),
        )

    def _of_another_shape(
        self, declared: syntax.Function, named: str, written: str, wanted: str
    ) -> checker.Diagnostic:
        return checker.Diagnostic(
            UNRESOLVED_ROLE,
            f"WHAT: the {self._name!r} role of the descriptor names "
            f"{named!r}, which the program declares as {written}, and the "
            f"role needs {wanted}. WHY: the five roles are confirmed by the "
            "shape a function declares, so a function taking or answering "
            "something else cannot stand in this one: a caller of the role "
            "would pass it a value it does not take. HOW: name a function of "
            f"the role's shape, {self._shape.published()} over the types this "
            "descriptor names, or declare the named function with that shape",
            (declared.line, declared.column),
            about=checker.AboutARole(self._name, named),
        )

    def _restricted_precondition(
        self, declared: syntax.Function, named: str, program: syntax.Program
    ):
        """The refusal of this role because a precondition narrows the
        input it is reached with, or `None`.

        Read over the role's own function and over every function
        reaching it reaches, because a clause asking something of its
        input is as binding behind a call as it is in front of one:
        SPEC.md lines 361-362 say that calls inside all helpers still
        need their own preconditions established, and this tool
        establishes none of them.
        """
        if not self._valid_for_every_input:
            return None
        asking = _the_first_asking_something(declared, program)
        if asking is None:
            return None
        if asking.name == declared.name:
            return self._asks_of_its_own_input(declared, named)
        return self._reaches_one_that_asks(declared, named, asking)

    def _asks_of_its_own_input(
        self, declared: syntax.Function, named: str
    ) -> checker.Diagnostic:
        return checker.Diagnostic(
            ROLE_PRECONDITION_RESTRICTED,
            f"WHAT: the {self._name!r} role of the descriptor names "
            f"{named!r}, which asks something of its input in its requires "
            f"clause. WHY: {self._why_it_must_hold_everywhere()} HOW: name a "
            "function whose requires clause is left out or written as "
            "'true', moving the condition into the body or into the "
            "postcondition; the step is the one role allowed to require a "
            "state, so a condition that must hold for a transition belongs "
            "there",
            (declared.line, declared.column),
            about=checker.AboutARole(self._name, named),
        )

    def _reaches_one_that_asks(
        self, declared: syntax.Function, named: str, asking: syntax.Function
    ) -> checker.Diagnostic:
        return checker.Diagnostic(
            ROLE_PRECONDITION_RESTRICTED,
            f"WHAT: the {self._name!r} role of the descriptor names "
            f"{named!r}, whose own requires clause asks for nothing, and "
            f"reaching it reaches {asking.name!r} at line {asking.line}, "
            "which asks something of its input in its requires clause. "
            f"WHY: {self._why_it_must_hold_everywhere()} A clause behind a "
            "call binds the role as much as one in front of it: running "
            f"{named!r} over an input {asking.name!r} refuses would refuse "
            "inside the role, which the 'evaluate' operation shows as a "
            "precondition violation. HOW: leave the condition out of "
            f"{asking.name!r} as well, or name a role function that reaches "
            "no function asking anything of its input; the 'verify' "
            "operation lists the preconditions each call owes",
            (declared.line, declared.column),
            about=checker.AboutARole(self._name, named),
        )

    def _why_it_must_hold_everywhere(self) -> str:
        return (
            "SPEC.md lines 359-360 require the initialiser, the projection, "
            "the invariant and the admissibility function to have "
            "preconditions valid for every input of their declared types, "
            "and lines 361-362 require the calls inside their helpers to "
            "have their own preconditions established; this tool "
            "establishes that for a clause that asks for nothing and for no "
            "other, because it reads the clause and settles nothing about "
            "it."
        )

    def _published_precondition(self) -> str:
        if self._valid_for_every_input:
            return (
                "valid for every input of its declared types, and so must "
                "every function reaching it reaches through a call, in a "
                "body or in a contract: this tool accepts a requires clause "
                "left out or written as 'true', and refuses any other, "
                "because it reads the clause and settles nothing about it "
                "(SPEC.md lines 359-360 and 361-362)"
            )
        return (
            "may require a state: SPEC.md lines 360-361 let the step ask for an "
            "invariant state, so its requires clause is read and left as it is"
        )


# The eight parts a descriptor names, in the order SPEC.md names them and
# in the order an answer reports them. Written once: the manifest
# publishes this table, a descriptor is read against it and an answer
# reports from it, so a published role and an answered role cannot
# differ.
STATE = "state"
EVENT = "event"
OUTCOME = "outcome"
THE_TYPE_ROLES = (
    TypeRole(STATE, "the type of the values the machine keeps as its state"),
    TypeRole(EVENT, "the type of the values the machine takes as its events"),
    TypeRole(OUTCOME, "the type the step answers, carrying the new state and the result"),
)
THE_FUNCTION_ROLES = (
    FunctionRole("init", RoleShape((), STATE), True),
    FunctionRole("step", RoleShape((STATE, EVENT), OUTCOME), False),
    FunctionRole("state-of", RoleShape((OUTCOME,), STATE), True),
    FunctionRole("admissible", RoleShape((STATE, EVENT), BOOL), True),
    FunctionRole("invariant", RoleShape((STATE,), BOOL), True),
)
THE_ROLES = THE_TYPE_ROLES + THE_FUNCTION_ROLES


def _roles_needing(type_role: str) -> tuple[str, ...]:
    """The function roles whose shape is written over `type_role`, read
    from the one table above, so a refusal about a type says which roles
    were left unread rather than a sentence kept by hand."""
    return tuple(
        role.name for role in THE_FUNCTION_ROLES if role.needs(type_role)
    )


def _the_first_asking_something(
    declared: syntax.Function, program: syntax.Program
) -> "syntax.Function | None":
    """The first function, reading `declared` and then every function it
    reaches through a call, whose requires clause asks something of its
    input -- or `None` when none of them does.

    Which functions reaching one reaches is asked of the checker, which
    owns that walk for its rule about cycles, so the machine module holds
    no second answer to it. A program whose calls form a cycle is refused
    before any descriptor is read, and the names already reached are kept
    anyway, so the walk ends.
    """
    reached: set[str] = set()
    waiting = [declared]
    while waiting:
        function = waiting.pop(0)
        if function.name in reached:
            continue
        reached.add(function.name)
        if checker.ContractStrength.of(function.requires).promises_something():
            return function
        waiting += [
            program.functions[name]
            for name in checker.callees_of(function, program)
            if name not in reached
        ]
    return None


def _written_kind_of(declared: object) -> str:
    if isinstance(declared, syntax.UnionType):
        return "union"
    return "record"


def _shape_of(declared: syntax.Function) -> str:
    parameters = ", ".join(
        parameter.type_name for parameter in declared.signature.params
    )
    return f"({parameters}) -> {declared.signature.return_type}"


@dataclass(frozen=True)
class NamedRoles:
    """The name a descriptor gives each of its eight roles, and nothing
    else.

    Asked for the name of a role rather than read as a table, so a shape
    written over the roles never has to know where a name was written in
    the document.
    """

    named: tuple[tuple[str, str], ...]

    def name_of(self, role: str) -> str:
        for name, given in self.named:
            if name == role:
                return given
        raise KeyError(role)


@dataclass(frozen=True)
class StatedAssumptions:
    """The assumptions a descriptor states, and nothing else.

    Carried into the answer under a name that says they are stated: this
    tool reads them and checks none of them, and a field that read as a
    property of the machine would be read as a checked one.
    """

    sentences: tuple[str, ...]

    def published(self) -> list:
        return list(self.sentences)


@dataclass(frozen=True)
class DescriptorDefects:
    """Every field of a descriptor that could not be read, each beside
    the reason it could not be.

    Several, because the fields are independent: an Owner who wrote two
    of them wrongly learns about both in one answer rather than repairing
    one and meeting the next. The service turns these into the refusal it
    gives for any field of a request it cannot read.
    """

    defects: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class ResolvedMachine:
    """The witness that all eight roles of one descriptor resolved: what
    each role resolved to, the version the descriptor was read in and the
    assumptions it states.

    The only value an answer reports a machine from, so an answer about a
    descriptor that did not resolve cannot carry a result.
    """

    roles: tuple[ResolvedRole, ...]
    assumptions: StatedAssumptions

    def published(self) -> dict:
        return {
            SCHEMA: SCHEMA_VERSION,
            ROLES: {resolved.role: resolved.published() for resolved in self.roles},
            "assumptions_stated": self.assumptions.published(),
            "what_this_says": (
                "every role the descriptor names resolves, in the submitted "
                "revision of the submitted program, to a declared type or to "
                "a checked function of the shape its role needs. It says "
                "nothing about the machine over its runs: no initialisation, "
                "preservation or admissibility claim is settled here, and the "
                "assumptions above are the descriptor's own, read and not "
                "checked. Nothing in the program was run and no obligation of "
                "it was settled: the declared examples of these functions were "
                "not run and their contracts were not put to a solver. Two "
                "other operations this manifest lists answer those two "
                "questions"
            ),
        }


@dataclass(frozen=True)
class UnresolvedRoles:
    """The refusals of the roles of one descriptor that did not resolve.

    The other outcome of resolving a descriptor, so an answer carries a
    witness or refusals and never both.
    """

    refusals: tuple[checker.Diagnostic, ...]


@dataclass(frozen=True)
class Descriptor:
    """One machine descriptor, read.

    Built only by `read` below, which refuses every field it cannot read
    by name, so a step that takes one of these is reached with a document
    whose four fields are there, whose version this tool reads, and whose
    eight roles are named. Python still lets a caller inside this tool
    build one by hand; nothing does, and the one path that reads a
    request builds it here.
    """

    named: NamedRoles
    assumptions: StatedAssumptions

    @classmethod
    def read(
        cls, submitted: object, unwritable: "object"
    ) -> "Descriptor | DescriptorDefects":
        """The descriptor `submitted` carries, or every field of it that
        could not be read.

        `unwritable(field, text)` is the rule about a text this tool can
        write, asked of the caller that owns it: every text a request
        carries is turned back into bytes somewhere, and half of a
        character has none. It is asked here, where the document is
        walked once, rather than by a second walk at the boundary.
        """
        if not isinstance(submitted, dict):
            return DescriptorDefects(
                (
                    (
                        FIELD,
                        f"WHAT: the {FIELD!r} field of the request holds "
                        f"{type(submitted).__name__}, not a descriptor "
                        "document. WHY: a machine is named by the four fields "
                        f"{checker.listed(THE_DOCUMENT_FIELDS)} of one "
                        "document, and a value of another kind has none of "
                        "them. HOW: send the descriptor as one JSON object; "
                        "the 'discover' operation publishes its shape under "
                        "'machine_descriptor_schema'",
                    ),
                )
            )
        defects: list[tuple[str, str]] = []
        defects += _unknown_fields_in(submitted)
        unreadable = _unwritable_texts_in(submitted, unwritable)
        defects += unreadable
        # The version is read from its text, so a text this tool cannot
        # write is not also reported as the wrong version: that check
        # depends on this one and did not run.
        if f"{FIELD}.{SCHEMA}" not in {field for field, _ in unreadable}:
            defects += _version_defects_in(submitted)
        named, naming_defects = _named_roles_in(submitted)
        defects += naming_defects
        assumptions, assumption_defects = _assumptions_in(submitted)
        defects += assumption_defects
        if defects:
            return DescriptorDefects(tuple(defects))
        return cls(named, assumptions)

    def resolved_against(
        self, program: syntax.Program
    ) -> "ResolvedMachine | UnresolvedRoles":
        """What the eight roles of this descriptor resolve to in
        `program`, or the refusals of those that did not.

        The three types are resolved first: a shape is written over them,
        so a type nothing declares leaves the five function roles with no
        shape to read, and its own refusal says so.
        """
        types, refused = self._resolved(THE_TYPE_ROLES, program)
        if refused:
            return UnresolvedRoles(tuple(refused))
        functions, refused = self._resolved(THE_FUNCTION_ROLES, program)
        if refused:
            return UnresolvedRoles(tuple(refused))
        return ResolvedMachine(tuple(types) + tuple(functions), self.assumptions)

    def _resolved(self, roles: tuple, program: syntax.Program) -> tuple[list, list]:
        resolved: list[ResolvedRole] = []
        refused: list[checker.Diagnostic] = []
        for role in roles:
            answer = role.resolve(self.named.name_of(role.name), program, self.named)
            if isinstance(answer, ResolvedRole):
                resolved.append(answer)
                continue
            refused.append(answer)
        return resolved, refused


def _unwritable_texts_in(submitted: dict, unwritable) -> list[tuple[str, str]]:
    """Every text of the document this tool cannot write, named by the
    field it stands in.

    Read before any name is looked up and before the program is read:
    this tool writes every text a request carries back into its answer,
    so a text it cannot write must be refused where it stands rather
    than taken as far as the answer, where the field it came from is no
    longer known.
    """
    defects: list[tuple[str, str]] = []
    for field, written in _texts_of(submitted):
        reason = unwritable(field, written)
        if reason is not None:
            defects.append((field, reason))
    return defects


def _texts_of(submitted: dict) -> list[tuple[str, str]]:
    """Every text the document carries, each beside the name of the field
    it stands in, walked from the one description of the document."""
    found: list[tuple[str, str]] = []
    version = submitted.get(SCHEMA)
    if isinstance(version, str):
        found.append((f"{FIELD}.{SCHEMA}", version))
    for group in (TYPES, ROLES):
        written = submitted.get(group)
        if not isinstance(written, dict):
            continue
        found += [
            (f"{FIELD}.{group}.{role}", given)
            for role, given in written.items()
            if isinstance(given, str)
        ]
    stated = submitted.get(ASSUMPTIONS)
    if isinstance(stated, list):
        found += [
            (f"{FIELD}.{ASSUMPTIONS}[{place}]", sentence)
            for place, sentence in enumerate(stated)
            if isinstance(sentence, str)
        ]
    return found


def _unknown_fields_in(submitted: dict) -> list[tuple[str, str]]:
    return [
        (
            f"{FIELD}.{written}",
            f"WHAT: the descriptor carries a field {written!r}, which this "
            f"tool does not read. WHY: the shape of a descriptor is fixed "
            f"per version, and {SCHEMA_VERSION!r} has the four fields "
            f"{checker.listed(THE_DOCUMENT_FIELDS)}; a field read by nobody "
            "would carry a part of the machine that nothing is said about. "
            f"HOW: take {written!r} out of the document, or write what it "
            "says under one of the four fields the 'discover' operation "
            "publishes under 'machine_descriptor_schema'",
        )
        for written in submitted
        if written not in THE_DOCUMENT_FIELDS
    ]


def _version_defects_in(submitted: dict) -> list[tuple[str, str]]:
    written = submitted.get(SCHEMA)
    if written == SCHEMA_VERSION:
        return []
    return [
        (
            f"{FIELD}.{SCHEMA}",
            f"WHAT: the descriptor is written in the version {written!r}, "
            f"and this tool reads {SCHEMA_VERSION!r}. WHY: the shape of a "
            "descriptor is fixed per version (SPEC.md line 353), so a "
            "document of a version this tool has never read cannot be read "
            f"by guesswork. HOW: write {SCHEMA_VERSION!r} under {SCHEMA!r} "
            "and the fields that version publishes, which the 'discover' "
            "operation lists under 'machine_descriptor_schema'",
        )
    ]


def _named_roles_in(submitted: dict) -> tuple[NamedRoles, list[tuple[str, str]]]:
    defects: list[tuple[str, str]] = []
    named: list[tuple[str, str]] = []
    for field in (TYPES, ROLES):
        written = submitted.get(field)
        if not isinstance(written, dict):
            defects.append(_not_an_object(field, written))
            continue
        expected = tuple(
            role.name for role in THE_ROLES if role.stands_in() == field
        )
        defects += [
            (
                f"{FIELD}.{field}.{role}",
                f"WHAT: the {field!r} field of the descriptor carries a role "
                f"{role!r}, which a descriptor does not name. WHY: the roles "
                f"of {field!r} are {checker.listed(expected)}, and a role no "
                "rule reads would name a part of the machine nothing is said "
                f"about. HOW: take {role!r} out, or write it under the role "
                "it fills",
            )
            for role in written
            if role not in expected
        ]
        for role in expected:
            given = written.get(role)
            if isinstance(given, str) and given.strip():
                named.append((role, given))
                continue
            defects.append(_not_a_name(field, role, given))
    return NamedRoles(tuple(named)), defects


def _not_an_object(field: str, written: object) -> tuple[str, str]:
    expected = tuple(role.name for role in THE_ROLES if role.stands_in() == field)
    return (
        f"{FIELD}.{field}",
        f"WHAT: the {field!r} field of the descriptor holds "
        f"{type(written).__name__}, not an object naming "
        f"{checker.listed(expected)}. WHY: each of those roles is one part of "
        "the machine, and a value of another kind names none of them. HOW: "
        f"write {field!r} as a JSON object with one text under each of "
        f"{checker.listed(expected)}",
    )


def _not_a_name(field: str, role: str, given: object) -> tuple[str, str]:
    held = "nothing" if given is None else f"{type(given).__name__}"
    return (
        f"{FIELD}.{field}.{role}",
        f"WHAT: the {role!r} role of the descriptor holds {held}, not the "
        f"name of a {'type' if field == TYPES else 'function'} the program "
        f"declares. WHY: a role is resolved by looking its name up in the "
        "submitted program, and a value of another kind, or an empty text, "
        f"names nothing to look up. HOW: write one text under "
        f"{field!r}.{role!r}, naming a "
        f"{'type' if field == TYPES else 'function'} the program declares",
    )


def _assumptions_in(submitted: dict) -> tuple[StatedAssumptions, list[tuple[str, str]]]:
    written = submitted.get(ASSUMPTIONS)
    if not isinstance(written, list) or not written:
        return StatedAssumptions(()), [
            (
                f"{FIELD}.{ASSUMPTIONS}",
                f"WHAT: the {ASSUMPTIONS!r} field of the descriptor holds "
                f"{'an empty list' if isinstance(written, list) else type(written).__name__}, "
                "not at least one sentence. WHY: SPEC.md lines 351-352 ask a "
                "descriptor to state the assumptions its runtime makes, and "
                "the evidence about a machine is conditional on them "
                "(SPEC.md line 416); a descriptor stating none would "
                "leave a reader of the answer with nothing to read them "
                "from. HOW: write the assumptions as a JSON list of "
                "sentences, such as that the runtime applies one event at a "
                "time over one authoritative state",
            )
        ]
    defects = [
        (
            f"{FIELD}.{ASSUMPTIONS}[{place}]",
            f"WHAT: the assumption at place {place} of the descriptor holds "
            f"{type(sentence).__name__}, not a sentence. WHY: the "
            "assumptions are carried into the answer as the descriptor "
            "states them, and a value of another kind states nothing. HOW: "
            f"write the assumption at place {place} as one JSON string",
        )
        for place, sentence in enumerate(written)
        if not isinstance(sentence, str) or not sentence.strip()
    ]
    if defects:
        return StatedAssumptions(()), defects
    return StatedAssumptions(tuple(written)), []


def published_schema() -> dict:
    """The descriptor shape an agent writes a descriptor from: its
    version, the four fields of the document and the eight roles with
    what each one resolves to.

    Read from the same table the reader and the resolution read, so a
    role an agent meets in an answer is one it can look up here, and a
    role published here is one an answer carries.
    """
    return {
        "version": SCHEMA_VERSION,
        "document": {field.name: field.published() for field in THE_DOCUMENT},
        ROLES: {role.name: role.published() for role in THE_ROLES},
        "what_an_answer_says": (
            "A completed answer says that each of the eight roles resolves, "
            "in the submitted revision of the submitted program, to a "
            "declared type or to a checked function of the shape its role "
            "needs, and it records the version the descriptor was read in. "
            "It settles no claim about the machine over its runs -- not "
            "initialisation, not preservation of an invariant, not "
            "admissibility -- and the assumptions it carries are the "
            "descriptor's own, read and not checked. A refusal names the "
            f"role that did not resolve, under {UNRESOLVED_ROLE!r} when the "
            "name is absent or of another shape and under "
            f"{ROLE_PRECONDITION_RESTRICTED!r} when a role that must hold "
            "for every input of its declared types asks something of its "
            "input; a field of the document this tool cannot read is "
            "refused as a malformed request naming that field, with every "
            "such field in one answer"
        ),
    }
