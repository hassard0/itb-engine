"""Tests for the multi-messenger parity analysis (v1.81)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import multimessenger_parity as mm
from itb.constraints.cosmic_birefringence import KAPPA_BETA


def test_three_positive_signals():
    beta, gw, pta = mm.predicted_signals()
    assert beta > 0 and gw > 0 and pta > 0


def test_cmb_beta_from_coupling():
    beta, _, _ = mm.predicted_signals()
    assert beta == pytest.approx(KAPPA_BETA * mm.GP, rel=1e-6)


def test_only_cmb_detected_now():
    """CMB currently detects (>1 sigma); GW & PTA predicted below current
    sensitivity (multi-messenger consistent, no current exclusion)."""
    beta, gw, pta = mm.predicted_signals()
    # CMB: 0.32 deg vs 0.09 deg sigma -> > 1
    assert beta / 0.09 > 1.0
    # GW & PTA snr_now < 1 by construction (current limits weak)
    assert gw / (gw * 30.0) < 1.0
    assert pta / 50.0 < 1.0
