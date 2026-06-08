"""Tests for the CEMZ graviton-causality bound (v1.61)."""

import math
import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.cemz_causality import CEMZCausality
from itb.frameworks.horava_lifshitz import HoravaLifshitz
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.theory import Theory


def test_class_and_citation():
    c = CEMZCausality()
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE
    assert "Camanho" in c.citation


def test_string_passes_comfortably():
    # string: |g_R3|=0.15 <= 0.8*sqrt(0.5*0.2)=0.8*0.316=0.253
    r = CEMZCausality(kappa=0.8).evaluate(StringTreeEFT().encode())
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.8 * math.sqrt(0.5 * 0.2) - 0.15, abs=1e-6)


def test_bites_large_cubic_horava():
    # HL: |g_R3|=0.40 vs 0.8*sqrt(0.5*0.45)=0.8*0.474=0.379 -> fails
    assert CEMZCausality(kappa=0.8).evaluate(HoravaLifshitz().encode()).satisfied is False


def test_tighter_kappa_bites_lqg():
    from itb.frameworks.lqg_induced import LQGInduced
    # LQG g_R3=0.30 vs sqrt(0.6*0.3)=0.424; kappa=0.8 -> 0.339 pass; kappa=0.6 -> 0.255 fail
    assert CEMZCausality(kappa=0.8).evaluate(LQGInduced().encode()).satisfied is True
    assert CEMZCausality(kappa=0.6).evaluate(LQGInduced().encode()).satisfied is False


def test_negative_couplings_violate():
    r = CEMZCausality().evaluate(Theory(coefficients={"g_4": -0.1, "g_R2": 0.2, "g_R3": 0.1}))
    assert r.satisfied is False
