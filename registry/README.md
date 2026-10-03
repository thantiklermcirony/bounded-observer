# The atlas

`atlas.csv` places every work in the programme as a chart of the law.

| Column | What it holds |
|---|---|
| `work` | Internal identifier |
| `short_title` | The work |
| `ssrn` | SSRN record, or `pending` |
| `layer` | Core, Foundations, Observer and state, Physics / Life / Mind chart, or **Outside UHL** |
| `uhl_section` | Where the capstone treats it |
| `bounded_quantity` | What is bounded, and by what |
| `chart` | Which rapidity chart applies |
| `verdict_status` | Status tag and what it rests on |
| `next_test` | **What would move it** |
| `last_result` | What happened when a test ran |

Two rules give the file its meaning.

**Every row has a next test.** A row with no next test is a row that cannot be wrong, and it
does not belong in a register. Two kinds of row are kept for the record but carry no test of
their own: a superseded row (L-U) and a synthesis row (L-A). Each names the rows that carry its
tests, and neither counts as evidence by itself.

**The `Outside UHL` layer is real.** Three works sit there: their conditions are not met, and
the law says nothing about them. Keeping them listed is what stops "universal" from meaning
"unfalsifiable". The law is universal over its four conditions C1–C4 and over nothing else.

Adding a row: see `../CONTRIBUTING.md`. You will be asked for the bounded quantity, its
ceiling, the neutral state, the composition operation, the chart, and one prediction with a
loss condition.
