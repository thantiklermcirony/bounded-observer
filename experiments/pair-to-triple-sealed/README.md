# Pair-to-triple data: sealed, quarantined

> **Status: not begun; data sealed; no hypothesis tested.**
>
> This folder archives *where* the data came from and *how* it was sealed. It contains no data,
> no design, no model and no result. Nothing here supports or refutes any claim.

## What happened

On 3 October 2026 (UTC, 09:40–10:08), during a search later stopped by the author, agents
searched public GitHub repositories for drug-combination data with three or more agents. They
cloned 49 repositories at fixed commits. From 13 of them they wrote 27 "sealed" files that hold
every combination of three or more agents, and 15 calibration extracts that hold single agents
and pairs only. The work was then stopped before any design was frozen, so no test exists.

The sealed and calibration files lived only in temporary session storage
(`/tmp/claude-0/stage1/triples/`), which is lost when the session ends. This archive preserves
everything needed to rebuild and check them, without the data itself.

| File | What it is |
| --- | --- |
| `MANIFEST.json` | Every sealed file and calibration extract, with bytes, SHA-256, UTC seal time, source repository, commit, source paths, selection rule, script, access status and licence. It also lists all 49 cloned repositories, with commit, role and licence evidence, and SHA-256 of each source file used. |
| `acquire.py` | Clones the source repositories at the recorded commits and verifies every source file's SHA-256. It prints names and PASS/FAIL only. |
| `verify_sealed.py` | Checks a directory of sealed files (and optionally the calibration extracts) against the manifest by size and SHA-256. It never displays contents. |
| `extraction/` | The ten sealing scripts, archived unmodified as they ran, with `SHA256SUMS.scripts`. |

**Checked when archiving.** The commands were run on 3 October 2026 against the session copies:
- `python verify_sealed.py --sealed /tmp/claude-0/stage1/triples/sealed --calibration /tmp/claude-0/stage1/triples`
  reported "all files match the manifest", for 27 sealed and 15 calibration files.
- `python acquire.py --only bg_ncats_tact bg_SvL-1_mixdra` re-acquired both repositories at their
  recorded commits, and all four source files matched.

The full acquisition was not re-run.

## How the files were handled

Each sealed file has an `access_status` in the manifest:
- **parsed (22 files).** A script loaded the source into memory and selected rows by how many
  agents were present. Per the recording agents, the response values were written to the
  sealed file without being displayed. That is the agents' record and cannot be independently
  verified.
- **verbatim copy (5 files).** The bytes were copied without parsing: two TACT tables, the
  mixdra workbook and two NCATS 10023 files. Acquisition at the recorded commit reproduces them
  exactly, as checked by hash.

The 15 calibration extracts (singles and pairs) **were opened and inspected**. They were meant
to be inspected.

The other 36 repositories were cloned and searched, but nothing was sealed from them.

## Why the blind may already be compromised

Read this before treating any later analysis of these files as out-of-sample.

1. **One sealed source is recorded as viewed.** The sweep record for NCATS assay 10023
   (`responses.csv`, `calc.csv`) says `triple_outcomes_viewed: true`; its synergy score columns
   were described. It also is not established that this assay contains a third drug at all.
2. **Every dataset has been published and analysed before.** The record for each:
   - MAGENTA trained on pairs and predicted these 56 triples, and both its predictions and the
     measured values are among the sealed files.
   - CARAMeL, M2D2 and INDIGO reuse these scores as training and test data.
   - Lozano-Huntelman et al. 2021 was re-analysed by Chitra et al. 2025.
   - SynergyFinder publishes synergy scores for its two NCATS triples.
   - van Loon et al. 2025 analysed concentration addition against independent action on the
     mixdra ternaries.
   - RGCA, TACT and EHP7600 each come with the authors' own analyses.

   Their published conclusions may be known to any analyst, including a language model through
   its training data. The blind holds only against *this programme's* own analysis.
3. **Agents had programmatic access to the values.** Parsing put response values in memory.
   That they were not displayed rests on the agents' records.
4. **File access times are no longer evidence.** The archival hashing on 3 October read every
   sealed file, so earlier reads, if any, cannot be detected from access times.
5. **The stopped run.** Per-dataset feasibility agents were running when the work was stopped.
   They were instructed to use triple *doses* only. Whether any of them read a sealed file is
   unknown, and they saved no output.
6. **Some sealed files are derived outcomes, not raw data:** interaction scores, published
   predictions and NCATS synergy scores.

## Licences and redistribution

**No data file is committed: none of the sealed files, calibration extracts or raw clones.**
The reasons:
- several licences are unresolved: EHP7600 has no licence file, the NCATS upstream terms were
  not verified, and SynergyFinder carries a "Proprietary and confidential" doc header that
  conflicts with its MPL-2.0 licence;
- several repositories redistribute other authors' experimental data under a code licence,
  without a separate data licence;
- one package asks to be contacted before publication use (mixdra);
- committing outcome files to a public repository would also end the blind for everyone.

TACT's `input/` data is explicitly CC-BY-4.0 and could be redistributed with attribution. It is
left out for the last reason. The licence evidence for each repository is in `MANIFEST.json`.

## Rebuilding

1. `python acquire.py --dest <scratch>/raw` clones the 13 source repositories at their commits
   and verifies the source files.
2. To re-seal, run the scripts in `extraction/` after pointing their hard-coded
   `/tmp/claude-0/stage1/triples/` paths at the scratch location. Scripts under `extraction/` that
   begin `seal_edith`, `seal_mixtox` and `seal_ncats` expect to run from the stage root. The five
   verbatim copies need only a file copy.
3. `python verify_sealed.py --sealed <scratch>/sealed` compares the result with the manifest.
   CSVs written by pandas may differ byte-for-byte under another pandas version. If they do,
   record the difference rather than overwriting the manifest.

No test may be run on these files until a design, its calibration, its models, its splits and
its decision thresholds are frozen and committed first. Any such design must first deal with
items 1–6 above.
