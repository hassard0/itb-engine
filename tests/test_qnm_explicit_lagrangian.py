"""Tests for the explicit-Lagrangian capstone (v2.450)."""

from experiments.qnm_explicit_lagrangian import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_candidate_feasible():
    assert _RES["candidate_feasible"] is True


def test_two_scalars_opposite_parity():
    scalars = [t for t in _RES["lagrangian_terms"] if "phi" in t["field"] or "theta" in t["field"]]
    assert len(scalars) == 2
    assert {s["parity"] for s in scalars} == {"even", "odd"}


def test_graviton_presupposed_matter_dominant():
    terms = _RES["lagrangian_terms"]
    assert any(t["tier"] == "presupposed" and "graviton" in t["field"] for t in terms)
    matter = next(t for t in terms if t["field"] == "matter")
    assert "dominant" in matter["coefficient"].lower()


def test_scales_and_scope():
    assert "0.72 M_Pl" in _RES["scales"]["UV_cutoff"]
    assert "3e13 GeV" in _RES["scales"]["scalaron_mass"]
    sc = _RES["honest_scope"].lower()
    assert "synthesis" in sc
    assert "schematic" in sc
    assert "toy" in sc
