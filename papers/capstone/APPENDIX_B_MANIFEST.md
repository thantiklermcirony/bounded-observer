# Appendix B reproduction manifest (capstone v2.1)

Appendix B (`05_appendix.md`, lines 73–120) has **46 rows**. Forty-five report a computation;
one (§13.2 data, line 103) points to the H2 analysis. The capstone says the checks "were run in
Python (NumPy, SciPy, SymPy)" and that "all verification scripts are provided as supplementary
material". No such supplement exists in this repository or anywhere searched (ERRATA E5).

**Statuses.**
- **reproduced**: the *original* script was rerun in this repair pass (3 October 2026) and its
  outputs matched the committed results byte for byte.
- **existing-but-not-rerun**: an original script exists but was not rerun. No row has this
  status.
- **newly reconstructed**: an *independent* check in `toolkit/tests/` covers the claim. It is
  **not the original script**. "Partial" means it checks the same law at other values, or only
  part of the row. The commit that added the test is given: `9470945` is the repository's first
  commit (1 October 2026); `28ab37d` and `3bcaa9e` were added on 3 October 2026.
- **missing-source**: no script and no independent check in the repository.

Toolkit tests pass in this pass (`python -m pytest toolkit/tests -q`). Passing confirms that the
reconstruction holds; it does not recover the original.

