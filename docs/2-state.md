# Gate 2 · State

**What must be kept, so that the rest of the past can be forgotten safely?**

An observer with finite memory has to throw almost everything away. The question is what it is
allowed to throw away. A *state* is the answer: a summary of the past that is sufficient for
the future.

## The definition that does the work

A proposed state $x$ is a state if and only if the conditional distribution of futures is the
same, under **every admissible intervention**, for all histories that $x$ identifies
(Theorem 10). The phrase "under every admissible intervention" is the whole content. A summary
that predicts the future when you leave the system alone, but not when you push it, is a
description, not a state.

This is the classical construction of causal and predictive states — Nerode 1958, Crutchfield
and Young 1989, Shalizi and Crutchfield 2001, Littman, Sutton and Singh 2002. Status: **[P]**.
What the programme adds is its application to biological state and to experimental action.

## The failure this is built to catch

**A measurement merges histories that have different futures.**

A biomarker merges the histories that produced it. A calm-looking reading merges a system that
has recovered, one held steady by support, and one whose reserve is spent. Once that
distinction is erased, fitting the same measurement harder cannot bring it back: if two
histories give the same reading but different futures, any predictor fed only that reading gets
the same input for both.

There are exactly three ways forward, and no fourth: get more information, narrow the claim, or
predict the mixture honestly.

## What a persistent residual tells us

A residual alone does not choose between missing state, a wrong transition rule, measurement
error, and a changing experimental setting. Freeze the proposed state $(x,Z)$, the admitted
interventions, the future outcome and window, the matching tolerance, and a meaningful
discrepancy before testing new data. Prepare different histories that match on $(x,Z)$, give
them the same intervention, and compare their **future distributions**, not only their means.
Repeated preparations and technical controls measure the noise floor; untouched histories
and batches test whether a separation travels.

If history still predicts the future beyond those errors, $(x,Z)$ fails the state test for
that intervention and operating range. Another candidate variable earns support only if it
predicts and removes the separation on held-out histories and challenges. If matched histories
have equivalent futures within a predeclared bound but a proposed equation still makes
reproducibly wrong predictions, test the equation, action encoding, and chart. Both failures
can occur together. Failure to detect a difference is not evidence of equivalence without a
precise confidence bound, and a finite challenge panel cannot certify every possible future.
The criterion is [P] (Theorem 10); which explanation fits a real residual remains an empirical
question.

## The closure trichotomy

Suppose a scalar summary $L$ of a history is proposed as a state, and that sequential histories
combine, $L(h_1; h_2) = F(L(h_1), L(h_2))$. Then exactly one of three cases holds
(Proposition 1):

- **Case I — no closure.** No single-valued $F$ exists. Equal values of $L$ support different
  futures. $L$ is not a state.
- **Case II — lawful closure outside the regular class.** $F$ exists and is associative, but
  continuity, strict monotonicity, the neutral state or cancellativity fails. Idempotent,
  absorbing, max-like and min-like laws live here. They erase distinctions irreversibly while
  remaining lawful.
- **Case III — regular closure.** $F$ satisfies C1–C4, and the law of gate 4 applies.

Associativity comes for free, because concatenating histories is associative. Status: **[P]**.

The capstone is the theory of Case III. Every arrival at a boundary is located in Case I or II,
in an unbounded drive, or in a change of law (Theorem 18) — which is what makes gate 4's
horizon claim falsifiable rather than decorative.

## Where this is being tested

IDA Live is this gate pointed at a mind. Its bet: **how you come back** after being displaced —
latency, overshoot, the residue left behind — carries information about your future capacity
that **where you are** does not. A calm reading merges the recovered, the supported and the
spent; a recovery trajectory might not.

That bet is not yet settled. The instrument has the read-side apparatus and does not yet have
the three things the test needs: a common perturbation, a matched starting state, and an
outcome the controller does not itself produce. See `apps/ida-live/docs/IDA_EVOLUTION.md`.

## On the site

[**Two histories, one reading**](https://thantiklermcirony.github.io/bounded-observer/#sim-histories) — watch two paths arrive at the
same number and then part. Add the one extra measurement that tells them apart.

## Sources

- Capstone v2.1, Theorem 10 and Proposition 1 — `papers/capstone/`
- *A Law of Biological State Sufficiency* — [SSRN 7425878](https://papers.ssrn.com/abstract=7425878)
- *Predictive Closure: State, action, and the experimental compression of history* — [SSRN 7427098](https://papers.ssrn.com/abstract=7427098)
- *The Temporal Architecture of Living Nature* — [SSRN 7426938](https://papers.ssrn.com/abstract=7426938)

**Next gate:** [Action](3-action.md) — which interventions act the same way from every state.
