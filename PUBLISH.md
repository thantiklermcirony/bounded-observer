# Publishing The Bounded Observer

This folder is the standalone release copy for
`https://github.com/thantiklermcirony/bounded-observer`. The Desktop research library is the
source archive and should stay intact. The older GitHub repositories are separate projects and
should stay available.

## 1. Check the destination

Open `https://github.com/thantiklermcirony/bounded-observer`. If it does not exist, create a
repository named `bounded-observer` under `thantiklermcirony`. Choose public visibility when
ready to publish. Do not add a GitHub-generated README, license, or `.gitignore`: this folder
already contains them. If the repository already exists, inspect its branches and contents
before pushing; do not force-push over existing work.

## 2. Verify the release copy

Run these checks from this folder with Python 3.10 or newer and Node.js 20 or newer:

```bash
python -m pip install -e "toolkit[test]"
python -m pytest toolkit/tests -q
node site/bo.test.mjs
python site/build_evidence.py
```

The last command regenerates `site/evidence.html` from `registry/atlas.csv`. Check the resulting
diff before committing. IDA Live has its own dependencies and tests in `apps/ida-live/README.md`.
The `.github/workflows/tests.yml` workflow runs the toolkit, site, atlas, and IDA Live checks on
GitHub.

## 3. Push this folder as its own repository

From this folder, after the destination has been checked:

```bash
git init -b main
git add -A
git commit -m "Publish The Bounded Observer research programme"
git remote add origin https://github.com/thantiklermcirony/bounded-observer.git
git push -u origin main
```

GitHub Desktop can also add this folder as a local repository and publish it to the same
account. The `.github/` workflows and issue templates are already included in this copy.

## 4. Enable the site

In the new repository, open **Settings → Pages**, set **Build and deployment → Source** to
**GitHub Actions**, and run or re-run the `site` workflow if needed. It builds the atlas page
and deploys `site/` to `https://thantiklermcirony.github.io/bounded-observer/`. Check that the
home page, Atlas, IDA Live, Papers, and Contribute pages load and that their source links lead
back to this repository.

## 5. Preserve the existing public work

Keep `empirical-architecture`, `empirical-observatory`, `boundedness-atlas`, and
`ida-stateatlas` available. Any later README pointers or atlas migration should be reviewed
against their current public contents as a separate change. This release does not archive,
delete, or overwrite them.

## Data and licences

Code is MIT (`LICENSE`); text and figures are CC BY 4.0 (`LICENSE-CONTENT`). Confirm these
terms before publishing. Raw EEG recordings in `Documents\IDA Live`, `web/samples.zip`, and the
OpenMuse test recording are not in this repository. `apps/ida-live/NOTICE.md` identifies the
third-party material and omitted test recording.
