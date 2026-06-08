"""Tests for the Bayesian framework-inference layer (v1.52)."""

import pytest

from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.discovered import DiscoveredParityViolating
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.inference import framework_posterior

FWS = [StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
       CausalDynamicalTriangulation(), DiscoveredParityViolating()]


def test_no_measurement_returns_prior():
    post = framework_posterior({}, FWS)
    assert all(abs(p.posterior - 1.0 / len(FWS)) < 1e-9 for p in post)


def test_posterior_normalized():
    post = framework_posterior({"g_R2_parity": (0.09, 0.02)}, FWS)
    assert abs(sum(p.posterior for p in post) - 1.0) < 1e-9


def test_parity_detection_is_handedness_sensitive():
    """Parity violation carries a sign. A measured g_R2_parity = +0.09 favours
    LQG (+0.08); a measured -0.09 favours the discovered branch (-0.092). The
    inference correctly distinguishes handedness."""
    pos = framework_posterior({"g_R2_parity": (0.09, 0.02)}, FWS)
    assert pos[0].name == "lqg_induced"                      # +0.09 -> +parity
    neg = framework_posterior({"g_R2_parity": (-0.09, 0.02)}, FWS)
    assert neg[0].name == "discovered_parity_violating"      # -0.09 -> -parity
    # parity-conserving frameworks (g_R2_parity=0) are strongly suppressed either way
    pc = next(p for p in pos if p.name == "string_tree_eft")
    assert pc.posterior < 0.01


def test_parity_null_favours_parity_conserving():
    """A tight null on g_R2_parity should disfavour LQG / parity-violating branch."""
    post = framework_posterior({"g_R2_parity": (0.0, 0.01)}, FWS)
    top = post[0].name
    assert top in ("string_tree_eft", "asymptotic_safety", "cdt")
    pv = next(p for p in post if p.name == "discovered_parity_violating")
    assert pv.posterior < 0.05


def test_sub_mm_yukawa_favours_matching_gR2():
    """g_R2 = 0.30 (LQG's value) should favour LQG over small-g_R2 frameworks."""
    post = framework_posterior({"g_R2": (0.30, 0.02)}, FWS)
    assert post[0].name == "lqg_induced"
