"""Tests for the engine validity-scope layer (v1.59)."""

from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.causal_set import CausalSet
from itb.frameworks.group_field_theory import GroupFieldTheory
from itb.frameworks.horava_lifshitz import HoravaLifshitz
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.scope import engine_validity


def test_local_lorentz_frameworks_in_scope():
    for fw in (StringTreeEFT(), AsymptoticSafety(), GroupFieldTheory()):
        v = engine_validity(fw)
        assert v.in_scope and not v.violations


def test_horava_lifshitz_out_of_scope_lorentz():
    v = engine_validity(HoravaLifshitz())
    assert not v.in_scope
    assert any("Lorentz" in s for s in v.violations)


def test_causal_set_out_of_scope_locality():
    v = engine_validity(CausalSet())
    assert not v.in_scope
    assert any("locality" in s for s in v.violations)


def test_emergent_gravity_out_of_scope_fundamental():
    from itb.frameworks.emergent_gravity import EmergentGravity
    v = engine_validity(EmergentGravity())
    assert not v.in_scope
    assert any("fundamental" in s for s in v.violations)


def test_in_scope_note_is_clear():
    assert "in scope" in engine_validity(StringTreeEFT()).note
    assert "OUT OF SCOPE" in engine_validity(HoravaLifshitz()).note
