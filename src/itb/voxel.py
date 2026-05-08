"""3D voxel sweep over (g_4, g_6, g_R2). The allowed region in 3D is a
volume; we represent it as a boolean voxel grid and provide slicing.

This is the move out of 2D toy projections into the actual 3D theory space
the engine is now defined on. Slices reveal how mixed positivity bounds
(which couple g_4, g_6, g_R2) carve the 3D volume."""

from dataclasses import dataclass

import numpy as np

from itb.constraints.base import Constraint
from itb.engine import check
from itb.theory import Theory


@dataclass
class VoxelResult:
    axes: dict[str, np.ndarray]    # ordered: x_param -> values, y_param -> values, z_param -> values
    feasibility_voxels: np.ndarray  # bool, shape (nx, ny, nz)
    binding_class_voxels: np.ndarray  # str grid


def voxel_sweep_3d(
    x_param: str, x_range: tuple[float, float], x_steps: int,
    y_param: str, y_range: tuple[float, float], y_steps: int,
    z_param: str, z_range: tuple[float, float], z_steps: int,
    constraints: list[Constraint],
    fixed_coefficients: dict[str, float] | None = None,
) -> VoxelResult:
    fixed = dict(fixed_coefficients or {})
    x_values = np.linspace(x_range[0], x_range[1], x_steps)
    y_values = np.linspace(y_range[0], y_range[1], y_steps)
    z_values = np.linspace(z_range[0], z_range[1], z_steps)
    feasibility = np.zeros((x_steps, y_steps, z_steps), dtype=bool)
    bclass = np.full((x_steps, y_steps, z_steps), "", dtype=object)
    for i, x in enumerate(x_values):
        for j, y in enumerate(y_values):
            for k, z in enumerate(z_values):
                coefficients = dict(fixed)
                coefficients[x_param] = float(x)
                coefficients[y_param] = float(y)
                coefficients[z_param] = float(z)
                report = check(Theory(coefficients=coefficients), constraints)
                feasibility[i, j, k] = report.feasible
                if report.binding_class is not None:
                    bclass[i, j, k] = report.binding_class
    return VoxelResult(
        axes={x_param: x_values, y_param: y_values, z_param: z_values},
        feasibility_voxels=feasibility,
        binding_class_voxels=bclass,
    )


def slice_voxel(
    result: VoxelResult,
    fixed_axis: str,
    fixed_value: float,
) -> dict:
    axes_keys = list(result.axes.keys())
    if fixed_axis not in axes_keys:
        raise ValueError(f"unknown axis: {fixed_axis}")
    idx = int(np.argmin(np.abs(result.axes[fixed_axis] - fixed_value)))
    axis_idx = axes_keys.index(fixed_axis)
    feas_slice = np.take(result.feasibility_voxels, indices=idx, axis=axis_idx)
    bclass_slice = np.take(result.binding_class_voxels, indices=idx, axis=axis_idx)
    other_keys = [k for k in axes_keys if k != fixed_axis]
    return {
        "fixed_axis": fixed_axis,
        "fixed_value": float(result.axes[fixed_axis][idx]),
        "x_param": other_keys[0],
        "x_values": result.axes[other_keys[0]],
        "y_param": other_keys[1],
        "y_values": result.axes[other_keys[1]],
        "feasibility_grid": feas_slice,
        "binding_class_grid": bclass_slice,
    }
