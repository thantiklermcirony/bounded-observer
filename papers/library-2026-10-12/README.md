# The Bounded Observer: UHL and SIH

Daniel John Murray · ORCID [0009-0005-1794-5945](https://orcid.org/0009-0005-1794-5945) · Revised working library, 12 October 2026.

UHL is an operational geometry of bounded normalized records and their lawful composition. Its stated cone and reading–generator premises select complex records; the elementary binary record has hyperbolic projective geometry. The capstone proves an explicit operational closure theorem. Physical applications have their additional models and bridges stated, and historical tests retain their original outcomes.

## Read the library

| Manuscript | PDF | Editable source |
|---|---|---|
| The Bounded Observer | [Capstone](pdf/capstone.pdf) | [Source](papers/capstone.md) |
| 1. The Geometry of Bounded Records | [Paper 1](pdf/paper1.pdf) | [Source](papers/paper1.md) |
| 2. One Motion on the Line | [Paper 2](pdf/paper2.pdf) | [Source](papers/paper2.md) |
| 3. Light Time and Horizons | [Paper 3](pdf/paper3.pdf) | [Source](papers/paper3.md) |
| 4. Two Observers | [Paper 4](pdf/paper4.pdf) | [Source](papers/paper4.md) |
| 5. Where Singularities Can Live | [Paper 5](pdf/paper5.pdf) | [Source](papers/paper5.md) |
| 6. The Partner Freedom | [Paper 6](pdf/paper6.pdf) | [Source](papers/paper6.md) |
| 7. Gravity as Equilibrium | [Paper 7](pdf/paper7.pdf) | [Source](papers/paper7.md) |
| 8. The Ceiling and the Constants | [Paper 8](pdf/paper8.pdf) | [Source](papers/paper8.md) |

## Hormesis and corrections

[Exact Onset and Peak Laws for Bounded Adaptive Responses](pdf/hormesis_amendment.pdf) supplies model-specific replacement theorems for the published linear-dose rapidity model and two distinct later Hill models, with finite metabolic-control corrections. Its [source](papers/hormesis_amendment.md) and checks are included.

The [proposed hormesis corrigendum](pdf/hormesis_corrigendum.pdf) identifies corrections to the published article, [doi:10.1177/15593258261469171](https://doi.org/10.1177/15593258261469171). It is an author proposal, not an issued journal correction. The [proposed deformed-kinematics notice](pdf/deformed_kinematics_correction.pdf) corrects the earlier uniqueness and operator claims; the current live SSRN revision was not verified during preparation. No public Dirac correction is included because the author states that manuscript was never published or posted.

## Reproduce the mathematical checks

Use Python 3.11 or later. Install `requirements.txt`, then run `python run_checks.py`. The thirteen independent modules check algebraic identities, finite-matrix constructions, exact model peak and detection laws, the locally covariant complete-positivity rate cone and explicit counterexamples. General claims rest on the proofs and cited theorems. Passing these checks is not empirical validation or peer review.

`provenance/` preserves the available T15, T15b and T20 protocol/output records. They are historical analyses, not newly replicated empirical experiments. In particular the registered T20 BAO-plus-supernova result was neutral; the later CMB extension is separately labelled exploratory. Those records support the reported history and do not make the full empirical pipeline independently reproduced here.

## Build the papers

Editable Markdown and standalone LaTeX are included. Prebuilt PDFs use XeLaTeX with Cambria and Cambria Math. The portable builder requires Pandoc (bundled by `pypandoc_binary`) and XeLaTeX; optional PNG inspection uses Poppler. `python build_publication.py --only capstone` builds one manuscript. Supply `--xelatex`, `--mainfont` and `--mathfont` when using different installed tools or fonts; changing fonts can change pagination. The standalone `.tex` files can also be compiled directly with their declared fonts.

Metadata supplies titles, abstracts, keywords, author identity and exact source/PDF hashes. `verification/` records the final build, mathematical checks, visual page coverage and DOI identity checks. A hash manifest identifies this release snapshot.

These are revised working preprints for author review and submission. The original manuscripts and earlier versions remain historical records. The library does not claim that boundedness alone uniquely derives all actual particle content, dynamics or constants. AI-assisted preparation is disclosed; responsibility for the final claims and submission rests with the author. No new reuse licence is granted by this package.
