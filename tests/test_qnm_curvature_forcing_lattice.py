"""Tests for the definitive curvature-forcing lattice (v2.417)."""

from experiments.qnm_curvature_forcing_lattice import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_lattice_shape():
    L = _RES["feasibility_lattice"]
    assert L["matter_only"]["gR2_floor"] < 0.02              # matter alone: g_R2 free
    assert L["cubic_g_R3_only"]["feasible"] is False          # cubic needs matter
    assert L["parity_only"]["feasible"] is False              # parity needs matter
    assert L["matter_plus_cubic"]["gR2_floor"] > 0.05         # matter+cubic forces g_R2>0
    assert L["matter_plus_parity"]["gR2_floor"] < 0.02        # matter+parity does NOT force


def test_sole_forcer_is_matter_x_cubic():
    assert _RES["consistency_checks"]["sole_forcer_is_matter_x_cubic"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "matter x cubic-curvature" in f
    assert "neither" in f and "matter sources gravity" in f
    assert "complete" in f or "all seven" in f
    sc = _RES["honest_scope"].lower()
    assert "refines v2.416" in sc
    assert "qualitative pattern" in sc
