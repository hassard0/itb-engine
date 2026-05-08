"""Region: a feasibility grid with axis metadata and binding-constraint info,
supporting set-algebra (intersection / union / difference / complement).

Used to ask questions like "what region is excluded by A but allowed by B?" —
the kind of diagnostic that turns the engine from yes/no into a physics tool.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class Region:
    feasibility: np.ndarray
    axes: dict[str, np.ndarray]
    binding: dict

    def _check_axes(self, other: "Region") -> None:
        if set(self.axes.keys()) != set(other.axes.keys()):
            raise ValueError(f"axis mismatch: {self.axes.keys()} vs {other.axes.keys()}")
        for k, v in self.axes.items():
            if not np.array_equal(v, other.axes[k]):
                raise ValueError(f"axis {k!r} values differ between regions")

    def __and__(self, other: "Region") -> "Region":
        self._check_axes(other)
        return Region(
            feasibility=self.feasibility & other.feasibility,
            axes={k: v.copy() for k, v in self.axes.items()},
            binding={},
        )

    def __or__(self, other: "Region") -> "Region":
        self._check_axes(other)
        return Region(
            feasibility=self.feasibility | other.feasibility,
            axes={k: v.copy() for k, v in self.axes.items()},
            binding={},
        )

    def __sub__(self, other: "Region") -> "Region":
        self._check_axes(other)
        return Region(
            feasibility=self.feasibility & ~other.feasibility,
            axes={k: v.copy() for k, v in self.axes.items()},
            binding={},
        )

    def __invert__(self) -> "Region":
        return Region(
            feasibility=~self.feasibility,
            axes={k: v.copy() for k, v in self.axes.items()},
            binding={},
        )


def region_from_sweep(sweep) -> Region:
    """Build a Region from a SweepResult, retaining binding info."""
    return Region(
        feasibility=sweep.feasibility_grid.copy(),
        axes={
            sweep.x_param: sweep.x_values.copy(),
            sweep.y_param: sweep.y_values.copy(),
        },
        binding={
            "grid": sweep.binding_grid.copy(),
            "class_grid": sweep.binding_class_grid.copy(),
        },
    )
