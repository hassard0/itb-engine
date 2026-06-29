"""Tests for the Riccati QNM solver + precision-requirement study (v2.213)."""

from experiments.qnm_riccati_solver import (
    REF,
    riccati_qnm,
    run,
    rw_potential,
)
from experiments.qnm_wkb_solver import schwarzschild_qnm


def test_riccati_is_an_independent_method_in_the_ballpark():
    # different method than WKB; lands the fundamental within a few percent
    ref = REF[(2, 0)]
    w = riccati_qnm(ref, L=2)
    assert w.imag < 0
    assert abs(w - ref) / abs(ref) < 0.06


def test_wkb_is_far_more_accurate_than_riccati():
    ref = REF[(2, 0)]
    wkb_err = abs(schwarzschild_qnm(n=0, L=2) - ref) / abs(ref)
    ric_err = abs(riccati_qnm(ref, L=2) - ref) / abs(ref)
    assert wkb_err < 0.01
    assert ric_err > wkb_err          # Riccati is the looser cross-check


def test_few_pct_resolve_does_not_yield_claim_grade_e_j():
    # the precision-requirement finding: a few-%-accurate re-solve is erratic for e_j
    res = run()
    sp = res["sensitivity_precision_study"]
    assert sp["resolve_at_1pct_reproduces_e_j"] is False
    assert sp["max_rel_error"] > 0.3
    assert res["claim_gate"].startswith("closed")


def test_potential_matches_wkb_module():
    # same Regge-Wheeler potential as the WKB solver
    from experiments.qnm_wkb_solver import rw_potential as rw2
    for r in (3.0, 5.0, 10.0):
        assert abs(rw_potential(r) - rw2(r)) < 1e-12
