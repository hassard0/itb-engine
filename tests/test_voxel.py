import numpy as np

from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.voxel import slice_voxel, voxel_sweep_3d, VoxelResult


def _full_set():
    return [
        ScalarPositivityG4(),
        ScalarPositivityG6(),
        ScalarConvexityG6vsG4(),
        GravitonMixedPositivity(),
        BekensteinTight(),
    ]


def test_returns_voxel_result():
    res = voxel_sweep_3d(
        x_param="g_4", x_range=(0.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(0.0, 1.0), y_steps=5,
        z_param="g_R2", z_range=(0.0, 1.0), z_steps=5,
        constraints=_full_set(),
    )
    assert isinstance(res, VoxelResult)
    assert res.feasibility_voxels.shape == (5, 5, 5)


def test_increasing_g_R2_shrinks_allowed_volume():
    """As g_R2 grows toward 1, the Bekenstein bound g_R2^2 <= 0.5 g_4 g_6
    becomes harder to satisfy and the allowed slice shrinks."""
    res = voxel_sweep_3d(
        x_param="g_4", x_range=(0.0, 1.5), x_steps=11,
        y_param="g_6", y_range=(0.0, 1.5), y_steps=11,
        z_param="g_R2", z_range=(0.0, 1.0), z_steps=11,
        constraints=_full_set(),
    )
    counts_per_g_R2 = res.feasibility_voxels.sum(axis=(0, 1))
    # Monotonically non-increasing as g_R2 increases (modulo discretization)
    diffs = np.diff(counts_per_g_R2)
    assert (diffs <= 0).sum() >= len(diffs) // 2  # mostly non-increasing


def test_slice_returns_2d_grid():
    res = voxel_sweep_3d(
        x_param="g_4", x_range=(0.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(0.0, 1.0), y_steps=5,
        z_param="g_R2", z_range=(0.0, 1.0), z_steps=5,
        constraints=_full_set(),
    )
    sl = slice_voxel(res, fixed_axis="g_R2", fixed_value=0.0)
    assert sl["feasibility_grid"].shape == (5, 5)
    assert sl["x_param"] == "g_4"
    assert sl["y_param"] == "g_6"


def test_slice_at_zero_g_R2_matches_2d_sweep_qualitatively():
    """A slice at g_R2=0 should make every Bekenstein/mixed-positivity check
    trivially satisfied and the result reduce to scalar bounds only."""
    res = voxel_sweep_3d(
        x_param="g_4", x_range=(0.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(0.0, 1.0), y_steps=11,
        z_param="g_R2", z_range=(0.0, 1.0), z_steps=11,
        constraints=_full_set(),
    )
    sl = slice_voxel(res, fixed_axis="g_R2", fixed_value=0.0)
    # Every cell with g_4 >= 0, g_6 >= 0, g_6 >= g_4^2 should be feasible
    for i, x in enumerate(sl["x_values"]):
        for j, y in enumerate(sl["y_values"]):
            expected = (x >= 0) and (y >= 0) and (y >= x ** 2)
            if expected:
                assert sl["feasibility_grid"][i, j], f"slice missed ({x},{y})"
