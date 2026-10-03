# Errata to version 2.1

Version 2.1 (30 September 2026) is the built record: the PDF and the concatenated markdown
match the part files. The corrections below were found after it was built. They are listed
here, not edited into the part files, so that the record and the PDF still agree. Fold them into
version 2.2.

Each entry gives what v2.1 says, what is wrong, the corrected statement, and how it was checked.

---

## E1. §2.2, Proposition 1, Case I: non-closure does not by itself refute statehood

**v2.1 says.** "No single-valued $F$ exists. Equal values of $L$ support different futures, so
$L$ is not a state."

**What is wrong.** $F$ can fail in either argument.
- *First argument.* Two histories with $L(h_1)=L(h_1')$ lead to different summaries after the
  same continuation $h_2$. That is a matched-present failure, so $L$ is not a state
  (Theorem 10).
- *Second argument.* Two continuations with $L(h_2)=L(h_2')$ act differently from the same
  present $h_1$. That is a failure of the action gate. $L$ may still be a sufficient state. §5.1
  ("Statehood and composition are separate gates") and A.3 say exactly this, so v2.1
  contradicts itself here.

**Corrected statement.** "Case I (no closure). No single-valued $F$ exists. Either equal values
of $L$ support different futures under the same continuation, so $L$ is not a state; or two
continuations with equal summaries act differently from the same present, so the action gate
fails (§5.1) while $L$ may still be a state."

**Status.** The trichotomy keeps [P]. Its three cases are still exhaustive. Only the reading of
Case I changes.

**Checked.** By reading §2.2 against §5.1 and A.3. No computation needed.

## E2. §13.5, second refuter: it cannot be observed

**v2.1 says.** One observation that would refute the law is "a horizon is reached with every
condition intact".

**What is wrong.** C3 asks for strict monotonicity on the whole interval $I$. If $I$ contained a
finite end $\beta$, then $\beta\oplus a>\beta$ for every $a>e$, which is impossible inside $I$.
The same argument applies at the lower end. So the ends are excluded by the premises, and an
arrival already shows that C1 or C3 failed at the bound. That is Theorem 18 (A.9), whose
contrapositive is correct. As a refuter, the item can never fire.

**Corrected statement.** Replace the item with the testable form of Proposition 9:
"a quantity whose boundary exponents $\gamma$ (drift) and $\beta$ (noise) are estimated from
its approach *without using whether it arrives*, and which then either reaches its bound
although $\gamma\ge1$ and $\beta\ge1$, or fails to reach it although $\gamma<1$ and the drift
points toward the bound."

**Status.** Proposition 9 parts (a) and (b) are [P] (Osgood, Feller). The refuter tests whether a
real system's measured exponent predicts its arrival, which is an empirical claim.

**Checked.** By the two-line argument above. See also `registry/review-2026-10-03.md` §3.

## E3. §13.2: the Bliss chart cannot be separated from the flat scale on these data

**v2.1 says.** The data cannot separate the log risk ratio from the log odds ratio, because
they nearly coincide for rare events.

**Add.** For the same reason, $-\log(1-p)\approx p$, so the Bliss-chart difference nearly
coincides with the risk difference when risks are low. The table shows it: median $I^2$ is 0.50
for Bliss against 0.52 for the risk difference. In 16 of the 19 meta-analyses the highest
control risk is below 0.45, and only 3 reach above 0.5. The result therefore supports "log RR and
log OR are more portable than RD", which is the classical finding. It does not test a rapidity
chart *as such*.

Read in the paper's own terms, the log risk ratio is the rapidity of the one-horizon chart whose
horizon sits at $p=0$, the bound these trials lie next to. Whether the chart with the *nearest*
horizon is the most portable is a sharper question. It needs trials near $p=1$. See
`registry/review-2026-10-03.md`, test T2.

**Checked.** Rerun from `experiments/h2-effect-scales/h2_results.csv`. Spearman $\rho$ between
the highest baseline risk and the RD-minus-Bliss $I^2$ gap is 0.08 ($p=0.79$).
