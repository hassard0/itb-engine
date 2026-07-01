"""Tests for the Weyl-sector marginalization swing (v2.400)."""

from experiments.qnm_weyl_sector_marginalized import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_bh_decay_robust():
    m = _RES["bh_entropy_shift"]["marginalized"]
    assert min(m) > 0.0                       # Delta S_ext > 0 across the wedge


def test_ghost_safe_robust():
    m = _RES["ghost_mass_over_cutoff"]["marginalized"]
    assert min(m) > 1.0                       # ghost above cutoff across the wedge


def test_cutoff_near_planckian_robust():
    m = _RES["species_cutoff_over_Mpl"]["marginalized"]
    assert min(m) > 0.5 and max(m) < 1.0      # near-Planckian across the wedge


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "survive the a=c assumption" in f
    assert "only their magnitudes loosen" in f or "widens the error bars" in f
    assert "closes the c!=a arc" in f
    sc = _RES["honest_scope"].lower()
    assert "toy" in sc
    assert "sign/ordering" in sc or "threshold survival" in sc or "sign/threshold" in sc
