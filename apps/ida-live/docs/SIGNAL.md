# Muscle, contact and eyes: how IDA Live tells them apart (v0.9.1)

## What went wrong

Danny's sessions of 26 September were held back as "muscle" 56–83% of the time while he sat
completely still. Replaying the recordings through the live code (tests/replay_quality.py) showed why:

* The biggest cause was a comparison with **yesterday's calibration**. The ear sensors' high
  frequencies (55–95 Hz) were about five times higher than when the reference was made, all
  session long, so the rule "ear high frequencies 3 SD above the reference" fired constantly.
* That rise was **contact, not jaw**. At the ear sensors the high frequencies moved with the
  50 Hz mains hum (r ≈ 0.6–0.66; at the forehead r ≈ 0.06), and both stepped up together after a
  head movement about two minutes in. A loosening dry electrode picks up more hum and more noise
  at the same time. A jaw muscle adds high frequencies and leaves the hum where it was.
* Many of the remaining forehead bursts came with blinks and eye movements (r ≈ 0.43 and 0.29).
  Those are the eyes, not tension in the face.
* The "spiky" test was always on, because the hum's skirts leaked into it and a fixed threshold
  (kurtosis 5) sat below the forehead's usual value (about 10).

## The rules now

Per sensor, every quarter second, over a 2 s window, each against that sensor's own last minute:

| Label | When |
|---|---|
| **loose** | high frequencies burst above their usual level AND a clear hum is present AND the hum rose by at least 60% as much (in log units): contact |
| **eyes** | a forehead burst that came with a rise in 1–4 Hz power (blinks, eye movements) |
| **muscle** | a burst that is neither of those, and spiky above that sensor's own usual spikiness, or local to that sensor |
| noise / poor / flat / interference / good | as before |

Sustained tension (which the one-minute comparison would absorb) is checked against **this
session's own first minute**, not another day's calibration, and only when the ear hum has not
risen with it. The kurtosis band now removes 4 Hz either side of the hum and its harmonic.

## Checked on the real recordings

| Session | Clean before | Clean after |
|---|---|---|
| booth 07:08 | 37% | 79% |
| booth 07:14 | 16% | 90% |
| Bloom 07:18 | 36% | 79% |

To check that real muscle still gets caught, realistic bursts (20–120 Hz, spiky motor-unit
envelopes, about ten times the usual high-frequency power) were added to the booth recording at
known moments:

| Burst | Caught (once inside the 2 s window) | Flagged when no burst |
|---|---|---|
| jaw (both ear sensors) | 94% | 3% |
| brow (both forehead sensors) | 87% | 3% |
| before the fix (either) | 88% | **54%** |

The old rule caught bursts only because it flagged half of everything.

## What still holds a session back, and what helps

About 10–20% of the time one ear sensor loses contact ("loose" or "not reading"); Home and the
level hints now name the sensor. The hum at the ear sensors is about a hundred times the level of
the frequencies around it, so running the laptop on battery (charger unplugged) should reduce it a
lot. Wetting the ear sensors and keeping hair out from under them helps too.
