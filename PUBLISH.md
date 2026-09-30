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
node site/bo.test.mjs
python registry/legacy/validate_inventory.py
python site/build_evidence.py
git diff --check
```

Check whether `site/evidence.html` changed after regeneration; commit it with
the corresponding `registry/atlas.csv` edit. The inventory validator checks
the dated source receipt and its GitHub Pages copy. IDA Live has its own
dependencies and checks in `apps/ida-live/README.md`. CI runs the site maths,
toolkit, current atlas, dated inventory and IDA checks.

Check the home page, Atlas, Library, Labs, IDA Live, Papers and Contribute
pages after deployment. The Library is a text-light, source-pinned receipt of
the earlier Atlas. The old Observatory remains a separate runnable project:
its server routes, database and live features cannot be copied unchanged to
GitHub Pages. Labs indexes its experiments, results and room source routes.

## Preserving the earlier work

Keep `boundedness-atlas`, `empirical-observatory`, `empirical-architecture`
and `ida-stateatlas` online for source history and deep links. The profile
README groups them in a collapsed archive below the new entry. Do not delete
or force-push their histories. The current `registry/atlas.csv` is the claim
classification for this project; `registry/legacy/` keeps the dated wider
programme inventory without reproducing manuscript prose or 471 page images.

## Rights

New code is MIT (`LICENSE`), and original text and figures are CC BY 4.0
(`LICENSE-CONTENT`). The inventory does not relicense the earlier manuscripts,
datasets, images or linked repositories. See `registry/legacy/README.md`.
