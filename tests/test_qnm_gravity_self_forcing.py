"""Tests for the v2.416 self-correction (matter-sources-gravity mis-attribution)."""

from experiments.qnm_gravity_self_forcing import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_matter_alone_does_not_force_curvature():
    assert _RES["gR2_floor_matter_only"] == 0.0
    assert _RES["matter_with_tiny_gR2_is_feasible"] is True


def test_gravity_structure_forces_curvature():
    assert len(_RES["cubic_curvature_forcers"]) >= 2
    assert len(_RES["parity_forcers"]) >= 2
    # v2.414 config floor is positive (candidate has g_R3 + parity), but from gravity structure not matter
    assert _RES["gR2_floor_v2414_config_matter_plus_gR3_parity"] > 0.05


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "self-correction" in f
    assert "mis-attributed" in f
    assert "retracted" in f or "corrects" in f
    sc = _RES["honest_scope"].lower()
    assert "retracts" in sc
    assert "other de-toying results" in sc or "those stand" in sc
