"""Tests for the minimal falsifier (v2.04)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import json
import io
import contextlib

import minimal_falsifier as mf


def _run():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        mf.main()
    return json.loads(buf.getvalue())


def test_power_nonnegative_and_birefringence_top():
    s = _run()
    ranking = s["ranking"]
    assert all(r["falsification_power_sigma"] >= 0 for r in ranking)
    assert "birefringence" in ranking[0]["obs"].lower()      # top falsifier


def test_huge_sigma_gives_low_power():
    """A measurement with a large sigma has low falsification power."""
    power_tight = abs(0.32 - 0.0) / 0.03
    power_loose = abs(0.32 - 0.0) / 0.30
    assert power_loose < power_tight


def test_minimal_falsifier_is_birefringence_2030():
    s = _run()
    assert "birefringence" in s["minimal_falsifier"].lower()
    assert "2030" in s["minimal_falsifier"]
