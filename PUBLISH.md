# Maintaining the published Bounded Observer

The public source is [thantiklermcirony/bounded-observer](https://github.com/thantiklermcirony/bounded-observer).
GitHub Actions publishes `site/` at
<https://thantiklermcirony.github.io/bounded-observer/> after a push to `main`.
The GitHub profile points readers to that site and pins this repository.

## Before publishing a change

Run from the repository root with Python 3.10+ and Node.js 20+:

```sh
python -m pip install -e "toolkit[test]"
python -m pytest toolkit/tests -q
python registry/validate_programme.py
node site/bo.test.mjs
node --test site/inside-core.test.mjs
node --test site/valley-world.test.mjs
node --test site/radiation-model.test.mjs
node --check site/inside.js
node --check site/valley-view.mjs
node --check site/inside-film.mjs
node --check site/inside-film-player.js
python registry/legacy/validate_inventory.py
python site/build_evidence.py
python site/build_programme.py
git diff --check
```

Commit generated `site/evidence.html` with its corresponding `registry/atlas.csv`
edit. The branch and publication registries generate `site/project.html`,
`site/papers.html` and the current work section of `site/labs.html`; commit those
pages with their source changes. Regeneration must leave these pages unchanged
in a clean checkout. The programme validator verifies branch contracts, local
links and the exact publication snapshot bytes. CI also runs the toolkit,
browser models, legacy inventory and IDA simulator checks. IDA setup and the
minimal cross-platform simulator route are in [LAB.md](LAB.md).

Check Project, the Walk, Inside, Atlas, Library, Labs, IDA Live, Radiation,
Papers and Contribute
pages after deployment. The Library is a text-light, source-pinned receipt of
the earlier Atlas. The old Observatory remains a separate runnable project:
its server routes, database and live features cannot be copied unchanged to
GitHub Pages. Labs indexes its experiments, results and room source routes.

## Preserving the earlier work

Keep `boundedness-atlas`, `empirical-observatory`, `empirical-architecture`
and `ida-stateatlas` online in their declared component and history roles.
Do not delete or force-push their histories. The current project registry is
`registry/branches.json`; `registry/atlas.csv` retains the earlier claim atlas,
and `registry/legacy/` preserves the dated wider programme inventory. Frozen
v2.1 remains under `papers/capstone/`. The October library remains byte-for-byte
under `papers/library-2026-10-12/`; reproduce its receipt-writing checks in a
separate working copy. Its later submission/licensing status is recorded in
[the dated publication receipt](papers/PUBLICATION_STATUS_2026-10-13.md).

## Rights

New code is MIT (`LICENSE`), and original text and figures are CC BY 4.0
(`LICENSE-CONTENT`). The inventory does not relicense the earlier manuscripts,
datasets, images or linked repositories. See `registry/legacy/README.md`.
