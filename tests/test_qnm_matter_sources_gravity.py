"""Tests for the matter-sources-gravity swing (v2.393)."""

from experiments.qnm_matter_sources_gravity import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_pure_gr_ok_but_matter_only_forbidden():
    assert _RES["pure_gr_feasible"] is True
    assert _RES["matter_only_feasible"] is False
    assert "anomaly_cancellation" in _RES["matter_only_violations"]


def test_anomaly_forces_nonzero_gR2():
    lo, hi = _RES["anomaly_forced_gR2_band"]
    assert lo > 0.0                     # g_R2=0 forbidden
    assert hi > lo
    fr = _RES["feasible_gR2_with_matter_only"]
    assert fr[0] > 1e-3                  # nonzero floor


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "sources the leading gravitational correction" in f
    assert "converse of matter dominance" in f
    assert "forbidden" in f
    sc = _RES["honest_scope"].lower()
    assert "toy" in sc
    assert "no perturbative gravitational anomaly for the graviton alone" in sc or "toy encoding" in sc
    assert "forbid-the-zero-corner" in sc or "forbids the g_r2 = 0 corner" in sc or "forbid zero" in sc
