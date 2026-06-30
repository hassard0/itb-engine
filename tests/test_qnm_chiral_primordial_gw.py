"""Tests for the chiral primordial GW parity discriminator (v2.319)."""

from experiments.qnm_chiral_primordial_gw import run, chirality


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_parity_even_frameworks_zero_chirality():
    res = run()
    for r in res["chirality_table"]:
        if not r["parity_violating"]:
            assert abs(r["chirality_Pi"]) < 1e-9
            assert r["predicts_CMB_TB_EB"] is False


def test_only_preferred_and_lqg_are_chiral():
    res = run()
    assert res["chiral_theories"] == ["engine_preferred", "lqg_induced"]


def test_chirality_sign_tracks_coupling_and_bounded():
    # positive coupling -> right-handed (positive Pi); bounded
    assert chirality(0.08) > 0
    assert chirality(-0.08) < 0
    assert abs(chirality(1.0)) < 1.0           # strictly bounded for a moderate coupling
    assert abs(chirality(10.0)) <= 1.0         # never exceeds unity even for large coupling
    assert abs(chirality(0.0)) < 1e-12          # zero coupling -> zero chirality


def test_chirality_is_chromatic():
    # grows in magnitude with wavenumber
    assert abs(chirality(0.08, k=4.0)) > abs(chirality(0.08, k=1.0))


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "chiral primordial" in f
    assert "tb" in f and "eb" in f
    assert "discriminator" in f
    sc = res["honest_scope"].lower()
    assert "magnitude is schematic" in sc
    assert "toy basis" in sc
