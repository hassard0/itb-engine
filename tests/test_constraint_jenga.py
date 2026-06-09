"""Tests for constraint Jenga (irreplaceability map) -- v1.93."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import constraint_jenga as cj


def test_string_framework_is_full_island():
    """A known survivor (string tree-EFT) satisfies every theoretical constraint
    -> its bitmask is the full mask (the island is non-empty)."""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    fb = cj._bits_of(StringTreeEFT().encode())
    assert fb == cj._FULL


def test_volume_without_redundant_constraint_unchanged():
    """If a constraint c is satisfied by every island point, removing it doesn't
    change the island (synthetic): bits all == FULL -> volume w/o c == V0."""
    full = cj._FULL
    bits = np.array([full, full, full], dtype=np.uint64)
    V0 = int((bits == full).sum())
    j = 0
    maskj = np.uint64(1) << np.uint64(j)
    Vj = int(((bits | maskj) == full).sum())
    assert Vj == V0


def test_volume_grows_when_removing_a_binding_constraint():
    """A sample that fails ONLY constraint j re-enters the island when j is removed."""
    full = cj._FULL
    j = 3
    maskj = np.uint64(1) << np.uint64(j)
    almost = full & ~maskj                       # all bits set except j
    bits = np.array([full, almost], dtype=np.uint64)
    V0 = int((bits == full).sum())               # 1
    Vj = int(((bits | maskj) == full).sum())     # 2 (the 'almost' point re-enters)
    assert V0 == 1 and Vj == 2
