# F17, step 4 of 5: the self-review

Seventeen dimensions were answered. Three of them were not a pass when
first read, and were repaired rather than written down as debt.

| Dimension | What was wrong | What was done |
|---|---|---|
| One source of truth | The SHA-256 of a text had two writers, and the `discover` answer repeated the text of a field the manifest already publishes. | The prefactor commit left one writer; the answer now reuses the published field. |
| Wrong states unrepresentable | Nothing refused a set of versions that was not the four, or a version with nothing said about it. | Both refuse at construction, each with what failed, why it matters and how to repair it. |
| Property tests | Two laws drew twelve cases from a closed grid of thirty cells. | They draw one case per cell, and the case count is written as the size of the grid. |
| Documents | The cost written here was measured on an earlier tree. | Re-measured on this one. |

Two dimensions do not apply, with the reason recorded: no design pattern
was introduced, the shapes are the ones this repository already uses; and
no formal model, because the change adds no state, no protocol, no
concurrency and no crash window.

## The independent review

A reviewer other than the author read the change and approved it, with
one medium defect and four notes. All of them are answered in
`craft.md`, under "What changed after the review". Each repair was seen
to fail once with the old behaviour put back, so none of them is a check
that cannot fail.
