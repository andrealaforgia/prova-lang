"""Closed core-0 values: Unit, Bool, Int and named constructors."""

from __future__ import annotations

from dataclasses import dataclass


class Unit:
    """The sole value of type Unit, rendered `()`."""

    _instance: "Unit | None" = None

    def __new__(cls) -> "Unit":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Unit)

    def __hash__(self) -> int:
        return hash(Unit)

    def __repr__(self) -> str:
        return "()"


UNIT = Unit()


@dataclass(frozen=True)
class ConstructorValue:
    """A record or union-variant value: a constructor name plus its
    ordered field values."""

    constructor: str
    fields: tuple[object, ...]

    def field(self, index: int) -> object:
        return self.fields[index]


def render(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Unit):
        return "()"
    if isinstance(value, ConstructorValue):
        if not value.fields:
            return f"({value.constructor})"
        rendered_fields = " ".join(render(f) for f in value.fields)
        return f"({value.constructor} {rendered_fields})"
    raise TypeError(f"not a core-0 value: {value!r}")
