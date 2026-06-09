"""Tests for the data-driven EFT (v1.79)."""
import sys
from pathlib import Path

import pytest

from itb.frameworks.data_driven import DiscoveredDataDriven
from itb.constraints.cosmic_birefringence import CosmicBirefringenceData, KAPPA_BETA

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))


def test_passes_theory_and_birefringence():
    """The data-driven EFT satisfies the theoretical stack AND the cosmic
    birefringence band (it is the consistent, beta-matching EFT)."""
    from stack import build_stack
    th = DiscoveredDataDriven().encode()
    theo = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    assert all(c.evaluate(th).satisfied for c in theo)
    assert CosmicBirefringenceData(mode="hint", n_sigma=2.0).evaluate(th).satisfied


def test_predicts_measured_beta():
    """Its parity coupling reproduces the Minami-Komatsu beta ~ 0.34 deg."""
    th = DiscoveredDataDriven().encode()
    beta = KAPPA_BETA * th.coefficients["g_R2_parity"]
    assert beta == pytest.approx(0.34, abs=0.05)


def test_requires_screening():
    """Its scalaron is heavy enough (large g_R2) that the UNSCREENED sub-mm bound
    excludes it -- viability requires screening (v1.79 headline)."""
    from itb.constraints.submm_gravity import SubmmGravityYukawaBound
    th = DiscoveredDataDriven().encode()
    assert not SubmmGravityYukawaBound(screened=False).evaluate(th).satisfied
    assert SubmmGravityYukawaBound(screened=True).evaluate(th).satisfied


def test_in_predict_registry():
    from itb.predict import FRAMEWORKS, predict
    assert "discovered_data_driven" in FRAMEWORKS
    p = predict("discovered_data_driven")
    assert "coefficients" in p or "observables" in p
