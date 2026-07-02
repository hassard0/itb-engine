"""Tests for the chiral-primordial-GW fingerprint (v2.443)."""

from experiments.qnm_chiral_gw import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_chirality_nonzero_and_locked():
    assert _RES["chirality_Pi_nonzero"] is True
    assert _RES["chirality_handedness"] == "positive"
    assert _RES["generic_starobinsky_Pi"] == 0.0


def test_parity_keystone_over_determined():
    od = _RES["parity_keystone_over_determination"]
    assert od["over_determined"] is True
    assert "birefringence" in od["experiment_1"].lower()
    assert "gw" in od["experiment_2"].lower()


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "chiral" in f and "over-determined" in f
    assert "plateau-class degeneracy" in f
    sc = _RES["honest_scope"].lower()
    assert "standard" in sc
    assert "amplitude" in sc and ("suppressed" in sc or "not computed" in sc or "uncomputed" in sc)
    assert "sign" in sc
