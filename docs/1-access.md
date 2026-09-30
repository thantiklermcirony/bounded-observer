# Gate 1 · Access

**What can an observer reach, from inside the world it measures?**

This is the premise everything else is derived from, and it is the one thing the programme
does not try to prove. An observer is inside. It has finite channels, finite memory, finite
time. It cannot step outside and look.

That sounds like a limitation to apologise for. It is not. It is a constraint strong enough to
force the rest.

## The observer is at the centre, and this is not a special position

Every observer finds itself at the centre of its own space. Not because it is privileged, but
because "here" is where it measures from. Theorem 29 makes this exact: for any observer whose
composition law is a group, or a gyrogroup whose gyrations preserve rapidity magnitude,

1. it is at the centre of its own space;
2. different observers read different raw values for the same state;
3. all observers agree on rapidity distances, $d(x,y) = |\psi((\ominus x) \oplus y)|$;
4. it can measure its horizons but never reach them;
5. in two or more dimensions, carrying a viewpoint around a loop of observers returns it
   rotated by an angle equal to the enclosed area divided by $\ell^2$.

Items 1–3 hold in any homogeneous space, flat ones included; there is nothing exotic in them.
What boundedness adds is item 4: a horizon you can measure the distance to and never arrive at.
What non-associativity adds is item 5: perspective with memory.

Status: **[P]**.

## What this rules out

The observer cannot use a coordinate it has no access to. This sounds obvious and is violated
constantly. A quantity defined only from outside the system — a true underlying value, an
absolute rate, a variable nobody can intervene on — cannot appear in a law the observer is
supposed to use. When one does, the law has smuggled in a view from nowhere.

The discipline that follows: before any chart is fitted, state what the observer can reach.
`registry/atlas.csv` has a column for exactly this, and a category for work whose conditions
the law does not meet.

## The exception worth knowing

The one-horizon monoids of Theorem 2 — a neutral state sitting at the end of the interval
rather than inside it — have no inverses. An observer there cannot be recentred, so items 1–3
above do not apply to it. Only the horizon survives. Dose is like this: there is no negative
dose, and you cannot recentre the world on "the dose I have already had" and carry on
symmetrically.

## On the site

[**You are the centre**](https://thantiklermcirony.github.io/bounded-observer/#sim-centre) — drag anywhere in a hyperbolic tiling.
The world recentres on you and the edge stays exactly as far away as it was. Every tile is the
same size; the ones near the rim only look small from where you happen to be standing.

## Sources

- *Bounded Composition and Its Horizons* v2.1, Theorem 29 and §11.2 — `papers/capstone/`
- *The Observer and the World: Predictive Closure, the Projective Shadow, and a First-principles
  Grammar of Empirical Science* — [SSRN 7347861](https://papers.ssrn.com/abstract=7347861)
- `toolkit/bounded/disk.py` — `recentre`, `distance`; `toolkit/tests/test_theorems.py::test_observer_centrality`

**Next gate:** [State](2-state.md) — what must be kept so the rest of the past can be forgotten.
