# September 2026 source inventory

This folder carries a compact, dated source receipt for the wider research
programme. It supports the site's [Research library](../../site/library.html)
and [Laboratories](../../site/labs.html) pages without moving the earlier
projects' runnable code or copying full manuscript text.

## Provenance

- Source: [Boundedness Atlas at `29a0cfca`](https://github.com/thantiklermcirony/boundedness-atlas/tree/29a0cfca16ac088cd08e0267b07a50c20eacbc9b), especially
  [`content/atlas.json`](https://github.com/thantiklermcirony/boundedness-atlas/blob/29a0cfca16ac088cd08e0267b07a50c20eacbc9b/content/atlas.json).
- Source inventory date: **13 September 2026**.
- Earlier laboratory status: [Empirical Observatory at `2ae59b3f`](https://github.com/thantiklermcirony/empirical-observatory/tree/2ae59b3fbc392f2200399631e2892677da146cad).
- `atlas-2026-09.json` retains 41 manuscript metadata records, 41 research
  families, 41 original numbered prediction items and 471 page addresses.
  Original keys and IDs are unchanged. Each paper and prediction carries a
  deep link into the exact prior source revision.
- `../../site/library-data.json` is an identical deployment copy for GitHub
  Pages. The original source file SHA-256 is recorded inside both copies.

## Selection and status

`build_inventory.py` takes the old `content/atlas.json` as an explicit input and
allows only a named set of bibliographic, summary, status, test and provenance
fields into this project. Full abstracts, closing sections, numbered-prediction
source text and all 471 page excerpts are **excluded**. Page numbers and the
original source links remain so a reader can inspect the exact passage.

The source statuses are reported as of that inventory's date. The current
`../atlas.csv` classifies the works for the Bounded Observer's six-gate argument
and may supersede an older claim. A source hash identifies supplied PDF bytes;
it does not verify a proof, novelty, an experiment or online SSRN version parity.

## Rebuild

With a checkout of the dated Boundedness Atlas:

```sh
python registry/legacy/build_inventory.py /path/to/boundedness-atlas/content/atlas.json
```

The script checks all three published counts and source IDs before writing both
copies. It needs only Python's standard library.

Run the checked-in preservation gate after any edit:

```sh
python registry/legacy/validate_inventory.py
```

It checks the unique paper and prediction IDs, source and page relationships,
pinned source URLs, the absence of manuscript excerpt fields, and the identical
GitHub Pages copy.

## Rights

The prior Atlas did not place its manuscripts or earlier work under a blanket
license. Each paper and third-party source keeps its original terms. This
compact inventory and the site's new summaries do not relicense the original
manuscripts or their quoted passages.
