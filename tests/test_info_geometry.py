"""Tests for the information-geometry curvature map (v2.06)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import info_geometry as ig


def test_fisher_metric_symmetric_psd():
    E, F, G = ig._metric(0.21, 0.23)
    M = np.array([[E, F], [F, G]])
    assert np.allclose(M, M.T)
    assert np.all(np.linalg.eigvalsh(M) >= -1e-9)      # PSD


def test_curvature_rises_toward_small_gC():
    """|R|-driving metric component blows up as g_C -> 0 (a/c = g_R2/g_C diverges)."""
    E_small, _, _ = ig._metric(0.21, 0.05)
    E_big, _, _ = ig._metric(0.21, 0.45)
    assert E_small > E_big                              # metric degenerates at small g_C


def test_flat_metric_zero_curvature():
    """A constant (flat) metric has zero Gaussian curvature (sanity for the Brioschi path)."""
    # ds^2 = dx^2 + dy^2 -> all derivatives zero -> K = 0
    E = F = G = None
    e, f, g = 1.0, 0.0, 1.0
    M1 = np.array([[0.0, 0.0, 0.0], [0.0, e, f], [0.0, f, g]])
    M2 = np.array([[0.0, 0.0, 0.0], [0.0, e, f], [0.0, f, g]])
    det = e * g - f ** 2
    K = (np.linalg.det(M1) - np.linalg.det(M2)) / det ** 2
    assert K == 0.0
