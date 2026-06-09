"""Tests for the Bayesian model comparison (v2.01)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import bayesian_model_comparison as bmc


def _vec(**kw):
    x = np.zeros(len(bmc.COEFFS))
    for k, v in kw.items():
        x[bmc.COEFFS.index(k)] = v
    return x


def test_matching_beta_beats_zero():
    """A framework predicting beta ~ 0.34 has higher likelihood than one with beta = 0."""
    match = bmc.log_like(_vec(g_R2_parity=0.34 / bmc.KAPPA_BETA), screened=True)
    zero = bmc.log_like(_vec(g_R2_parity=0.0), screened=True)
    assert match > zero


def test_submm_penalizes_large_unscreened_scalaron():
    """A large g_R2 is penalized when unscreened, exempt when screened."""
    big = _vec(g_R2_parity=0.1, g_R2=0.5)
    assert bmc.log_like(big, screened=False) < bmc.log_like(big, screened=True)


def test_catalogued_frameworks_predict_zero_beta_data_driven_matches():
    """Textbook frameworks predict beta=0 (disfavored); the data-driven EFT matches ~0.34."""
    def beta(name):
        g = bmc.FRAMEWORKS[name].encode().coefficients.get("g_R2_parity", 0.0)
        return bmc.KAPPA_BETA * g
    assert beta("string_tree_eft") == 0.0
    assert beta("asymptotic_safety") == 0.0
    assert abs(beta("discovered_data_driven") - bmc.BETA_OBS) < 0.1   # ~0.32 vs 0.34
