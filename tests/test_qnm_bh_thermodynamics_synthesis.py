"""Tests for the BH-thermodynamics synthesis capstone (v2.277)."""

import math

from experiments.qnm_bh_thermodynamics_synthesis import run
from experiments.qnm_black_hole_thermodynamics import M_PL_KG, T_PL_K, hawking_temperature_K


def test_all_checks_pass():
    res = run()
    assert res["all_pass"] is True
    assert res["checks_passed"] == res["checks_total"] == 6
    for c in res["consistency_checks"]:
        assert c["pass"] is True, c["name"]


def test_hawking_temperature_bridges_si_and_natural_units():
    # T_H(M_Pl)/T_Pl must equal the natural-units T_H = 1/(8 pi) used in v2.273/274/276
    assert abs(hawking_temperature_K(M_PL_KG) / T_PL_K - 1.0 / (8 * math.pi)) < 1e-6


def test_area_is_the_unifying_object_six_roles():
    res = run()
    roles = res["area_is_the_unifying_object"]
    assert len(roles) == 6
    text = " ".join(r["area_role"] for r in roles).lower()
    for word in ("entropy", "bound", "radiates", "quantized", "island", "phase"):
        assert word in text


def test_each_check_named_and_true():
    res = run()
    names = {c["name"] for c in res["consistency_checks"]}
    assert "bekenstein_holographic_S_BH_all_equal" in names
    assert "area_quantum_entropy_is_ln3" in names
    assert "hawking_T_is_1_over_8piM_across_units" in names


def test_honest_scope_is_synthesis_not_new_bound():
    res = run()
    sc = res["honest_scope"].lower()
    assert "no new bound" in sc
    assert "synthesis" in sc or "cross-verification" in sc
    assert "not an engine constraint refit" in sc