| # | Line | Claim (as printed) | Reported result | Script or check | Input | Status |
|---|---|---|---|---|---|---|
| 1 | 75 | §2.4 non-Einstein admissible law | tangent law 0.628 vs Einstein 0.696 | none | — | missing-source |
| 2 | 76 | §3.1 negentropy slope | artanh m | none | — | missing-source |
| 3 | 77 | §3.1 Fisher length, two states | π | none | — | missing-source |
| 4 | 78 | §3.2 error table | 0.3%, 9.9%, 63.6%, 167.3% | none | — | missing-source |
| 5 | 79 | Theorem 4 generator | 1−κu²; 2⊕2=−4/3 at κ=−1 | `test_theorems.py::test_trichotomy` (9470945) | — | newly reconstructed (partial: 2⊕2 = −4/3 only; generator not checked) |
| 6 | 80 | Theorem 7 | X ∝ e(1−e) | none | — | missing-source |
| 7 | 81 | Theorem 8 drastic limit | 0.294, 0.400, 0.966 | none | — | missing-source |
| 8 | 82 | §5.2 gyration = area of (0,a,a⊕b) | 0.48996, 0.60035, 0.34012 (pairs) | `test_theorems.py::test_gyration_equals_triangle_area` (9470945); `test_falsifiable.py::test_gyration_angle_equals_area_on_random_pairs` (28ab37d); `site/bo.test.mjs` (0.600) | — | newly reconstructed (partial: random pairs; the three printed values are not asserted, except 0.600 in the browser test) |
| 9 | 83 | Theorem 16 locks | sinh lock 1.048; sin slip period 4.18880 | `test_theorems.py::test_locking` (9470945) | — | newly reconstructed (partial: locks checked at Φ = 1.2, not 2.5; slip period not checked) |
| 10 | 84 | Theorem 16 tanh unlock | asymptotic speeds 9.0 and 6.0 | none | — | missing-source |
| 11 | 85 | Theorem 15 without rate symmetry | net flux formula | none | — | missing-source |
| 12 | 86 | Proposition 2 | J = θ tanh θ − ln cosh θ; limit ln 2 | none | — | missing-source |
| 13 | 87 | Proposition 4 | lawful-mean bias 0.00205 vs 0.00200 | none | — | missing-source |
| 14 | 88 | Proposition 5 | Riccati form | none | — | missing-source |
| 15 | 89 | Proposition 6 | order defect (q−1)[b(a)−b(b)] | none | — | missing-source |
| 16 | 90 | Theorem 8 landmarks | α = −1 gives Einstein; Tsallis rescaling | `test_theorems.py::test_dial_landmarks` (9470945) | — | newly reconstructed (partial: Einstein landmark only) |
| 17 | 91 | Theorem 17 | ℓ² = 1.000000 at a=0.1, b=0.2 | `test_falsifiable.py::test_einstein_ceiling_recovers_the_ceiling` (28ab37d) | — | newly reconstructed (same identity, random a, b) |
| 18 | 92 | Theorem 22 | 10⁶ paths, none reached 0 or 1 | none | — | missing-source |
| 19 | 93 | Theorem 23 | P_fix 0.0097; T₁ 199.9 | none | — | missing-source |
| 20 | 94 | Theorem 23 beneficial allele | approximation high by 1.0–2.0 generations | none | — | missing-source |
| 21 | 95 | Theorem 23(a) | both ends exit boundaries | none | — | missing-source |
| 22 | 96 | Theorem 27 | so(1,3) brackets | none | — | missing-source |
| 23 | 97 | Theorem 25 item 1 | agreement to 10⁻¹⁰ | none | — | missing-source |
| 24 | 98 | Theorem 26 | Frobenius norm 0.069 | none | — | missing-source |
| 25 | 99 | §9.2 mirror | 1−R = 1.09×10⁻¹⁰ | none | — | missing-source |
| 26 | 100 | §10.2 Bliss–Loewe | peak e* = 0.618, g = 0.0902 | `test_falsifiable.py::test_dial_gap_identity_and_that_the_gap_vanishes_at_both_ends` (3bcaa9e) | — | newly reconstructed |
| 27 | 101 | §11.1 Bayes | λ = tanh(½ log LR) | none | — | missing-source |
| 28 | 102 | §12 non-collapsibility | pooled 2.085 | none | — | missing-source |
| 29 | 103 | §13.2 data | see §13.2 | `experiments/h2-effect-scales/h2test.py` (original) | metadat, `github.com/wviechtb/metadat` @ `0cb96ce4ff16586a9dbc8a9b0f9bc617538d2738` | **reproduced**: `python h2test.py` regenerated `h2_results.csv` byte-identical |
| 30 | 104 | Proposition 3 exponents | Var/(1−m)² → 1/(a+1); two-point Var/(1−m) → 2 | `test_falsifiable.py::test_prop3_boundary_exponent_by_quadrature`, `::test_prop3_two_states_give_exponent_one` (28ab37d) | — | newly reconstructed (partial: exponents checked; the printed ratios and normalisation are not) |
| 31 | 105 | Proposition 9a (Osgood) | arrival at T = 1, 2, 10 for γ = 0, 0.5, 0.9; none for γ ≥ 1 | `test_falsifiable.py::test_prop9_*` (28ab37d); `test_theorems.py::test_osgood` (9470945, smoke) | — | newly reconstructed (same law by integration, from gap 0.3; the smoke test asserts T = 2 at γ = 0.5) |
| 32 | 106 | Proposition 9b (Feller) | Wright–Fisher boundary 100% / 0% | none | — | missing-source |
| 33 | 107 | Ceiling exponents of the charts | logit 1, Bliss 1, dial 1, Loewe 2, zero-order 0 | none | — | missing-source |
| 34 | 108 | Theorem 19, simultaneity | 1.4375; 2.6000 | `test_theorems.py::test_far_side` (9470945) | — | newly reconstructed (partial: 1.4375 only) |
| 35 | 109 | Proposition 3 continuum | 1.6747, 1.5000, 1.3333, 1.2000 for a = −0.5, 0, 1, 3 | `test_falsifiable.py::test_prop3_boundary_exponent_by_quadrature` (28ab37d) | — | newly reconstructed (partial: a = −0.5, 0, 1 with atom mass 1 and θ = 10⁵, 2·10⁵; a = 3 not checked) |
| 36 | 110 | Proposition 3, no upper bound | 2.9555, 2.9859; Var/δ³ → 0.5 | `test_falsifiable.py::test_prop3_density_vanishing_faster_than_any_power_gives_exponent_three` (28ab37d) | — | newly reconstructed (at θ = 10⁴, 2·10⁴) |
| 37 | 111 | Theorem 16, beyond the tanh threshold | drift 0.1, 0.2, 0.4 = abs(Φ) − 2β | `test_theorems.py::test_locking` (9470945) | — | newly reconstructed (partial: same law at Φ = 3) |
| 38 | 112 | Proposition 3 corollary | bound holds, tight at start | none | — | missing-source |
| 39 | 113 | Proposition 6 bracket | εη(fg′ − gf′) | `test_theorems.py::test_bracket_predicts_order_effect` (9470945) | — | newly reconstructed |
| 40 | 114 | Theorem 25 item 4 | max contraction 0.3333 = tanh(ln4/4); AB − BA ≠ 0 | `test_theorems.py::test_forward_only_channels_contract_by_birkhoff`, `::test_forward_only_need_not_commute` (9470945, smoke) | — | newly reconstructed (partial: the bound holds on random matrices; tightness 0.3333 is not checked) |
| 41 | 115 | Theorem 25, Bures | π/4 | none | — | missing-source |
| 42 | 116 | Theorem 16 tanh near threshold | gaps 0.549, 1.472, 2.647; rates 1.500, 0.380, 0.040 | `test_theorems.py::test_locking` (9470945) | — | newly reconstructed (partial: the rate formula at Φ = 1.2; the printed values are not checked) |
| 43 | 117 | Theorem 19 across the horizon | 1.25; −1.2353; −2.1818; 1.0986 + 1.5708i | `test_theorems.py::test_far_side` (9470945), far-side parity tests (f041719) | — | newly reconstructed (partial: −2.1818 not asserted) |
| 44 | 118 | Theorem 25 items 1–2 | commutators 0; 0.504 | none | — | missing-source |
| 45 | 119 | §8.4 room | sinh r / r = 1.18, 15, 1100 | `test_theorems.py::test_room_inside` (9470945, smoke) | — | newly reconstructed (smoke: checks 2π sinh r against printed values) |
| 46 | 120 | §13.3 H1 | ρ = −0.12, p = 0.76 | `experiments/h1-decrease/h1_dial.py` (original) | DECREASE, `github.com/IanevskiAleksandr/DECREASE` @ `0f5871cad64fb8c43a88242e02baac175ed98d0e` | **reproduced**: `python h1_dial.py` regenerated `h1_results.json`, `h1_blocks.csv`, `h1_pairs.csv` byte-identical |

**Totals:**

| Status | Rows | Which |
| --- | --- | --- |
| reproduced | 2 | 29, 46 |
| existing-but-not-rerun | 0 | — |
| newly reconstructed | 17 | 5 full or nearly so (17, 26, 31, 36, 39); 12 partial (5, 8, 9, 16, 30, 34, 35, 37, 40, 42, 43, 45) |
| missing-source | 27 | 1–4, 6, 7, 10–15, 18–25, 27, 28, 32, 33, 38, 41, 44 |

**What this means.** Twenty-seven reported computations have no surviving script and no
independent check here. They are not shown to be wrong; they are unverifiable from this
repository until their original scripts are recovered or the checks are rebuilt. Rebuilding
them is outside this repair pass.

**How the reproduced rows were run (3 October 2026).** For each, the original script was copied
unchanged into a scratch directory beside the public input data and run with `python`. Its
outputs were then compared with the committed files using `cmp`.
