"""What this tool is made of, as an answer reports it.

An answer says which text it is about and which tool read it. This
module owns the second half of that: the digest over a text, and, beside
it, what stands behind an answer.

It reads nothing of a program and decides nothing about one: a client
compares what two answers stand on, and two answers that agree here were
read by the same tool from the same language.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Digest:
    """The SHA-256 of one text, written as the hexadecimal a client
    recomputes for itself.

    Built only by hashing a text, so nothing hands a client a digest it
    did not compute from characters. One place writes the algorithm: the
    revision of a submitted source and the digest over this tool's own
    description are then spelled the same way, and a client comparing
    the two never has to ask which spelling it holds.
    """

    hexadecimal: str

    @classmethod
    def of(cls, text: str) -> "Digest":
        return cls(hashlib.sha256(text.encode("utf-8")).hexdigest())

    def rendered(self) -> str:
        return self.hexadecimal
