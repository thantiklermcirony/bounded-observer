"""Decode real Muse S Athena bytes (OpenMuse test recording, preset p1035) through the live path."""

import asyncio
from pathlib import Path

import pytest

from ida_live.config import load_settings
from ida_live.core import Buffers, now
from ida_live.features import build_all

DATA = Path(__file__).parent / "data" / "athena_p1035_openmuse.txt"


@pytest.mark.skipif(not DATA.exists(), reason="sample recording not present")
def test_real_bytes_decode_to_expected_streams():
    pytest.importorskip("bleak")
    from ida_live.sources.replay import ReplaySource

    s = load_settings()
    bufs = Buffers()
    src = ReplaySource(s, bufs.push, lambda m: None, path=str(DATA), speed=8.0)

    async def go():
        await src.start()
        await asyncio.sleep(4.0)
        await src.stop()

    asyncio.run(go())
    assert bufs.get("EEG").channels == ["EEG_TP9", "EEG_AF7", "EEG_AF8", "EEG_TP10"]
    assert bufs.get("OPTICS").channels == ["OPTICS_LI_NIR", "OPTICS_RI_NIR", "OPTICS_LI_IR", "OPTICS_RI_IR"]
    assert bufs.get("EEG").total > 2000
    vals = {}
    for f in build_all(s):
        v, _ = f.compute(bufs, now())
        vals.update(v)
    assert {"alpha_tp", "theta_af", "beta", "aperiodic"} <= set(vals)
    assert 45 < vals.get("heart_bpm", 0) < 110
