"""Tests for the Godel test (internal-consistency audit) -- v1.87."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import godel_test as gt


def _bits_from_rows(rows):
    """rows: list of per-sample satisfied-index lists -> uint64 bit array."""
    out = np.zeros(len(rows), dtype=np.uint64)
    for i, r in enumerate(rows):
        b = np.uint64(0)
        for j in r:
            b |= np.uint64(1) << np.uint64(j)
        out[i] = b
    return out


def test_feasible_bitwise():
    # sample 0 satisfies {0,1}; sample 1 satisfies {1,2}; none satisfies {0,2}
    bits = _bits_from_rows([[0, 1], [1, 2]])
    assert gt.feasible(bits, [0, 1])
    assert gt.feasible(bits, [1])
    assert not gt.feasible(bits, [0, 2])      # no sample has both 0 and 2


def test_find_mus_minimal():
    """Constraints {0,1} are jointly infeasible (no sample satisfies both); the MUS
    of a larger infeasible start set should reduce to {0,1}."""
    # samples satisfy at most one of {0,1}; constraint 2 is always satisfiable
    bits = _bits_from_rows([[0, 2], [1, 2], [0, 2], [1, 2]])
    assert not gt.feasible(bits, [0, 1])
    core = gt.find_mus(bits, [0, 1, 2])
    assert sorted(core) == [0, 1]              # 2 deleted, {0,1} is the minimal core


def test_theoretical_stack_has_a_survivor():
    """A known framework satisfies every THEORETICAL constraint -> the stack is
    feasible (no internal contradiction)."""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    th = StringTreeEFT().encode()
    assert all(gt._ALL[j].evaluate(th).satisfied for j in range(gt._N_THEORY))


def test_data_constraints_are_separate():
    """The 4 data constraints are appended after the theoretical ones."""
    assert gt._N - gt._N_THEORY == 4
    data_names = {gt._NAMES[i] for i in range(gt._N_THEORY, gt._N)}
    assert "submm_gravity_yukawa_bound" in data_names
    assert "cosmic_birefringence_data" in data_names
