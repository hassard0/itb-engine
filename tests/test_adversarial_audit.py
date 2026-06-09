"""Tests for the adversarial self-audit (v1.97)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import adversarial_audit as aa


def test_popcount_and_full_mask():
    """unsat = ~bits & full_mask; popcount counts failed constraints."""
    nc = aa._NC
    full = (np.uint64(1) << np.uint64(nc)) - np.uint64(1)
    # a sample satisfying all -> bits == full -> unsat == 0 -> popcount 0
    bits = np.array([full], dtype=np.uint64)
    unsat = (~bits) & full
    pc = sum(int((unsat[0] >> np.uint64(k)) & np.uint64(1)) for k in range(nc))
    assert pc == 0


def test_single_failure_detected():
    """A bitmask missing exactly one bit -> failure multiplicity 1 (near-miss)."""
    nc = aa._NC
    full = (np.uint64(1) << np.uint64(nc)) - np.uint64(1)
    j = 5
    bits = full & ~(np.uint64(1) << np.uint64(j))          # all set except bit j
    unsat = (~bits) & full
    pc = sum(int((unsat >> np.uint64(k)) & np.uint64(1)) for k in range(nc))
    assert pc == 1
    # the failed constraint is j
    failed = [k for k in range(nc) if (unsat >> np.uint64(k)) & np.uint64(1)]
    assert failed == [j]


def test_string_framework_passes_all():
    """A survivor (the island is non-empty) -> bitmask is full (multiplicity 0)."""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    th = StringTreeEFT().encode()
    assert all(c.evaluate(th).satisfied for c in aa._STACK)
