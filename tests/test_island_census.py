"""Sanity tests for the global survival census (v1.73)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import island_census as ic


def test_box_is_parity_even():
    """Parity columns are pinned to zero (parity-even census slice)."""
    pi = ic.COEFFS.index("g_R2_parity")
    pj = ic.COEFFS.index("g_R3_parity")
    assert ic.LO[pi] == ic.HI[pi] == 0.0
    assert ic.LO[pj] == ic.HI[pj] == 0.0
    assert int(ic.VARY.sum()) == 6        # six varying coordinates


def test_box_well_formed():
    assert len(ic.COEFFS) == len(ic.LO) == len(ic.HI) == 8
    assert np.all(ic.HI >= ic.LO)


def test_eval_chunk_runs():
    """A small chunk evaluates and returns a coherent structure."""
    surv, n, binding, fail, surv_X = ic._eval_chunk((1234, 500))
    assert n == 500
    assert 0 <= surv <= n
    assert surv_X.shape[0] == surv          # survivor rows match count
    if surv:
        assert surv_X.shape[1] == 8
        # survivors must lie within the box
        assert np.all(surv_X >= ic.LO - 1e-9)
        assert np.all(surv_X <= ic.HI + 1e-9)
    # binding counts only for survivors; fail counts only for failures
    assert int(binding.sum()) == surv
    assert int(fail.sum()) == n - surv
