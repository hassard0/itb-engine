"""Tests for the swampland-web synthesis capstone (v2.265)."""

import math

from experiments.qnm_swampland_web_synthesis import run
from experiments.qnm_inflation_tensor_qg import M_PL_GEV
from experiments.qnm_weak_gravity_conjecture import M_PL_eV


def test_all_consistency_checks_pass():
    res = run()
    assert res["all_pass"] is True
    assert res["checks_passed"] == res["checks_total"] == 6
    for c in res["consistency_checks"]:
        assert c["pass"] is True


def test_planck_conventions_differ_by_sqrt_8pi():
    # the full (WGC) and reduced (inflation/TCC/species) Planck masses must differ by sqrt(8 pi)
    ratio = (M_PL_eV / 1e9) / M_PL_GEV
    assert abs(ratio - math.sqrt(8 * math.pi)) / math.sqrt(8 * math.pi) < 0.01


def test_web_has_four_conjectures():
    res = run()
    names = " ".join(w["conjecture"] for w in res["swampland_web"]).lower()
    for tag in ("weak gravity", "distance", "trans-planckian", "species"):
        assert tag in names


def test_tcc_is_the_strongest_r_bound():
    res = run()
    chk = {c["name"]: c["pass"] for c in res["consistency_checks"]}
    assert chk["tcc_strictly_stronger_than_sdc"] is True
    assert chk["both_push_r_down"] is True


def test_honest_scope_flags_synthesis_not_new_bound():
    res = run()
    sc = res["honest_scope"].lower()
    assert "no new bound" in sc
    assert "conjecture" in sc
    assert "light tower" in sc
