"""Tests for the rigorous strict-floor upgrade (v2.369)."""

from experiments.qnm_ringdown_floor_strict import run

_RES = run(n_random=20000, seed=0)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_matter_multistate():
    assert _RES["r_matter"] < 1.0


def test_strict_cauchy_schwarz():
    # every distinct-mass 2-state measure has r < 1 (the bound 1 approached only as masses coincide);
    # the honest strict check is the positive gap (the reported max rounds up toward 1)
    assert _RES["strict_cs_gap_to_1"] > 0.0
    assert _RES["consistency_checks"]["strict_cauchy_schwarz_r_below_1_for_distinct_masses"] is True
    assert _RES["consistency_checks"]["single_state_saturates_r_equals_1"] is True


def test_form_factor_independent():
    lo, hi = _RES["r_curv_scan_min_max"]
    assert hi < 1.0          # r_curv < 1 even at the extreme end of s in [-5,5]
    assert lo < hi           # it does vary (that is why the VALUE is fragile, v2.368)


def test_arc_and_rigor_framing():
    arc = _RES["arc"]
    assert "conjecture" in arc["v2367"]
    assert "band" in arc["v2368"]
    assert "STRICT" in arc["v2369"] or "strict" in arc["v2369"].lower()
    f = _RES["finding"].lower()
    assert "equivalence principle" in f
    assert "strictly" in f
    assert "theorem" in f
    sc = _RES["honest_scope"].lower()
    assert "strict inequality" in sc and "not a value" in sc
    assert "toy" in sc
