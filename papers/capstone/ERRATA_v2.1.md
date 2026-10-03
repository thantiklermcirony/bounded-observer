# Errata to version 2.1

Version 2.1 (30 September 2026) is the built record: the PDF and the concatenated Markdown
match the part files. The entries below were found after it was built. They are listed here,
not edited into the part files, so that the archived record and its PDF still agree.

**Version status.** The author reports a locally reviewed v2.7, which has not been recovered
into this repository. These errata are against v2.1. They must be reconciled with v2.7 before
any of them is folded into a manuscript. No intermediate version is implied.

Each entry gives what v2.1 says, what is wrong, the corrected statement, and how it was checked.
Entries E1–E3 were first written on 3 October 2026 (commit `df48ae4`) and revised the same day
after review. The revisions are noted in each entry.

**Four things that this paper, and these errata, keep apart:**
1. *boundedness* of a quantity;
2. *lawful composition*, meaning C1–C4, which gives an additive rapidity (Aczél) but no
   particular chart and no curvature;
3. the *additional projective assumptions* (a linear two-channel world read through a ratio,
   Theorem 6) that select Einstein/logit or the Hamacher dial;
4. *empirical model identification*: which chart a real system uses, decided by data.

Agreement of data with an established result at level 4 is not evidence for anything at
level 3.

---

## E1. §2.2, Proposition 1, Case I: non-closure does not by itself show state insufficiency

**v2.1 says.** "No single-valued $F$ exists. Equal values of $L$ support different futures, so
$L$ is not a state."

