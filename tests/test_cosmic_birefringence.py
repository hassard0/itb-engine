"""Tests for the cosmic-birefringence DATA constraint (v1.78)."""
import sys
from pathlib import Path

import pytest

from itb.constraints.cosmic_birefringence import CosmicBirefringenceData, KAPPA_BETA
from itb.theory import Theory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))


def _th(gp):
    return Theory(coefficients={"g_R2_parity": gp, "g_R3_parity": 0.0})


def test_beta_mapping():
    c = CosmicBirefringenceData()
    assert c.beta_pred(_th(0.1)) == pytest.approx(KAPPA_BETA * 0.1)


def test_excludes_zero_and_band():
    c = CosmicBirefringenceData(mode="hint", n_sigma=2.0)
    assert c.excludes_zero_at_sigma == pytest.approx(0.34 / 0.09, abs=0.05)
    lo, hi = c.preferred_band
    assert lo > 0.0                                  # band excludes zero (positive)
    assert lo < 0.1 < hi                             # MK central value is inside


def test_prefers_nonzero_positive():
    """Nonzero positive-handed coupling satisfies; parity-even (0) does not."""
    c = CosmicBirefringenceData(mode="hint", n_sigma=2.0)
    assert c.evaluate(_th(0.10)).satisfied           # bullseye
    assert not c.evaluate(_th(0.0)).satisfied        # parity-even disfavored


def test_wrong_handedness_excluded():
    """A negative (opposite-sign) parity coupling predicts beta<0 -> disfavored."""
    c = CosmicBirefringenceData(mode="hint", n_sigma=2.0)
    assert not c.evaluate(_th(-0.092)).satisfied


def test_ignore_mode_vacuous():
    c = CosmicBirefringenceData(mode="ignore")
    assert c.evaluate(_th(0.0)).satisfied
    assert c.evaluate(_th(-0.5)).satisfied


def test_build_stack_birefringence_optional():
    from stack import build_stack
    theo = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    bire = build_stack(bnossw_mean="geometric", rfc_form="convex_hull",
                       include_birefringence=True)
    assert len(bire) == len(theo) + 1
    assert bire[-1].name == "cosmic_birefringence_data"
    assert "cosmic_birefringence_data" not in [c.name for c in theo]
