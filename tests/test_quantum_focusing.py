import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.quantum_focusing import QuantumFocusingConjecture
from itb.theory import Theory


def test_class_b_information():
    c = QuantumFocusingConjecture()
    assert c.constraint_class is ConstraintClass.B_INFORMATION
    assert "Bousso" in c.citation


def test_qfc_satisfied_when_matter_coupling_dominates():
    c = QuantumFocusingConjecture(alpha=0.5)
    # g_4=0.5, g_R2=0.2: 0.5*0.2 - 0.5*0.04 = 0.10 - 0.02 = 0.08 ✓
    r = c.evaluate(Theory(coefficients={"g_4": 0.5, "g_R2": 0.2}))
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.08)


def test_qfc_violated_when_g_R2_dominates_matter():
    c = QuantumFocusingConjecture(alpha=0.5)
    # g_4=0.1, g_R2=0.5: 0.05 - 0.125 = -0.075
    r = c.evaluate(Theory(coefficients={"g_4": 0.1, "g_R2": 0.5}))
    assert r.satisfied is False


def test_qfc_trivially_satisfied_at_pure_gr():
    c = QuantumFocusingConjecture()
    r = c.evaluate(Theory(coefficients={"g_4": 0.0, "g_R2": 0.0}))
    assert r.satisfied is True
    assert r.margin == 0.0


def test_all_four_frameworks_pass_qfc():
    """QFC at α=0.5 should be satisfied by all current toy frameworks."""
    from itb.frameworks.asymptotic_safety import AsymptoticSafety
    from itb.frameworks.lqg_induced import LQGInduced
    from itb.frameworks.pure_gr import PureGR
    from itb.frameworks.string_tree_eft import StringTreeEFT

    c = QuantumFocusingConjecture(alpha=0.5)
    for fw_cls in (PureGR, StringTreeEFT, AsymptoticSafety, LQGInduced):
        theory = fw_cls().encode()
        assert c.evaluate(theory).satisfied is True, fw_cls.__name__
