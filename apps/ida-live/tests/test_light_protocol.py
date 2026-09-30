import asyncio
from collections import Counter

import numpy as np
import pytest

from ida_live.config import load_settings
from ida_live.protocols.ir import LightTrialProtocol, make_allocation


def test_allocation_balanced_in_blocks():
    rng = np.random.default_rng(3)
    arms = make_allocation(12, 4, rng, "small")
    for i in range(0, 12, 4):
        assert Counter(arms[i:i + 4]) == {"active": 2, "sham": 2}
    assert make_allocation(6, 4, rng, "nothing") == ["sham"] * 6


class FakeSource:
    can_set_preset = True

    def __init__(self):
        self.calls = []
        self.t = 0.0

    async def set_preset(self, preset):
        self.calls.append(preset)
        return float(len(self.calls))


def test_sham_and_active_send_identical_command_counts(tmp_path):
    s = load_settings()
    s["ir_protocol"].update(trials=4, pre_s=0.01, post_s=0.01, iti_jitter_s=[0.0, 0.01])
    s["ir_protocol"]["burst_s"]["small"] = 0.01
    src, events = FakeSource(), []
    p = LightTrialProtocol(s, "small", src, tmp_path, emit=lambda k, d: events.append((k, d)),
                           ask_guess=None, mark_event=lambda k: None, bench=True)
    asyncio.run(p.run())
    # one settle command, then exactly two commands per trial regardless of arm
    assert len(src.calls) == 1 + 2 * 4
    per_trial = [src.calls[1 + 2 * i: 3 + 2 * i] for i in range(4)]
    for arm, (on, off) in zip(p.arms, per_trial):
        assert off == "p20"
        assert on == ("p1035" if arm == "active" else "p20")
    # no public event carries the allocation
    assert not any("arms" in d for _, d in events)
    sealed = p.reveal()
    assert sealed["arms"] == p.arms


def test_reveal_refuses_before_end_and_detects_tampering(tmp_path):
    s = load_settings()
    p = LightTrialProtocol(s, "small", FakeSource(), tmp_path, emit=lambda k, d: None,
                           ask_guess=None, mark_event=lambda k: None)
    with pytest.raises(RuntimeError):
        p.reveal()
    p.state = "done"
    (tmp_path / "allocation.sealed.json").write_text("{}")
    with pytest.raises(RuntimeError):
        p.reveal()


def test_rejects_sources_without_preset_control(tmp_path):
    class NoControl:
        can_set_preset = False

    with pytest.raises(RuntimeError):
        LightTrialProtocol(load_settings(), "small", NoControl(), tmp_path, lambda k, d: None, None, lambda k: None)
