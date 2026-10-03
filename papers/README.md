# Papers

| Paper | Status | Where |
|---|---|---|
| **Bounded Composition and Its Horizons** (the capstone) | v2.1 ready; four specialist readers, then submission | `capstone/` |
| The Observer and the World (the grammar) | On SSRN; revision to point down to the capstone, after the capstone's readers report | [SSRN 7347861](https://papers.ssrn.com/abstract=7347861) |
| Hormesis as a geometric necessity | **Published** | [SSRN 6858819](https://papers.ssrn.com/abstract=6858819) |
| A dynamical model of glutathione homeostasis | **Published** | [SSRN 6754498](https://papers.ssrn.com/abstract=6754498) |
| Finite rescue windows in NRF2-active cancer | Major revision in progress | [SSRN 7181465](https://papers.ssrn.com/abstract=7181465) |
| The classification (boundary exponent and cone type decide the geometry) | **Not yet written.** The only open path to a prediction that can win | — |
| IDA Live, the software | **Not yet written.** The repository is public and its tests run in CI | `../apps/ida-live/` |

The full list of the author's SSRN records, and where each sits in the programme, is in
`../registry/atlas.csv`.

## The capstone

`capstone/` holds the source of *Bounded Composition and Its Horizons: when a bounded quantity
earns an additive chart, a horizon and a geometry*, version 2.1, 30 September 2026. 57 pages.

Build it with `python papers/capstone/build.py --out <dir>` from any working directory. It
needs pandoc (or `pip install pypandoc_binary`) for HTML and DOCX, and Python Playwright with
Chromium for the PDF (`--chromium <path>` if the bundled revision is not installed).
`figs.py` regenerates the six figures. The part files `00_front.md` through `05_appendix.md` are
the source of record. The build writes only to `--out`; it never overwrites the archived v2.1
Markdown or PDF.

**The original stylesheet is not in the repository.** The v2.1 build used a `style.css` that was
never committed, so a rebuild renders with pandoc's default styling and does not match the
archived PDF's look: 58 pages against 57. A clean-checkout build on 3 October 2026 is recorded in
[`capstone/build-verification-2026-10-03.json`](capstone/build-verification-2026-10-03.json),
with source commit, source hashes, tools and output hashes. Its Markdown is byte-identical to
the archived concatenation, and its PDF carries the v2.1 footer, all six figures and rendered
MathML. That build is a check of the build, not a new release; its outputs are not committed.

**Later versions.** The author reports a locally reviewed v2.7. **v2.7 not recovered:** it is in
no repository, branch, tag, archive or Drive location searched. v2.1 is the latest version in
this repository; that does not make it the current manuscript. The errata below are against
v2.1 and still need reconciling with v2.7.

Versions 1.0, 1.1 and 2.0 are kept unchanged in the author's research library. The claim
register in §15 has 35 rows. The puzzle register in §12 has 38 entries: 12 re-read by the law,
11 located (turned into a test), 15 outside its conditions. Corrections found after v2.1 was
built are listed in [`capstone/ERRATA_v2.1.md`](capstone/ERRATA_v2.1.md).
