# R3 oracle: what was promised, and what proves it

## What this delivery is about

Four inputs still ended in something other than an answer about the
request: an integer a program computes but the tool cannot write, a
budget variable holding thousands of digits, a request whose own JSON
nests thousands of arrays deep, and half a character echoed back in the
operation field. Each one now gets one JSON answer that names what
stopped it.

## The promises

| # | A caller can now see |
|---|---|
| P1 | An evaluation whose result is too large to write is refused at the function that computed it, with the limit and the digits reached |
| P2 | Running the declared examples of that program gives the same refusal, not a report that the tool failed |
| P3 | An integer at or below the limit comes back exactly, however far past 64 bits |
| P4 | A budget variable this tool cannot read as a number is refused by name, and a number a caller may lower to is still read |
| P5 | A request nesting deeper than the tool reads is told so; a request at the limit is answered as before |
| P6 | The manifest states how deep a request may nest and how many digits an answer writes, each with its reason |
| P7 | An operation field holding a character that cannot be written as UTF-8 is named with the character position, and never echoed |
| P8 | A budget variable named with such a character is refused without repeating the name |
| P9 | The derandomised fuzz sends all four families, and everything answered before is answered as before |
| P10 | No answer this tool prints carries a text that cannot be written as UTF-8 |

## The decisions taken, and why

**Where the new limit is published.** Acceptance criterion 1 offered two
places. Publishing a third name under `resource_limits.limits` would
break `test_f14_b9_the_limits_published_before_still_stand.py`, which
pins that map to exactly two names, and the request forbids editing an
existing test. The other option, the budget refusal
`output_budget_exceeded`, is declared in the tool's own table of refusal
shapes as carrying no place at all, so it could not be the *located*
refusal the criterion asks for, and its numbers (bytes of an answer
against a megabyte) would be false for a 5000-digit value. The owner
was absent, so the recorded decision is a third reading of the same
sentence: a new **diagnostic** category, `written_integer_digits_exceeded`,
published among the categories and their schemas and documented under
`computed_integers`, while `resource_limits.limits` keeps its two names.

**Refuse or write.** A value past the limit is refused. The request
calls refusal the safe default; writing a number of unbounded length
would put work with no stated bound between the caller and its answer.

**The numbers.** 4000 digits for an integer an answer writes, below the
4300 the interpreter writes as one number, far above the 20 digits of a
64-bit value and the 1000 digits of the longest literal the tool reads.
64 arrays or objects for the nesting of a request, counting the request
object: the deepest request this tool answers nests 2, and 64 leaves
the interpreter's own 1000 frames untouched.

**No formal model.** Each of the four is a decision about one input,
inside one process, with no state kept between runs, no concurrency and
no protocol. A Quint model would restate the code.

**No remote question service** was used: the host running this delivery
forbids one.

## What proves each promise

Four acceptance files drive the real `prova` command over its own
standard input and output, one per family; a property file extends the
derandomised fuzz with the four families and four generated laws; a
unit test exercises the last check before an answer is printed, which no
accepted request reaches. Every one of them failed first on the tree as
it was before the change; that run is recorded in the workspace journal.

## Still open

A budget variable whose *name* cannot be written is observed only
through a real command, not in the in-process fuzz: a running process
cannot hold such a variable, because its environment is written in
bytes.
