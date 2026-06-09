"""Tests for the black-hole entropy shift / WGC sector (v1.82)."""
import sys
from pathlib import Path

import pytest

from itb.gravitational_observables import BlackHoleEntropyShift
from itb.constraints.bh_entropy_positivity import WaldEntropyPositivity
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.pure_gr import PureGR
from itb.theory import Theory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))


def test_mapping_and_euler_drops_out():
    """Delta S_ext = A*g_C + B*g_4; g_R2 (Euler) is topological -> zero jacobian."""
    obs = BlackHoleEntropyShift(A=1.0, B=0.5)
    th = Theory(coefficients={"g_C": 0.3, "g_4": 0.5, "g_R2": 0.4})
    assert obs.predict(th)[0] == pytest.approx(0.3 + 0.5 * 0.5)
    J = obs.jacobian(th, ["g_C", "g_4", "g_R2"])
    assert J[0, 0] == 1.0          # g_C
    assert J[0, 1] == 0.5          # g_4
    assert J[0, 2] == 0.0          # g_R2 (Euler) topological -> no entropy shift


def test_positive_for_consistent_frameworks():
    """String-EFT and asymptotic safety have Delta S_ext > 0 (WGC: BHs can decay)."""
    obs = BlackHoleEntropyShift()
    for fw in (StringTreeEFT(), AsymptoticSafety()):
        assert obs.predict(fw.encode())[0] > 0.0


def test_pure_gr_zero_shift():
    """Pure two-derivative GR has no higher-derivative correction -> Delta S = 0."""
    obs = BlackHoleEntropyShift()
    assert obs.predict(PureGR().encode())[0] == pytest.approx(0.0, abs=1e-9)
    # and Wald positivity is (marginally) satisfied
    assert WaldEntropyPositivity().evaluate(PureGR().encode()).satisfied


def test_wald_positivity_satisfied_by_survivors():
    """The Wald-entropy condition is satisfied by the consistent frameworks (it is a
    thermodynamic restatement of positivity, not a new exclusion)."""
    from stack import build_stack
    stack = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    assert "wald_entropy_positivity" in [c.name for c in stack]
    for fw in (StringTreeEFT(), AsymptoticSafety()):
        th = fw.encode()
        if all(c.evaluate(th).satisfied for c in stack if c.name != "wald_entropy_positivity"):
            assert WaldEntropyPositivity().evaluate(th).satisfied


def test_in_predict_fingerprint():
    from itb.predict import predict
    p = predict("discovered_data_driven")
    assert "bh_entropy_shift_delta_S_ext" in p["observables"]
    assert p["observables"]["bh_entropy_shift_delta_S_ext"] > 0.0
