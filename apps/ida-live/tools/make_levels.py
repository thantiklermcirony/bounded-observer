"""Writes levels/levels.json. The ladders are generated here so every level's nine tiers
follow the same rule and can be changed in one place.

Design rule: each scene is chosen so that what you watch invites the state it measures, and
the image answers in the same language (calm stills water, warmth opens a flower, focus
steadies a walker, flow carries a surfer, recovery calms a storm, openness widens a sky).
entrain_hz is the rhythm of the level's optional pulsing tone: alpha 10 Hz for calm, theta 6 Hz
for flow, beta 18 Hz for focus, 40 Hz (the strongest auditory steady-state response) for open
awareness; 0 = none. It is tested, not assumed: rounds get the rhythm or irregular pulses, sealed.
Every tier is measured from your own baseline in that scene (the settle phase), in units of
your frozen reference, so a scene that shifts your EEG (watching video lowers alpha) can't
make a level impossible, and a day-to-day comparison is still in the same units.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PX = "https://cdn.pixabay.com/video/"
LICENCE = "Pixabay Content License: free to use and modify, no attribution required"


def lerp(a, b, k, n=9):
    return a + (b - a) * k / (n - 1)


def ladder(names, depth=(0.3, 2.6), tau=(0.5, 0.25), novelty=(0.15, 0.7), perturb=(0.3, 1.0),
           every=(30.0, 14.0), first_perturb=0.0):
    out = []
    for k, name in enumerate(names):
        out.append({
            "name": name,
            "depth": round(lerp(*depth, k), 3),
            "tau": round(lerp(*tau, k), 3),
            "novelty": round(lerp(*novelty, k), 3),
            "perturb": round(first_perturb if k == 0 else lerp(*perturb, k - 1, 8), 3),
            "perturb_every_s": round(lerp(*every, k), 1),
        })
    return out


LEVELS = [
    {
        "entrain_hz": 10,
        "id": "still", "number": 1, "title": "Still Water", "subtitle": "Let the water go still",
        "tests": "Calm, restful alertness",
        "instruction": "Soft eyes on the water. Nothing to do, nowhere to go. As you settle, the wind drops and the mist lifts.",
        "index": "relative_alpha", "target": "ix_alpha_rel3", "mode": "water", "video": "loop",
        "perturbation": "drop",
        "basis": [
            "Alpha rhythm (8-13 Hz) grows with relaxed, wakeful calm and shrinks with effort and arousal; relative alpha is the classic calm-training signal (Klimesch 1999; Hardt & Kamiya 1978).",
            "Busy, changing images suppress alpha, so this scene barely moves: a still lake whose only motion is the one you cause.",
            "Measured against your own baseline in this scene, not against your calibration, because watching anything lowers alpha.",
        ],
        "clip": {"file": "still.mp4", "credit": "Mist over a lake at sunrise, Pixabay (" + LICENCE + ")",
                 "page": "https://pixabay.com/videos/lake-steam-sunrise-water-forest-297745/",
                 "urls": [PX + "2025/08/16/297745_large.mp4", PX + "2022/08/15/127992-739777105_medium.mp4",
                          PX + "2022/08/15/127995-739777119_medium.mp4"]},
        "tiers": ladder(["Ripples", "Slowing", "Glassy", "Mirror", "Clear", "Deep", "Silent", "Still", "Monk"],
                        depth=(0.3, 2.4), perturb=(0.25, 0.9), every=(32, 16)),
    },
    {
        "entrain_hz": 0,
        "id": "bloom", "number": 2, "title": "Bloom", "subtitle": "Welcome it open",
        "tests": "Warmth: approach and positive feeling",
        "instruction": "Watch it open and feel glad for it, the way you'd welcome someone you love through the door. Lean toward it with warmth, not effort.",
        "index": "frontal_asymmetry", "target": "ix_faa", "mode": "bloom", "video": "scrub",
        "perturbation": "chill",
        "basis": [
            "Frontal alpha asymmetry: more alpha over the right forehead than the left means relatively more left-frontal activity, the best-known EEG sign of approach motivation and positive feeling (Davidson 1992; Harmon-Jones & Gable 2018).",
            "People can shift it with feedback, and doing so changes how they respond to emotional films (Allen, Harmon-Jones & Cavender 2001).",
            "A blossom is an approach scene: it invites warmth and anticipation, not blankness, so the flower opens with the feeling it evokes. The effect is modest and debated, which is exactly what the replay round tests.",
        ],
        "clip": {"file": "bloom.mp4", "credit": "Hibiscus bloom time-lapse, Pixabay (" + LICENCE + ")",
                 "page": "https://pixabay.com/videos/hibiscus-bloom-to-flourish-blossom-27202/",
                 "urls": [PX + "2019/09/24/27202-362518528_large.mp4", PX + "2018/07/01/17005-277920542_large.mp4",
                          PX + "2018/08/20/17869-286460813_large.mp4"]},
        "tiers": ladder(["Bud", "Warming", "Stirring", "Opening", "Unfolding", "Radiant", "Blossom", "Full bloom", "Monk"],
                        depth=(0.3, 2.4), perturb=(0.25, 0.9), every=(30, 16)),
    },
    {
        "entrain_hz": 18,
        "id": "steady", "number": 3, "title": "Tightrope", "subtitle": "Hold the line",
        "tests": "Focused, steady attention",
        "instruction": "Put all of your attention on the walker's feet and the line. Keep it exact and unbroken. Wavering attention sways the rope.",
        "index": "engagement", "target": "ix_engagement", "mode": "steady", "video": "scrub",
        "perturbation": "gust", "stability_gate": True,
        # once your attention map passes its gate, this level rewards YOUR focus signature instead
        "profile": {"contrast": "focus", "sign": 1},
        "basis": [
            "The engagement index beta / (alpha + theta) rises with sustained, task-focused attention and was built to drive attention-adaptive systems (Pope, Bogart & Bartolome 1995).",
            "Focus here must also be steady: the rope only stills when the index stays up without swinging, the stability that defines sustained attention.",
        ],
        "clip": {"file": "steady.mp4", "credit": "Tightrope walker, Pixabay (" + LICENCE + ")",
                 "page": "https://pixabay.com/videos/rope-balance-walker-risk-tightrope-132848/",
                 "urls": [PX + "2022/09/28/132848-754950610_medium.mp4", PX + "2022/09/28/132848-754950610_small.mp4",
                          PX + "2020/06/27/43254-435970559_large.mp4"]},
        "tiers": ladder(["Wobble", "Steadying", "Poised", "First steps", "Balanced", "Sure-footed", "Exact", "Effortless", "Monk"],
                        depth=(0.3, 2.5), perturb=(0.35, 1.0), every=(26, 13)),
    },
    {
        "entrain_hz": 6,
        "id": "ride", "number": 4, "title": "Ride", "subtitle": "Not too hard, not too easy",
        "tests": "Flow: absorbed, effortless doing",
        "instruction": "Ride with the surfer. Stay with every moment of the wave. Push too hard and it breaks up, drift off and it stalls. Find the pocket in between.",
        "index": "frontal_theta", "target": "ix_theta_af_rel", "mode": "ride", "video": "travel",
        "perturbation": "rapids",
        "gate": {"index": "engagement", "target": "ix_engagement", "lo": -0.75, "hi": 1.75, "soft": 0.5},
        "basis": [
            "Flow is absorbed engagement at the balance of challenge and skill (Csikszentmihalyi 1990), an inverted U: too little is boredom, too much is strain.",
            "EEG studies of flow report more frontal theta with moderate, not maximal, engagement (Katahira et al. 2018). So here frontal theta must rise while engagement stays inside a band.",
            "Forehead theta also picks up eye movement; blinks are held out, and the replay round checks the rest.",
        ],
        "clip": {"file": "ride.mp4", "credit": "Surfer riding a wave, Pixabay (" + LICENCE + ")",
                 "page": "https://pixabay.com/videos/ocean-nature-surfing-wave-31517/",
                 "urls": [PX + "2020/01/23/31517-387662255_medium.mp4", PX + "2020/01/23/31517-387662255_small.mp4",
                          PX + "2026/08/16/370908_large.mp4"]},
        "tiers": ladder(["Paddling", "Catching", "Up", "Riding", "Carving", "Gliding", "In the pocket", "Flow", "Monk"],
                        depth=(0.25, 2.2), perturb=(0.3, 0.95), every=(28, 14)),
    },
    {
        "entrain_hz": 0,
        "id": "storm", "number": 5, "title": "Storm", "subtitle": "Let it hit. Come back.",
        "tests": "Recovery: how fast you return after a shock",
        "instruction": "The storm will knock you. Don't brace, don't fight it. Let each hit pass through and come back to where you were. The sea slows as you return.",
        "index": "return", "target": "return", "mode": "storm", "video": "travel", "corridor": "near",
        "perturbation": "thunder",
        "basis": [
            "Resilience is recovery, not immunity: how quickly the brain returns to its own baseline after a disturbance (the return in Integrated Dynamic Awareness).",
            "Your baseline is this scene before the knocks; distance is measured in relative alpha and engagement together, and every knock's recovery time is scored.",
            "Knocks are single flashes and jolts, never flicker faster than once every few seconds.",
        ],
        "clip": {"file": "storm.mp4", "credit": "Stormy sea, Pixabay (" + LICENCE + ")",
                 "page": "https://pixabay.com/videos/wave-breaking-sea-ocean-water-283533/",
                 "urls": [PX + "2025/06/03/283533_large.mp4", PX + "2025/06/03/283533_medium.mp4",
                          PX + "2023/11/23/190331-887815673_medium.mp4"]},
        # corridor "near": depth is minus the largest distance from baseline that still counts
        "tiers": ladder(["Buffeted", "Bracing", "Holding", "Returning", "Anchored", "Unshaken", "Eye of the storm",
                         "Calm within", "Monk"], depth=(-1.6, -0.42), tau=(0.45, 0.22), novelty=(0.5, 0.85),
                        perturb=(0.65, 1.0), every=(13, 8), first_perturb=0.6),
    },
    {
        "entrain_hz": 40,
        "id": "sky", "number": 6, "title": "Night Sky", "subtitle": "Take in the whole sky",
        "tests": "Open awareness (experimental)",
        "instruction": "Don't pick a star. Let your gaze go wide and take in the whole sky at once. When a meteor pulls you, notice it and open back out.",
        "index": "complexity", "target": "lzc", "mode": "sky", "video": "scrub",
        "perturbation": "meteor",
        "profile": {"contrast": "scope", "sign": -1},
        "basis": [
            "Open monitoring meditation widens attention to everything at once instead of one object (Lutz et al. 2008).",
            "Signal complexity (Lempel-Ziv) tracks how much the brain is doing at once: it falls in sleep and anaesthesia and rises in expanded states (Casali 2013; Schartner 2017). The Murray Reality Equation names complexity as the measure of awareness.",
            "Whether you can raise it on purpose is an open question. This level is the test.",
        ],
        "clip": {"file": "sky.mp4", "credit": "Milky Way time-lapse over mountains, Pixabay (" + LICENCE + ")",
                 "page": "https://pixabay.com/videos/starry-sky-mountains-milky-way-169951/",
                 "urls": [PX + "2023/07/04/169951-842348732_medium.mp4", PX + "2023/07/04/169951-842348732_small.mp4",
                          PX + "2015/08/08/50-135716611_medium.mp4"]},
        "tiers": ladder(["Looking", "Wider", "Open", "Spacious", "Vast", "Boundless", "Clear sky", "Whole", "Monk"],
                        depth=(0.3, 2.4), perturb=(0.3, 0.9), every=(28, 14)),
    },
]

# The attention map: short tasks that force attention where the test needs it, with a
# behavioural check (press Space when a small light blinks where you are attending), so the EEG
# of focused, free, narrow and broad attention is labelled by what you actually did.
# roi = the region to attend, in the video's own coordinates: centre x, y and radii (0..1).
ATTENTION = [
    {"id": "attn_centre", "title": "Hold the centre", "clip": {
        "file": "centre.mp4", "credit": "City traffic time-lapse, Pixabay (" + LICENCE + ")",
        "page": "https://pixabay.com/videos/id-21985/",
        "urls": [PX + "2019/03/13/21985-323496013_large.mp4", PX + "2025/03/26/267745_large.mp4"]},
     "roi": [0.5, 0.5, 0.11, 0.19], "still_centre": True,
     "blocks": [["focus", 20], ["watch", 20], ["focus", 20], ["watch", 20], ["focus", 20], ["watch", 20]],
     "cue": {"focus": "Focus: the still centre", "watch": "Free: let your eyes wander"},
     "say": {"focus": "Keep your eyes and your mind on the still circle in the middle. Everything else can move. Press Space the moment the small light in the middle blinks.",
             "watch": "Now just watch. Let your eyes go wherever they like. Nothing to press."}},
    {"id": "attn_jelly", "title": "The jellyfish", "clip": {
        "file": "jelly.mp4", "credit": "Jellyfish, Pixabay (" + LICENCE + ")",
        "page": "https://pixabay.com/videos/id-134171/",
        "urls": [PX + "2022/10/09/134171-758855292_large.mp4", PX + "2022/10/09/134171-758855292_medium.mp4"]},
     "roi": [0.47, 0.58, 0.25, 0.40],
     "blocks": [["focus", 20], ["watch", 20], ["focus", 20], ["watch", 20], ["focus", 20], ["watch", 20]],
     "cue": {"focus": "Focus: the jellyfish", "watch": "Free: the whole scene"},
     "say": {"focus": "Rest all of your attention on the jellyfish. Let the rest fall away. Press Space when a light blinks on the jellyfish; ignore any in the background.",
             "watch": "Just watch the whole scene. Nothing to press."}},
    {"id": "attn_summit", "title": "The summit", "clip": {
        "file": "summit.mp4", "credit": "Climber on a snowy summit slope, Pixabay (" + LICENCE + ")",
        "page": "https://pixabay.com/videos/id-119076/",
        "urls": [PX + "2022/06/02/119076-716970666_medium.mp4", PX + "2021/05/06/73228-548173103_large.mp4"]},
     "roi": [0.25, 0.60, 0.09, 0.16],
     "blocks": [["narrow", 20], ["broad", 20], ["narrow", 20], ["broad", 20], ["narrow", 20], ["broad", 20]],
     "cue": {"narrow": "Narrow: only the climber", "broad": "Wide: the whole view at once"},
     "say": {"narrow": "Stay with the climber, only the climber. Press Space when a light blinks on them.",
             "broad": "Now open out and take in the whole view at once, every part of it together. Press Space when a light blinks anywhere."}},
]

if __name__ == "__main__":
    out = ROOT / "levels" / "levels.json"
    out.write_text(json.dumps({"version": 3, "levels": LEVELS, "attention": ATTENTION}, indent=1), encoding="utf-8")
    print(f"wrote {out} ({len(LEVELS)} levels)")
