# The Search (v0.10)

**Question:** what is the target state? Before the app can carry a mind to a point, the point has
to be found. The Search treats each idea of "clarity" as a hypothesis and lets your own clarity
decide between them.

## The seven candidate shapes

| Shape | Measured as (2 s, in your settle spread) |
|---|---|
| Side to side balance | how alike left and right alpha are, forehead and behind the ears |
| Front to back balance | how alike forehead and ear alpha are |
| Waves moving together | alpha-wave correlation averaged over all six sensor pairs |
| Calm | relative alpha |
| Absorption | forehead theta share |
| Focus | beta over alpha + theta |
| Openness | complexity (LZ) |

## One Search (about 12 minutes)

25 s of settle, then eight one-minute rounds in a sealed order. In six, the water answers one shape.
In two, nothing is steered (the scene drifts on its own). Rounds are chosen by Thompson sampling, so
shapes whose evidence is still uncertain get tested more. After each round, one tap: how clear is
your mind (Foggy, Dull, Ordinary, Clear, Crystal). Three times a round a faint light blinks in the
small dark circle below the centre: press Space. A staircase keeps the lights at your threshold,
so catching them measures how clearly you actually perceive. No carry during the Search (it would
confound). Every round records all seven shapes, whatever was being steered.

## What the report says (Home › Results › The Search)

* **Steered:** clarity and light-catching when steered towards a shape, compared with nothing steered.
* **Goes with clarity:** across all rounds, whether more of a shape went with clearer moments.
* **Sweet spot:** whether clarity peaks at a point along a shape rather than at an extreme. Once a
  shape shows a sweet spot, later Searches steer *to that point* instead of towards "more".
* **Held out:** with three or more Searches, each is predicted from the others.

**The point is called (provisionally) only if** one shape predicts both your clarity taps and your
light-catching on held-out Searches better than every other shape, and steering towards it beats
nothing steered with a 95% interval above zero. Checked by simulation: a planted sweet spot on one
shape was found at the right place; with no real relation, nothing was called.

## Why a sweet spot rather than "perfect"

Perfect symmetry or perfect correlation across the whole head is not what healthy alertness looks
like: widespread hypersynchrony is what seizures, deep sleep and anaesthesia look like. The
framework's own boundedness axiom says the same thing in its language: the boundary is never the
destination, and the attracting states are interior points. The Search looks for that interior point
instead of assuming it is at an extreme.
