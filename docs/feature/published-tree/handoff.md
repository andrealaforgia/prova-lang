# F12 handoff: reading a program

## What a reader gets

Ask the tool to read a program and it answers the tree it built: one node
per part of the program, each saying what it is and where it stands. The
comments written in the source come back with it, each on the first node
standing after it, or at the end of the document when nothing follows.
A program that breaks a rule of core-0 is refused exactly as a check
refuses it, and no tree is published for it. The manifest advertises the
operation, publishes what it takes and what it answers, and publishes the
shape of the tree.

## How it was checked

Three pairs under `conformance/parse` fix the schema: a source, and the
tree it must be answered with, written by hand from the text before the
code existed. Six acceptance files ask the service through its public
operation, one of them through the real command. Three laws over
generated programs hold the places, the comments and the agreement with
`check`, all derandomised so two runs draw the same cases.

Two independent reviews were answered. The first rejected the work with
eight findings; every one was repaired, and each repair was checked by
putting the wrong behaviour back and watching a test fail. The second
approved it with three notes: the place of a pattern, a clause and a
binding is now pinned by a published pair, so a tool that put them all at
line 1 column 1 fails; the refusal to build a part of a program without
its place is now observed by a unit test; and the third note is answered
below.

## What is verified by reading only

The published schema says a field and a parameter stand at the name they
declare rather than at the parenthesis that opens the pair. That sentence
is prose inside a machine-readable document, and the test mandates forbid
pinning the wording of documentation, so no test asserts it. The
behaviour it describes is pinned: the published pairs carry the exact
place of every field and parameter in them. If the sentence goes stale
while the behaviour stays right, nothing fails.

## What was not verified

- No linter and no type checker is configured here, so the mechanical
  check only compiles the package and the tests.
- Jev was unreachable for the whole run, so every open choice was settled
  locally and written down.
- A tree of a program nesting close to the published reading limit was
  never published: the reader refuses such a text before a tree is built,
  and nothing measures how large an answered tree may become.
- The craft step could not be recorded again after this branch moved onto
  main; the exact refusal was reported to the owner and nothing was
  decided here.
