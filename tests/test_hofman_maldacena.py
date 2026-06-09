"""Tests for the Hofman-Maldacena a/c wedge (v1.71)."""
import sys
from pathlib import Path

import pytest

from itb.constraints.hofman_maldacena import HofmanMaldacenaWedge
from itb.theory import Theory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))


def _ev(gR2, gC):
    return HofmanMaldacenaWedge().evaluate(
        Theory(coefficients={"g_R2": gR2, "g_C": gC}))


def test_center_ac1_passes():
    """a = c (a/c = 1, holographic default) sits inside the wedge."""
    r = _ev(0.2, 0.2)
    assert r.satisfied
    assert r.details["a_over_c"] == pytest.approx(1.0)


def test_default_gC_is_gR2():
    """Missing g_C falls back to g_R2 (a/c = 1)."""
    r = HofmanMaldacenaWedge().evaluate(Theory(coefficients={"g_R2": 0.3}))
    assert r.satisfied
    assert r.details["a_over_c"] == pytest.approx(1.0)


def test_lower_edge_saturated():
    """a/c = 1/3 (g_C = 3 g_R2) is the scalar floor: saturated, still satisfied."""
    r = _ev(0.1, 0.3)
    assert r.details["a_over_c"] == pytest.approx(1.0 / 3.0)
    assert r.margin == pytest.approx(0.0, abs=1e-12)
    assert r.satisfied


def test_upper_edge_saturated():
    """a/c = 31/18 (Maxwell ceiling): saturated, still satisfied."""
    gC = 0.18
    gR2 = (31.0 / 18.0) * gC
    r = _ev(gR2, gC)
    assert r.details["a_over_c"] == pytest.approx(31.0 / 18.0)
    assert r.margin == pytest.approx(0.0, abs=1e-9)
    assert r.satisfied


def test_above_ceiling_excluded():
    """a/c = 4 (g_R2=0.2, g_C=0.05) is above 31/18 -> excluded."""
    r = _ev(0.2, 0.05)
    assert r.details["a_over_c"] == pytest.approx(4.0)
    assert not r.satisfied
    assert r.details["binding"].startswith("upper")


def test_below_floor_excluded():
    """a/c = 0.2 (g_R2=0.1, g_C=0.5) is below 1/3 -> excluded."""
    r = _ev(0.1, 0.5)
    assert not r.satisfied
    assert r.details["binding"].startswith("lower")


def test_negative_c_excluded():
    """c = g_C <= 0 violates unitarity."""
    assert not _ev(0.2, -0.1).satisfied


def test_pure_gr_vacuous():
    """No curvature-squared sector (g_R2 = g_C = 0): bound inapplicable, passes."""
    r = HofmanMaldacenaWedge().evaluate(Theory(coefficients={"g_R2": 0.0}))
    assert r.satisfied
    assert r.details["binding"] == "none"


def test_wedge_bites_witness():
    """The witness point is feasible without the wedge but excluded with it,
    and the wedge is the SOLE excluder."""
    from stack import build_stack

    base = {"g_4": 0.5, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.2, "g_R3": 0.15,
            "g_R2_parity": 0.0, "g_R3_parity": 0.0, "g_C": 0.05}
    th = Theory(coefficients=base)
    new = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    old = [c for c in new if c.name != "hofman_maldacena_wedge"]
    assert all(c.evaluate(th).satisfied for c in old)          # old: feasible
    failed = [c.name for c in new if not c.evaluate(th).satisfied]
    assert failed == ["hofman_maldacena_wedge"]                # new: only wedge
