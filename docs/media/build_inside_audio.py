"""Build Inside's synchronized voice-and-score track from the voice master.

Run with the workspace Python runtime; requires numpy and imageio_ffmpeg.
The master has eight paragraphs in the same order as the film scenes. The cut
points fall in the generated silences between those paragraphs, checked with
ffmpeg's silencedetect. The score is generated here, with a fixed random seed.
"""

from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import wave

import imageio_ffmpeg
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
VOICE = Path(__file__).with_name("inside-voice-master.mp3")
OUTPUT = ROOT / "site" / "inside-audio.mp3"
RATE = 24_000
ENDS = [0, 10.543, 20.215, 34.805, 49.258, 61.975, 70.882, 81.423, 92.712]
SCENE_LENGTHS = [14, 13, 19, 19, 17, 12, 14, 15]
SCENE_STARTS = np.cumsum([0, *SCENE_LENGTHS[:-1]]).tolist()
DURATION = sum(SCENE_LENGTHS)


def write_score(path: Path) -> None:
    t = np.arange(RATE * DURATION, dtype=np.float32) / RATE
    fade = np.minimum(1, t / 3) * np.minimum(1, (DURATION - t) / 5)
    swell = np.interp(t, [0, 27, 46, 82, 94, 108, 123], [.55, .7, .46, .6, .9, .75, .1])
    slow = .78 + .22 * np.sin(2 * np.pi * .052 * t)
    base = (
        .036 * np.sin(2 * np.pi * (55 * t + .26 * np.sin(2 * np.pi * .025 * t)))
        + .021 * np.sin(2 * np.pi * 82.407 * t)
        + .012 * np.sin(2 * np.pi * 164.814 * t + .28 * np.sin(2 * np.pi * .011 * t))
        + .007 * np.sin(2 * np.pi * 220 * t)
    ) * slow * swell * fade
    rng = np.random.default_rng(1962)
    knots = rng.normal(0, 1, DURATION * 75 + 1).astype(np.float32)
    wind = np.interp(t * 75, np.arange(len(knots)), knots).astype(np.float32)
    wind *= .006 * (.5 + .5 * np.sin(2 * np.pi * .07 * t + 1)) * fade
    left = base + wind
    right = base * .96 - wind * .7
    for index, start in enumerate(SCENE_STARTS[1:], 1):
        count = 3 * RATE
        pulse_t = np.arange(count, dtype=np.float32) / RATE
        frequency = [330, 392, 293.66, 440, 329.63, 493.88, 659.25][index - 1]
        chime = .035 * np.exp(-1.8 * pulse_t) * (
            np.sin(2 * np.pi * frequency * pulse_t)
            + .27 * np.sin(2 * np.pi * frequency * 2.01 * pulse_t)
        )
        offset = start * RATE
        left[offset : offset + count] += chime * (.65 if index % 2 else 1)
        right[offset : offset + count] += chime * (1 if index % 2 else .65)
    pcm = np.column_stack((left, right))
    pcm = np.clip(pcm * 32767, -32767, 32767).astype("<i2")
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(pcm.tobytes())


def build() -> None:
    if not VOICE.is_file():
        raise SystemExit(f"Missing voice master: {VOICE}")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    with TemporaryDirectory(prefix="inside-audio-") as scratch:
        score = Path(scratch) / "score.wav"
        write_score(score)
        filters = ["[0:a]asplit=8" + "".join(f"[s{i}]" for i in range(8))]
        for index, length in enumerate(SCENE_LENGTHS):
            filters.append(
                f"[s{index}]atrim=start={ENDS[index]}:end={ENDS[index + 1]},"
                "asetpts=PTS-STARTPTS,atempo=0.85,apad=pad_dur=3,"
                f"atrim=0:{length},asetpts=PTS-STARTPTS[v{index}]"
            )
        filters.append("".join(f"[v{i}]" for i in range(8)) + "concat=n=8:v=0:a=1[voice]")
        filters.append("[voice]aformat=channel_layouts=stereo,volume=1.0[narration]")
        filters.append("[1:a]volume=0.34[score]")
        filters.append("[narration][score]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.92[out]")
        command = [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(VOICE), "-i", str(score),
            "-filter_complex", ";".join(filters), "-map", "[out]",
            "-ar", str(RATE), "-codec:a", "libmp3lame", "-b:a", "160k",
            str(OUTPUT),
        ]
        subprocess.run(command, check=True)
    print(f"Built {OUTPUT} ({DURATION} seconds)")


if __name__ == "__main__":
    build()