**What is wrong.** A two-argument composition $L(h_1;h_2)=F(L(h_1),L(h_2))$ can fail in either
argument, and the two failures mean different things.
- *State insufficiency (first argument).* Two histories with $L(h_1)=L(h_1')$ lead to different
  values after the same continuation $h_2$. Then $L$ does not determine its own future: it is
  not a sufficient state (Theorem 10).
- *Action-summary insufficiency (second argument).* Two continuations with $L(h_2)=L(h_2')$ act
  differently from the same present. Then the summary of the *intervention* is too coarse: the
  action gate fails. $L$ may still be a sufficient state. §5.1 ("Statehood and composition are
  separate gates") and A.3 say exactly this, so v2.1 contradicts itself here.

**Corrected statement.** "Case I (no closure). No single-valued $F$ exists. Either equal values
of $L$ support different futures under the same continuation, so $L$ is not a state; or two
continuations with equal summaries act differently from the same present, so the action gate
fails (§5.1) while $L$ may still be a state. Failure of $F$ does not by itself show which."

**A minimal example of each.** Both are tested in `toolkit/tests/test_falsifiable.py`.
- *State sufficient, action gate fails.* The state is $x$. Interventions $T_b(x)=x+1$ and
  $T_c(x)=2x+1$ have the same endpoint from rest ($T_b(0)=T_c(0)=1$), but from $x=1$ they give
  2 and 3. The future depends only on $x$ and the intervention, so $x$ is a sufficient state.
  No single-valued $F$ on endpoint summaries exists, since $F(1,1)$ would have to be both 2
  and 3.
- *State insufficient.* The world carries $(x,h)$ and $L$ reads only $x$. Under $x' = x + h\,b$,
  two histories with $x=1$ but $h=0$ and $h=1$ go to 1 and 2 under the same continuation
  $b=1$.

**Status.** The trichotomy keeps [P]; its three cases are still exhaustive. Only the reading of
Case I changes.

**Checked.** By reading §2.2 against §5.1 and A.3, and by the two examples above, which are
run as tests. *Revised 3 October:* the example and the final sentence were added.

## E2. §13.5, second refuter: it cannot be observed, and the boundary results need their assumptions

**v2.1 says.** One observation that would refute the law is "a horizon is reached with every
condition intact".

**What is wrong.** C3 asks for strict monotonicity on the whole interval $I$, and C4 supplies
a neutral state $e$. Let $\beta$ be a finite end of $I$ with $\beta\neq e$, say $\beta=\sup I>e$.
If $\beta$ belonged to $I$, then for $e<a<\beta$ strict monotonicity would give
$\beta\oplus a>\beta\oplus e=\beta$, which is impossible inside $I$. The mirror argument covers
a lower end below $e$. **So every finite end other than the neutral state is excluded from $I$
by the premises.** An end equal to $e$, as in the monoid case of Theorem 2, may belong to $I$.

The horizons are therefore never in the domain, and an observed arrival at one already shows
that a premise failed (Theorem 18, A.9, whose contrapositive is correct). As a refuter, the
item can never fire.

*Revised 3 October.* The first version of this entry said "the ends", without the exception
for an end equal to $e$. It also proposed a replacement refuter: "reaches its bound although
$\gamma\ge1$ and $\beta\ge1$, or fails to reach it although $\gamma<1$". **That replacement is
withdrawn.** Not reaching a bound within a finite observation does not establish that it is
never reached. And the stochastic result concerns attainability, not almost-sure arrival.

**What the boundary results actually say, with their assumptions.**
- **Deterministic arrival (Proposition 9a; Osgood).** For an autonomous, noise-free motion
  $\dot e=X(e)$ with $X$ continuous and positive on the approach and $X(e)\sim k(1-e)^\gamma$
  near the bound, the bound is reached in finite time if and only if $\gamma<1$. Then the
  arrival time from gap $\delta_0$ is $\delta_0^{1-\gamma}/(k(1-\gamma))$.
- **Stochastic first passage (Proposition 9b; Feller).** For a one-dimensional time-homogeneous
  diffusion $de=X\,dt+\sigma\,dW$, regular in the interior, with power-law drift and noise at the
  boundary, Feller's classification says whether the boundary is *attainable*: reached in
  finite time with positive probability. It does not say the boundary is reached almost surely,
  or when. First-passage times are a separate calculation.

**What a test of either would need.** Declare all of these in advance:
- the observation horizon $T_{\rm obs}$;
- the measurement resolution, meaning the smallest gap from the bound that can be told from
  zero;
- the calibration uncertainty of the estimated exponents and rate constants;
- the predicted arrival time (deterministic), or the predicted first-passage probability by
  $T_{\rm obs}$ (stochastic).

Without these, a proposed test is **incomplete**, not a validation. **No replacement refuter is
adopted in this erratum.**

**Status.** Proposition 9(a) and (b) are [P] as classical results under the assumptions above.
Whether a real system meets those assumptions is an empirical question with no test specified
here.

**Checked.** By the argument above. The deterministic statement is also checked numerically by
integration in `toolkit/tests/test_falsifiable.py`, under its own assumptions.

## E3. §13.2: the Bliss chart cannot be separated from the flat scale on these data

**v2.1 says.** The data cannot separate the log risk ratio from the log odds ratio, because
they nearly coincide for rare events.

**Add.** For the same reason, $-\log(1-p)\approx p$ when risks are low, so the Bliss-chart
difference nearly coincides with the risk difference.
- The table shows it: median $I^2$ is 0.50 for Bliss against 0.52 for the risk difference.
- In 16 of the 19 meta-analyses the highest control risk is below 0.45, and only 3 reach above
  0.5.

The observed comparison is kept as reported. What it supports is "log RR and log OR are more
portable than RD in these 19 meta-analyses", which repeats an established effect-scale finding.
**It does not test a rapidity chart as such, and agreement with that finding is not evidence for
a uniquely hyperbolic mechanism** (see the four distinctions above).

A sharper question, *not adopted and not tested*: is the one-horizon chart whose horizon lies
nearest the trials' baseline risk the most portable? Any test of it would need trials spanning
high baseline risk, and its power would have to be computed for the chosen design, not assumed
from being near the bound. See `registry/review-2026-10-03.md`, T2, which is parked.

**Checked.** Rerun from `experiments/h2-effect-scales/h2_results.csv`. Spearman $\rho$ between
the highest baseline risk and the RD-minus-Bliss $I^2$ gap is 0.08 ($p=0.79$, 14 meta-analyses).
*Revised 3 October:* the scope sentence was added and the "nearest horizon" question was marked
as not adopted.

## E4. §7.4 and A.19: "the principal branch" needs its convention

**v2.1 says.** For $|x|>1$, $\operatorname{artanh}x=\operatorname{artanh}(1/x)+i\pi/2$,
"taking the principal branch".

**What needs stating.** That representative is $\tfrac12\operatorname{Log}\frac{1+x}{1-x}$, with the
principal logarithm of the *ratio*. The other common reading,
$\tfrac12[\operatorname{Log}(1+x)-\operatorname{Log}(1-x)]$, gives $-i\pi/2$ for $x>1$. With the
stated representative:
- additivity is exact for composition with an inside change, which is the case Theorem 19
  states, including compositions through infinity such as $(-3)\oplus0.5=5$;
- two outside states always compose to an inside state, and there additivity holds only modulo
  $i\pi$: $2\oplus2=4/5$ and $r(2)+r(2)-r(4/5)=i\pi$;
- $\tanh$ recovers the value exactly in every case.

**Status.** A clarification, not a change to Theorem 19. **Checked** in
`toolkit/tests/test_theorems.py` and `site/bo.test.mjs` against an independent oracle.

## E5. Declarations: the verification scripts are not supplied

**v2.1 says.** "Analysis code, the H1 pre-registration and all verification scripts are
provided as supplementary material" (05_appendix.md, Data and code availability). Appendix B
says the checks "were run in Python (NumPy, SciPy, SymPy)".

**What is wrong.** No supplement exists in this repository, and none was found in any branch,
archive or Drive location searched. Only the H1 and H2 analysis code is present. The status of
every Appendix B row is recorded in `papers/capstone/APPENDIX_B_MANIFEST.md`.

**Corrected statement.** "Analysis code for H1 and H2 and the H1 pre-registration are in the
repository. The scripts behind the other Appendix B checks are not available; see the
Appendix B manifest for which checks have been reproduced or reconstructed and which are
missing."

**Status.** A documentation correction; the historical release is kept unchanged.
