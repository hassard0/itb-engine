"""Tests for the gravitational-leptogenesis unification (v2.324)."""

from experiments.qnm_gravitational_leptogenesis import run, eta_B, beta_deg, chirality


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_parity_even_zero_baryon_asymmetry():
    res = run()
    for r in res["table"]:
        if not r["parity_violating"]:
            assert abs(r["eta_B_schematic"]) < 1e-12
            assert r["can_source_baryon_asymmetry"] is False


def test_baryon_asymmetry_requires_parity():
    assert abs(eta_B(0.0)) < 1e-12
    assert abs(eta_B(0.06)) > 1e-12
    # sign tracks the coupling
    assert eta_B(0.06) > 0 and eta_B(-0.06) < 0


def test_three_signatures_sourced_by_same_coupling():
    # all three vanish at zero coupling, all nonzero for nonzero coupling
    assert abs(eta_B(0.0)) < 1e-12 and abs(beta_deg(0.0)) < 1e-12 and abs(chirality(0.0)) < 1e-12
    gp = 0.06
    assert eta_B(gp) > 0 and beta_deg(gp) > 0 and chirality(gp) > 0


def test_only_parity_violating_frameworks_source_baryons():
    res = run()
    sourcing = sorted(r["theory"] for r in res["table"] if r["can_source_baryon_asymmetry"])
    assert sourcing == ["engine_preferred", "lqg_induced"]


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "baryon asymmetry" in f
    assert "unifies three" in f or "three cosmological signatures" in f
    sc = res["honest_scope"].lower()
    assert "not the magnitude" in sc
    assert "scale-dependent" in sc
    assert "toy basis" in sc
