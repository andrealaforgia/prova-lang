# F3 self-review

All seventeen review dimensions were answered against the committed change.
None was left as debt: fifteen passed on the change as written, and two are
marked not applicable with their reason.

## What the review found worth saying

- **One owner per fact.** The wording that lists several places, the sentence
  of the rule each kind of name obeys, and the programs the tests use each
  live in exactly one place.
- **The value refuses the invalid case at its constructor.** A declared name
  with no spelling cannot be built, so a refusal that could not say which name
  to repair cannot exist.
- **The tests reach the tool only through the command.** They import nothing
  from the source, and the places they expect are read from their own fixture
  text rather than from the checker.
- **The law is generated, not tabulated.** The property decides the expected
  verdict from the generator's own data before the program text is written.
- **Cost.** 17 added tests, nine consecutive runs, median 0.56 s for the set,
  slowest single test 0.06 s.

## Not applicable, with reasons

- **Design patterns.** The change is one value object, one collection of them
  and one pass that reads it. Further indirection would hide the rule.
- **Formal model.** The rule holds no state, speaks no protocol and runs
  nothing concurrently, so a model would restate the pass line for line.

## Independent review

None happened. No agent other than the executor exists in this run, so nothing
here is an independent verdict. The change is handed off for the independent
review and the blind examination that follow, with the superseded expectation
and the now unreachable `resolve_constructor` branch named for them.
