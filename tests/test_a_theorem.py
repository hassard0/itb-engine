"""Tests for the a-theorem sign bound (v1.70).

Correctness of the constraint itself, plus a guard documenting the empirically
established fact that it is REDUNDANT with the corrected stack in the current
toy basis (no negative-g_R2 point survives the existing constraints).
"""
import sys
from pathlib import Path

import pytest

from itb.constraints.a_theorem import ATheoremMonotonicity
from itb.theory import Theory

# make experiments/stack.py importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))


def test_sign_bound():
    c = ATheoremMonotonicity()
    assert c.evaluate(Theory(coefficients={"g_R2": 0.3})).satisfied
    assert c.evaluate(Theory(coefficients={"g_R2": 0.0})).satisfied
    assert not c.evaluate(Theory(coefficients={"g_R2": -0.01})).satisfied


def test_margin_is_gR2():
    c = ATheoremMonotonicity()
    r = c.evaluate(Theory(coefficients={"g_R2": 0.17}))
    assert r.margin == pytest.approx(0.17)


def test_gradient():
    c = ATheoremMonotonicity()
    g = c.gradient(Theory(coefficients={"g_R2": 0.2, "g_4": 0.5}))
    assert g["g_R2"] == 1.0
    assert g["g_4"] == 0.0


def test_redundant_with_corrected_stack():
    """No negative-g_R2 point survives the existing corrected stack at a
    string-like matter point -> the a-theorem adds no information here.
    (This is the v1.70 result; the test pins it so a future basis change that
    makes the bound load-bearing will visibly break this guard.)"""
    from stack import build_stack

    stack = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    base = {"g_4": 0.5, "g_6": 0.4, "g_8": 0.4,
            "g_R2_parity": 0.0, "g_R3_parity": 0.0}
    found_feasible_negative = False
    for i in range(-10, 0):            # g_R2 in [-0.5, -0.05]
        for j in range(0, 11):         # g_R3 in [0, 0.5]
            coeffs = dict(base)
            coeffs["g_R2"] = i * 0.05
            coeffs["g_R3"] = j * 0.05
            th = Theory(coefficients=coeffs)
            if all(c.evaluate(th).satisfied for c in stack):
                found_feasible_negative = True
    assert not found_feasible_negative
