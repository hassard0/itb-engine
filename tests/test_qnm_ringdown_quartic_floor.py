"""Tests for the ringdown quartic-curvature floor result (v2.336)."""

from experiments.qnm_ringdown_quartic_floor import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_requires_nonzero_quartic():
    assert _RES["consistency_checks"]["constructed_requires_nonzero_quartic_curvature"] is True
    assert _RES["constructed_gR4_floor"] > 0


def test_gR4_floor_is_moment_tower_value():
    # g_R3^2 / g_R2 for the constructed theory
    assert abs(_RES["constructed_gR4_floor"] - 0.09 ** 2 / 0.193) < 1e-3


def test_constructed_has_smallest_nonzero_floor():
    rows = _RES["gR4_floors"]
    hd = [r for r in rows if r["theory"] != "pure_gr"]
    smallest = min(hd, key=lambda r: r["gR4_floor"])
    assert smallest["theory"] == "engine_constructed"
    # pure GR sits at exactly zero
    pg = next(r for r in rows if r["theory"] == "pure_gr")
    assert pg["gR4_floor"] == 0.0


def test_ordering_constructed_below_community():
    floors = {r["theory"]: r["gR4_floor"] for r in _RES["gR4_floors"]}
    for fw in ("asymptotic_safety", "cdt", "string_tree_eft", "lqg_induced"):
        assert floors["engine_constructed"] < floors[fw]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "ringdown" in f
    assert "smallest" in f or "mildest" in f
    assert "cp-even" in f
    sc = _RES["honest_scope"].lower()
    assert "floor is rigorous" in sc or "rigorous and exact" in sc
    assert "schematic" in sc
    assert "toy basis" in sc
