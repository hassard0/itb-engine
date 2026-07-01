"""Tests for the infinite log-convex curvature tower swing (v2.375)."""

from experiments.qnm_infinite_curvature_tower import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_log_convex_ratio():
    assert abs(_RES["log_convex_ratio_r"] - 0.09 / 0.193) < 1e-3
    assert 0.0 < _RES["log_convex_ratio_r"] < 1.0     # positive and convergent


def test_geometric_floor_all_positive_and_monotone():
    tower = _RES["geometric_floor_tower"]
    vals = list(tower.values())
    assert all(v > 0 for v in vals)                    # no truncation
    assert all(vals[i] > vals[i + 1] for i in range(len(vals) - 1))   # geometric decay (r<1)


def test_infinite_no_truncation():
    assert _RES["consistency_checks"]["infinite_tower_no_finite_truncation"] is True
    assert _RES["higher_derivative_expansion_converges"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "every order" in f
    assert "string-like" in f
    assert "log-convex" in f
    assert "not a finite-derivative" in f or "not a truncated" in f or "opposite of a truncated" in f
    sc = _RES["honest_scope"].lower()
    assert "rigorous given" in sc or "rigorous-given" in sc
    assert "toy" in sc
    assert "g_r5 and beyond are not engine couplings" in sc or "not engine couplings" in sc
