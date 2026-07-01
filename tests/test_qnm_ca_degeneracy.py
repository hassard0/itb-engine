"""Tests for the c-a degeneracy method swing (v2.397)."""

from experiments.qnm_ca_degeneracy import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_gR2_drives_supermajority():
    assert _RES["n_gR2_dependent"] > _RES["n_total_constraints"] / 2
    assert _RES["gR2_dependent_fraction"] > 0.5


def test_hofman_maldacena_trivial():
    assert _RES["hofman_maldacena_trivial"] is True
    assert _RES["hofman_maldacena_margin"] > 0.2   # a/c=1 deep inside the wedge


def test_would_unlock_lists_real_constraints():
    assert len(_RES["would_unlock_on_c_neq_a"]) >= 2
    assert any("hofman" in c or "maldacena" in c for c in _RES["would_unlock_on_c_neq_a"])


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "c-a degeneracy" in f
    assert "resolve c != a" in f or "resolving it" in f
    assert "highest-impact" in f or "highest-leverage" in f
    sc = _RES["honest_scope"].lower()
    assert "reasoned highest-impact judgement" in sc or "not a proven optimum" in sc
    assert "characterizes the basis, not the theory" in sc or "method / meta result" in sc
