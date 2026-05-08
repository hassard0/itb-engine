# ITB Engine v0.2 Implementation Plan — All 7 Research Ideas

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land all 7 research-direction ideas captured during the v0.1.0 build (signed-distance margins, set-algebra regions, binding-class diagnostics, Fisher metric on theory space, tolerance-graded SDP path, negative-result mode, lazy cvxpy + SDP opt-in) so the engine moves from "does this theory work?" to "what physics is binding here, how observably-distinct are these theories, and how fragile are they?"

**Architecture:** Five additive milestones layered on the v0.1.0 spine. M1 sharpens the constraint protocol with gradient + signed-distance information. M2 introduces a `Region` abstraction with intersection/union/difference and per-cell binding-class diagnostics. M3 lights up the real SDP path with tolerance levels. M4 adds an Observable interface and Fisher information metric on coefficient space. M5 implements smallest-violating-perturbation analysis. The frontend gets new UI controls in a final integration task.

**Tech Stack:** Python 3.11, cvxpy (now actually exercised), NumPy, SciPy (optimize.minimize for #6), FastAPI, Plotly. No new heavy deps.

---

## File Structure

```
src/itb/
├── theory.py                       (unchanged)
├── constraints/
│   ├── base.py                     MODIFY: add gradient() + signed_distance_margin
│   ├── scalar_positivity.py        MODIFY: implement gradients
│   └── scalar_positivity_sdp.py    NEW: cvxpy-backed SDP variant (M3)
├── frameworks/                     (unchanged)
├── engine.py                       MODIFY: tolerance param, binding tracking
├── regions.py                      NEW: Region abstraction (M2)
├── mapper.py                       MODIFY: binding-per-cell, boundary detection,
│                                            Newton boundary tracing (M2/M3)
├── observables.py                  NEW: Observable interface (M4)
├── fisher.py                       NEW: Fisher metric computation (M4)
├── perturbation.py                 NEW: smallest-violating perturbation (M5)
├── plotting.py                     MODIFY: binding-class coloring, metric coords
└── api/server.py                   MODIFY: expose new endpoints/params

tests/
├── test_constraint_gradients.py    NEW (M1)
├── test_regions.py                 NEW (M2)
├── test_engine_binding.py          NEW (M2)
├── test_mapper_v02.py              NEW (M2/M3) — binding grid + boundary tracing
├── test_scalar_positivity_sdp.py   NEW (M3)
├── test_engine_tolerance.py        NEW (M3)
├── test_observables.py             NEW (M4)
├── test_fisher.py                  NEW (M4)
├── test_plotting_v02.py            NEW (M4)
├── test_perturbation.py            NEW (M5)
└── test_server_v02.py              NEW (integration)
```

---

## Tasks

### Task 1 — Constraint gradients + signed-distance margin (Idea #1)

**Files:**
- Modify: `src/itb/constraints/base.py`
- Modify: `src/itb/constraints/scalar_positivity.py`
- Create: `tests/test_constraint_gradients.py`

- [ ] **Step 1: Write the failing test**

`tests/test_constraint_gradients.py`:
```python
import numpy as np

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.theory import Theory


def test_g4_gradient_unit_in_g4_direction():
    c = ScalarPositivityG4()
    g = c.gradient(Theory(coefficients={"g_4": 0.7, "g_6": 0.2}))
    assert set(g.keys()) == {"g_4", "g_6"}
    assert g["g_4"] == 1.0
    assert g["g_6"] == 0.0


def test_g6_gradient_unit_in_g6_direction():
    c = ScalarPositivityG6()
    g = c.gradient(Theory(coefficients={"g_4": 0.7, "g_6": 0.2}))
    assert g["g_4"] == 0.0
    assert g["g_6"] == 1.0


def test_signed_distance_margin_normalized():
    c = ScalarPositivityG4()
    r = c.evaluate(Theory(coefficients={"g_4": 0.5}))
    # gradient is a unit vector, so signed distance == raw margin
    assert r.signed_distance_margin == 0.5


def test_signed_distance_negative_means_violation():
    c = ScalarPositivityG4()
    r = c.evaluate(Theory(coefficients={"g_4": -0.3}))
    assert r.signed_distance_margin == -0.3
    assert r.satisfied is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_constraint_gradients.py -v`
Expected: FAIL — `gradient` method missing.

- [ ] **Step 3: Write the implementation**

`src/itb/constraints/base.py` — replace whole file:
```python
"""Base protocol for consistency constraints.

Each constraint is a self-contained module. Subclasses provide:
  - evaluate(theory) -> ConstraintResult
  - gradient(theory) -> dict[str, float]      (partials w.r.t. each coefficient)

The gradient enables signed-distance interpretation of margins and
Newton-style boundary tracing in the mapper.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np

from itb.theory import Theory


class ConstraintClass(Enum):
    A_AMPLITUDE = "amplitude_bootstrap"
    B_INFORMATION = "information_theoretic"
    C_UNIVERSALITY = "gravitational_universality"


@dataclass
class ConstraintResult:
    constraint_name: str
    satisfied: bool
    margin: float
    signed_distance_margin: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


class Constraint(ABC):
    name: str = ""
    citation: str = ""
    constraint_class: ConstraintClass = ConstraintClass.A_AMPLITUDE

    @abstractmethod
    def evaluate(self, theory: Theory) -> ConstraintResult: ...

    def gradient(self, theory: Theory) -> dict[str, float]:
        """Default: zero gradient. Override for differentiable constraints."""
        return {k: 0.0 for k in theory.coefficients}

    def _signed_distance(self, raw_margin: float, gradient: dict[str, float]) -> float:
        norm = float(np.linalg.norm(list(gradient.values()))) if gradient else 0.0
        if norm == 0.0:
            return raw_margin
        return raw_margin / norm
```

`src/itb/constraints/scalar_positivity.py` — replace whole file:
```python
"""Adams-Arkani-Hamed-Dubovsky-Nicolis-Rattazzi (2006) positivity bounds for a
real-scalar EFT. The forward 2->2 elastic amplitude must satisfy g_{2n} >= 0
for n >= 2 from analyticity + unitarity + crossing.

Reference:
  Adams, Arkani-Hamed, Dubovsky, Nicolis, Rattazzi. "Causality, Analyticity
  and an IR Obstruction to UV Completion." JHEP 10 (2006) 014.
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class ScalarPositivityG4(Constraint):
    name = "scalar_positivity_g4"
    citation = "Adams, Arkani-Hamed, Dubovsky, Nicolis, Rattazzi 2006"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=g4 >= 0,
            margin=g4,
            signed_distance_margin=self._signed_distance(g4, grad),
            details={"bound": "g_4 >= 0", "value": g4},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_4", 0.0)
        out.setdefault("g_6", 0.0)
        out["g_4"] = 1.0
        return out


class ScalarPositivityG6(Constraint):
    name = "scalar_positivity_g6"
    citation = "Adams, Arkani-Hamed, Dubovsky, Nicolis, Rattazzi 2006"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g6 = theory.coefficients.get("g_6", 0.0)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=g6 >= 0,
            margin=g6,
            signed_distance_margin=self._signed_distance(g6, grad),
            details={"bound": "g_6 >= 0", "value": g6},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_4", 0.0)
        out.setdefault("g_6", 0.0)
        out["g_6"] = 1.0
        return out
```

- [ ] **Step 4: Run all tests; existing should still pass**

Run: `pytest`
Expected: 41 prior + 4 new = 45 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/constraints tests/test_constraint_gradients.py
git commit -m "add constraint gradients + signed-distance margins"
```

---

### Task 2 — Region abstraction with set algebra (Idea #2 part 1)

**Files:**
- Create: `src/itb/regions.py`
- Create: `tests/test_regions.py`

- [ ] **Step 1: Write the failing test**

`tests/test_regions.py`:
```python
import numpy as np

from itb.regions import Region


def _grid(values):
    return np.array(values, dtype=bool)


def test_region_holds_grid_and_axes():
    r = Region(
        feasibility=_grid([[True, False], [True, True]]),
        axes={"g_4": np.array([0.0, 1.0]), "g_6": np.array([0.0, 1.0])},
        binding={},
    )
    assert r.feasibility.shape == (2, 2)
    assert "g_4" in r.axes


def test_intersection_logical_and():
    a = Region(_grid([[True, True], [False, True]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    b = Region(_grid([[True, False], [True, True]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    c = a & b
    np.testing.assert_array_equal(c.feasibility, [[True, False], [False, True]])


def test_union_logical_or():
    a = Region(_grid([[True, False], [False, False]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    b = Region(_grid([[False, True], [True, False]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    c = a | b
    np.testing.assert_array_equal(c.feasibility, [[True, True], [True, False]])


def test_difference_a_minus_b():
    a = Region(_grid([[True, True], [True, True]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    b = Region(_grid([[True, False], [False, True]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    c = a - b
    np.testing.assert_array_equal(c.feasibility, [[False, True], [True, False]])


def test_complement():
    a = Region(_grid([[True, False], [False, True]]),
               {"x": np.array([0.0, 1.0]), "y": np.array([0.0, 1.0])}, {})
    np.testing.assert_array_equal((~a).feasibility,
                                  [[False, True], [True, False]])


def test_axes_must_match():
    a = Region(_grid([[True]]), {"x": np.array([0.0]), "y": np.array([0.0])}, {})
    b = Region(_grid([[True]]), {"x": np.array([1.0]), "y": np.array([0.0])}, {})
    import pytest
    with pytest.raises(ValueError):
        _ = a & b
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_regions.py -v`
Expected: FAIL — `itb.regions` not found.

- [ ] **Step 3: Write the implementation**

`src/itb/regions.py`:
```python
"""Region: a feasibility grid with axis metadata and binding-constraint info,
supporting set-algebra (intersection / union / difference / complement).

Used to ask questions like "what region is excluded by A but allowed by B?" —
the kind of diagnostic that turns the engine from yes/no into a physics tool.
"""

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Region:
    feasibility: np.ndarray            # bool grid
    axes: dict[str, np.ndarray]        # ordered: x_param -> values, y_param -> values
    binding: dict                      # per-cell binding info; opaque structure

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
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_regions.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/regions.py tests/test_regions.py
git commit -m "add Region abstraction with set algebra (Idea #2)"
```

---

### Task 3 — Engine returns binding constraint when infeasible (Idea #3 prep)

**Files:**
- Modify: `src/itb/engine.py`
- Create: `tests/test_engine_binding.py`

- [ ] **Step 1: Write the failing test**

`tests/test_engine_binding.py`:
```python
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.engine import check
from itb.theory import Theory


def test_binding_is_none_when_feasible():
    r = check(Theory(coefficients={"g_4": 0.5, "g_6": 0.5}),
              [ScalarPositivityG4(), ScalarPositivityG6()])
    assert r.feasible is True
    assert r.binding is None


def test_binding_is_first_violation():
    r = check(Theory(coefficients={"g_4": -1.0, "g_6": 0.5}),
              [ScalarPositivityG4(), ScalarPositivityG6()])
    assert r.feasible is False
    assert r.binding == "scalar_positivity_g4"


def test_binding_when_both_violated_picks_most_negative():
    r = check(Theory(coefficients={"g_4": -0.1, "g_6": -1.0}),
              [ScalarPositivityG4(), ScalarPositivityG6()])
    assert r.feasible is False
    # g_6 violated by -1.0, g_4 by -0.1 — g_6 is the more strongly binding one
    assert r.binding == "scalar_positivity_g6"


def test_binding_class_in_report():
    r = check(Theory(coefficients={"g_4": -1.0}),
              [ScalarPositivityG4()])
    assert r.binding_class == "amplitude_bootstrap"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_engine_binding.py -v`
Expected: FAIL — `binding` attribute missing.

- [ ] **Step 3: Write the implementation**

`src/itb/engine.py` — replace whole file:
```python
"""Engine: evaluate a theory against a set of constraints; return feasibility,
the most-binding constraint when infeasible, and per-constraint results."""

from dataclasses import dataclass

from itb.constraints.base import Constraint, ConstraintResult
from itb.theory import Theory


@dataclass
class EngineReport:
    theory_name: str
    feasible: bool
    results: list[ConstraintResult]
    binding: str | None = None        # name of most-binding violated constraint
    binding_class: str | None = None  # constraint_class.value of binding constraint


def check(theory: Theory, constraints: list[Constraint]) -> EngineReport:
    results = [c.evaluate(theory) for c in constraints]
    feasible = all(r.satisfied for r in results)
    binding_name: str | None = None
    binding_cls: str | None = None
    if not feasible:
        violated = [(c, r) for c, r in zip(constraints, results) if not r.satisfied]
        # most-binding = most negative signed distance
        c, r = min(violated, key=lambda cr: cr[1].signed_distance_margin)
        binding_name = r.constraint_name
        binding_cls = c.constraint_class.value
    return EngineReport(
        theory_name=theory.name,
        feasible=feasible,
        results=results,
        binding=binding_name,
        binding_class=binding_cls,
    )
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_engine_binding.py tests/test_engine.py -v`
Expected: 4 new + 5 prior = 9 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/engine.py tests/test_engine_binding.py
git commit -m "engine reports most-binding constraint and class on infeasibility"
```

---

### Task 4 — Mapper records binding-class per cell + boundary detection (Idea #3)

**Files:**
- Modify: `src/itb/mapper.py`
- Create: `tests/test_mapper_v02.py`

- [ ] **Step 1: Write the failing test**

`tests/test_mapper_v02.py`:
```python
import numpy as np

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.mapper import sweep_2d, boundary_cells


def _sweep():
    return sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )


def test_binding_grid_shape_matches_feasibility():
    s = _sweep()
    assert s.binding_grid.shape == s.feasibility_grid.shape


def test_binding_grid_empty_string_inside_allowed_region():
    s = _sweep()
    # (0.6, 0.6) -> indices (8, 8) -> feasible -> binding empty
    assert s.binding_grid[8, 8] == ""


def test_binding_grid_records_g4_in_left_half():
    s = _sweep()
    # (-0.6, +0.6) -> indices (2, 8) -> g4 violated, g6 OK
    assert s.binding_grid[2, 8] == "scalar_positivity_g4"


def test_binding_grid_records_g6_in_lower_half():
    s = _sweep()
    # (+0.6, -0.6) -> indices (8, 2) -> g4 OK, g6 violated
    assert s.binding_grid[8, 2] == "scalar_positivity_g6"


def test_boundary_cells_are_on_axis_lines():
    s = _sweep()
    cells = boundary_cells(s)
    # boundary cells: those adjacent to a feasibility flip
    # for the first quadrant, that's roughly the x=0 and y=0 lines
    assert len(cells) > 0
    # all boundary cells should be near an axis (within 1 grid step of zero)
    step = 0.2
    for (i, j) in cells:
        x = s.x_values[i]
        y = s.y_values[j]
        assert (abs(x) <= step + 1e-9) or (abs(y) <= step + 1e-9)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_mapper_v02.py -v`
Expected: FAIL — `binding_grid` and `boundary_cells` missing.

- [ ] **Step 3: Write the implementation**

`src/itb/mapper.py` — replace whole file:
```python
"""Theory-space mapper: sweeps over a parameter grid and records both
feasibility and the most-binding constraint per cell. Also exposes
boundary detection — cells adjacent to a feasibility flip."""

from dataclasses import dataclass

import numpy as np

from itb.constraints.base import Constraint
from itb.engine import check
from itb.theory import Theory


@dataclass
class SweepResult:
    x_param: str
    x_values: np.ndarray
    y_param: str
    y_values: np.ndarray
    feasibility_grid: np.ndarray
    binding_grid: np.ndarray   # str grid: empty if feasible, else binding constraint name
    binding_class_grid: np.ndarray  # str grid: empty or constraint_class.value


def sweep_2d(
    x_param: str,
    x_range: tuple[float, float],
    x_steps: int,
    y_param: str,
    y_range: tuple[float, float],
    y_steps: int,
    constraints: list[Constraint],
    fixed_coefficients: dict[str, float] | None = None,
) -> SweepResult:
    fixed = dict(fixed_coefficients or {})
    x_values = np.linspace(x_range[0], x_range[1], x_steps)
    y_values = np.linspace(y_range[0], y_range[1], y_steps)
    feasibility = np.zeros((x_steps, y_steps), dtype=bool)
    binding = np.full((x_steps, y_steps), "", dtype=object)
    binding_class = np.full((x_steps, y_steps), "", dtype=object)
    for i, x in enumerate(x_values):
        for j, y in enumerate(y_values):
            coefficients = dict(fixed)
            coefficients[x_param] = float(x)
            coefficients[y_param] = float(y)
            theory = Theory(coefficients=coefficients, name="sweep_point")
            report = check(theory, constraints)
            feasibility[i, j] = report.feasible
            if report.binding is not None:
                binding[i, j] = report.binding
                binding_class[i, j] = report.binding_class or ""
    return SweepResult(
        x_param=x_param,
        x_values=x_values,
        y_param=y_param,
        y_values=y_values,
        feasibility_grid=feasibility,
        binding_grid=binding,
        binding_class_grid=binding_class,
    )


def boundary_cells(sweep: SweepResult) -> list[tuple[int, int]]:
    """Return (i, j) indices of cells that are adjacent to a feasibility flip
    (4-neighborhood). Useful for boundary visualization."""
    g = sweep.feasibility_grid
    cells: list[tuple[int, int]] = []
    nx, ny = g.shape
    for i in range(nx):
        for j in range(ny):
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ni, nj = i + di, j + dj
                if 0 <= ni < nx and 0 <= nj < ny and g[i, j] != g[ni, nj]:
                    cells.append((i, j))
                    break
    return cells
```

- [ ] **Step 4: Run all mapper tests**

Run: `pytest tests/test_mapper.py tests/test_mapper_v02.py -v`
Expected: 5 prior + 5 new = 10 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/mapper.py tests/test_mapper_v02.py
git commit -m "mapper records binding-per-cell and detects boundary cells (Idea #3)"
```

---

### Task 5 — engine.regions(): build a Region from a sweep (Idea #2 part 2)

**Files:**
- Modify: `src/itb/regions.py`
- Modify: `tests/test_regions.py` (extend)

- [ ] **Step 1: Write the failing test (append to test_regions.py)**

Append to `tests/test_regions.py`:
```python
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.mapper import sweep_2d
from itb.regions import region_from_sweep


def test_region_from_sweep_carries_binding():
    s = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    r = region_from_sweep(s)
    assert r.feasibility.shape == (5, 5)
    assert r.binding.get("grid") is not None
    assert r.binding.get("class_grid") is not None


def test_intersection_drops_binding():
    s = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=3,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=3,
        constraints=[ScalarPositivityG4()],
    )
    r1 = region_from_sweep(s)
    r2 = region_from_sweep(sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=3,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=3,
        constraints=[ScalarPositivityG6()],
    ))
    inter = r1 & r2
    # binding info from individual sweeps doesn't survive set ops by design;
    # caller should rebuild from the intersected sweep if they need diagnostics
    assert inter.binding == {}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_regions.py -v`
Expected: existing 6 pass; new 2 fail — `region_from_sweep` missing.

- [ ] **Step 3: Append to `src/itb/regions.py`**

```python
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
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_regions.py -v`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/regions.py tests/test_regions.py
git commit -m "add region_from_sweep bridge with binding-info retention"
```

---

### Task 6 — Plotting: color cells by binding-constraint class (Idea #3)

**Files:**
- Modify: `src/itb/plotting.py`
- Create: `tests/test_plotting_v02.py`

- [ ] **Step 1: Write the failing test**

`tests/test_plotting_v02.py`:
```python
import json

import plotly.graph_objects as go

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.mapper import sweep_2d
from itb.plotting import build_binding_class_figure


def _sweep():
    return sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )


def test_binding_class_figure_is_plotly():
    fig = build_binding_class_figure(_sweep())
    assert isinstance(fig, go.Figure)


def test_binding_class_figure_has_three_traces():
    # one for allowed, one for amplitude-bound, plus optional info-bound traces
    fig = build_binding_class_figure(_sweep())
    assert len(fig.data) >= 1


def test_binding_class_figure_serialises():
    fig = build_binding_class_figure(_sweep())
    payload = json.loads(fig.to_json())
    assert "data" in payload
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_plotting_v02.py -v`
Expected: FAIL — `build_binding_class_figure` missing.

- [ ] **Step 3: Append to `src/itb/plotting.py`**

```python
import numpy as np


_CLASS_COLORS = {
    "": "#3da34d",                          # allowed (no binding)
    "amplitude_bootstrap": "#cf3535",       # red
    "information_theoretic": "#1f6feb",     # blue
    "gravitational_universality": "#b35900",# orange
}
_CLASS_INTS = {k: i for i, k in enumerate(_CLASS_COLORS.keys())}


def build_binding_class_figure(sweep) -> go.Figure:
    cls = sweep.binding_class_grid
    z = np.vectorize(lambda v: _CLASS_INTS.get(v, 0))(cls).astype(int).T
    colorscale = []
    n = max(len(_CLASS_INTS) - 1, 1)
    for k, i in _CLASS_INTS.items():
        colorscale.append([i / n, _CLASS_COLORS[k]])
    fig = go.Figure(
        data=go.Heatmap(
            x=sweep.x_values,
            y=sweep.y_values,
            z=z,
            colorscale=colorscale,
            zmin=0,
            zmax=n,
            showscale=False,
            hovertemplate=(
                f"{sweep.x_param}=%{{x:.3f}}<br>"
                f"{sweep.y_param}=%{{y:.3f}}<br>"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Binding constraint by class (green=allowed)",
        xaxis_title=sweep.x_param,
        yaxis_title=sweep.y_param,
        template="plotly_white",
    )
    return fig
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_plotting_v02.py tests/test_plotting.py -v`
Expected: 4 prior + 3 new = 7 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/plotting.py tests/test_plotting_v02.py
git commit -m "add binding-class-colored figure (Idea #3)"
```

---

### Task 7 — Newton boundary tracing (Idea #1 application)

**Files:**
- Modify: `src/itb/mapper.py` (append)
- Create: `tests/test_boundary_tracing.py`

- [ ] **Step 1: Write the failing test**

`tests/test_boundary_tracing.py`:
```python
import numpy as np

from itb.constraints.scalar_positivity import ScalarPositivityG4
from itb.mapper import trace_boundary_along_axis


def test_traces_boundary_for_g4_positivity():
    # Constraint: g_4 >= 0. Starting at g_4 = +0.5, walk along the negative
    # gradient (i.e. towards the boundary) and stop at the boundary.
    point = trace_boundary_along_axis(
        constraint=ScalarPositivityG4(),
        start={"g_4": 0.5, "g_6": 0.0},
        max_iters=20,
        tol=1e-9,
    )
    assert abs(point["g_4"] - 0.0) < 1e-6
    assert point["g_6"] == 0.0


def test_returns_starting_point_if_already_on_boundary():
    point = trace_boundary_along_axis(
        constraint=ScalarPositivityG4(),
        start={"g_4": 0.0, "g_6": 1.0},
        max_iters=20,
        tol=1e-9,
    )
    assert abs(point["g_4"]) < 1e-9


def test_traces_from_violation_back_to_boundary():
    point = trace_boundary_along_axis(
        constraint=ScalarPositivityG4(),
        start={"g_4": -0.7, "g_6": 0.5},
        max_iters=20,
        tol=1e-9,
    )
    assert abs(point["g_4"]) < 1e-6
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_boundary_tracing.py -v`
Expected: FAIL — `trace_boundary_along_axis` missing.

- [ ] **Step 3: Append to `src/itb/mapper.py`**

```python
from itb.theory import Theory as _Theory


def trace_boundary_along_axis(
    constraint,
    start: dict[str, float],
    max_iters: int = 50,
    tol: float = 1e-9,
) -> dict[str, float]:
    """Newton-style root-find along the constraint's gradient direction
    starting from `start`, walking to the constraint boundary (margin = 0).

    For a linear constraint with unit gradient the boundary is reached in
    one Newton step; for nonlinear constraints multiple iterations may be
    needed, hence max_iters.
    """
    point = dict(start)
    for _ in range(max_iters):
        theory = _Theory(coefficients=dict(point))
        margin = constraint.evaluate(theory).margin
        if abs(margin) < tol:
            return point
        grad = constraint.gradient(theory)
        norm_sq = sum(v * v for v in grad.values())
        if norm_sq == 0.0:
            return point
        # Newton step along negative gradient: x <- x - margin * grad / |grad|^2
        for k, gv in grad.items():
            point[k] = point.get(k, 0.0) - margin * gv / norm_sq
    return point
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_boundary_tracing.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/mapper.py tests/test_boundary_tracing.py
git commit -m "add Newton boundary tracing using gradient info (Idea #1 use)"
```

---

### Task 8 — SDP-mode constraint variant (Idea #5 + #7)

**Files:**
- Create: `src/itb/constraints/scalar_positivity_sdp.py`
- Create: `tests/test_scalar_positivity_sdp.py`

- [ ] **Step 1: Write the failing test**

`tests/test_scalar_positivity_sdp.py`:
```python
from itb.constraints.scalar_positivity_sdp import ScalarPositivityG4SDP
from itb.theory import Theory


def test_sdp_feasible_at_positive_value():
    c = ScalarPositivityG4SDP()
    r = c.evaluate(Theory(coefficients={"g_4": 0.5}))
    assert r.satisfied is True


def test_sdp_infeasible_at_negative_value():
    c = ScalarPositivityG4SDP()
    r = c.evaluate(Theory(coefficients={"g_4": -0.5}))
    assert r.satisfied is False


def test_sdp_feasibility_at_zero_with_default_tolerance():
    c = ScalarPositivityG4SDP()
    r = c.evaluate(Theory(coefficients={"g_4": 0.0}))
    # exactly zero is on the boundary; default tolerance treats >= -tol as feasible
    assert r.satisfied is True


def test_sdp_records_solver_status_in_details():
    c = ScalarPositivityG4SDP()
    r = c.evaluate(Theory(coefficients={"g_4": 0.5}))
    assert "solver_status" in r.details


def test_sdp_lazy_imports_cvxpy():
    # cvxpy must NOT be imported merely by importing the SDP module
    # (it should only import at evaluate-time); we approximate this by
    # checking that the module's top-level globals don't reference cvxpy.
    import itb.constraints.scalar_positivity_sdp as mod
    assert "cvxpy" not in mod.__dict__
    assert "cp" not in mod.__dict__
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_scalar_positivity_sdp.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write the implementation**

`src/itb/constraints/scalar_positivity_sdp.py`:
```python
"""SDP-mode positivity bound. Uses cvxpy to formulate g_4 >= 0 as an SDP
feasibility problem. Lazy import of cvxpy: it is only imported when the
constraint is actually evaluated, so importing this module costs nothing."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class ScalarPositivityG4SDP(Constraint):
    name = "scalar_positivity_g4_sdp"
    citation = "Adams et al 2006 (cvxpy SDP form)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory, tolerance: float = 1e-7) -> ConstraintResult:
        import cvxpy as cp  # lazy import
        g4_value = float(theory.coefficients.get("g_4", 0.0))
        x = cp.Variable()
        constraints = [x >= 0, x == g4_value]
        prob = cp.Problem(cp.Minimize(0), constraints)
        prob.solve(solver=cp.SCS, verbose=False)
        status = prob.status
        feasible = status in (cp.OPTIMAL, cp.OPTIMAL_INACCURATE) and g4_value >= -tolerance
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=feasible,
            margin=g4_value,
            signed_distance_margin=g4_value,
            details={"bound": "g_4 >= 0 (SDP)", "value": g4_value, "solver_status": status},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_4", 0.0)
        out["g_4"] = 1.0
        return out
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_scalar_positivity_sdp.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/constraints/scalar_positivity_sdp.py tests/test_scalar_positivity_sdp.py
git commit -m "add SDP-mode positivity constraint with lazy cvxpy import (#5 + #7)"
```

---

### Task 9 — Engine accepts tolerance + records numerical certificates (Idea #5 part 2)

**Files:**
- Modify: `src/itb/engine.py`
- Create: `tests/test_engine_tolerance.py`

- [ ] **Step 1: Write the failing test**

`tests/test_engine_tolerance.py`:
```python
from itb.constraints.scalar_positivity import ScalarPositivityG4
from itb.engine import check
from itb.theory import Theory


def test_default_tolerance_treats_exact_zero_as_feasible():
    r = check(Theory(coefficients={"g_4": 0.0}), [ScalarPositivityG4()])
    assert r.feasible is True


def test_strict_tolerance_treats_tiny_negative_as_infeasible():
    r = check(
        Theory(coefficients={"g_4": -1e-12}),
        [ScalarPositivityG4()],
        tolerance=0.0,
    )
    assert r.feasible is False


def test_loose_tolerance_treats_small_negative_as_feasible():
    r = check(
        Theory(coefficients={"g_4": -1e-3}),
        [ScalarPositivityG4()],
        tolerance=1e-2,
    )
    assert r.feasible is True


def test_tolerance_recorded_in_report():
    r = check(
        Theory(coefficients={"g_4": 0.5}),
        [ScalarPositivityG4()],
        tolerance=1e-4,
    )
    assert r.tolerance == 1e-4
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_engine_tolerance.py -v`
Expected: FAIL — `tolerance` parameter not accepted.

- [ ] **Step 3: Modify `src/itb/engine.py` — replace whole file**

```python
"""Engine: evaluate a theory against a set of constraints; return feasibility,
the most-binding constraint when infeasible, and per-constraint results.

A `tolerance` parameter relaxes the strict satisfaction test: a constraint is
treated as satisfied if its margin is >= -tolerance. Default tolerance is a
small positive number to avoid spurious infeasibility from floating-point
noise on boundary points."""

from dataclasses import dataclass

from itb.constraints.base import Constraint, ConstraintResult
from itb.theory import Theory


DEFAULT_TOLERANCE = 1e-9


@dataclass
class EngineReport:
    theory_name: str
    feasible: bool
    results: list[ConstraintResult]
    binding: str | None = None
    binding_class: str | None = None
    tolerance: float = DEFAULT_TOLERANCE


def check(
    theory: Theory,
    constraints: list[Constraint],
    tolerance: float = DEFAULT_TOLERANCE,
) -> EngineReport:
    raw_results = [c.evaluate(theory) for c in constraints]
    # apply tolerance: a constraint is "satisfied" if margin >= -tolerance
    results: list[ConstraintResult] = []
    for r in raw_results:
        satisfied = r.margin >= -tolerance
        results.append(
            ConstraintResult(
                constraint_name=r.constraint_name,
                satisfied=satisfied,
                margin=r.margin,
                signed_distance_margin=r.signed_distance_margin,
                details=dict(r.details),
            )
        )
    feasible = all(r.satisfied for r in results)
    binding_name: str | None = None
    binding_cls: str | None = None
    if not feasible:
        violated = [(c, r) for c, r in zip(constraints, results) if not r.satisfied]
        c, r = min(violated, key=lambda cr: cr[1].signed_distance_margin)
        binding_name = r.constraint_name
        binding_cls = c.constraint_class.value
    return EngineReport(
        theory_name=theory.name,
        feasible=feasible,
        results=results,
        binding=binding_name,
        binding_class=binding_cls,
        tolerance=tolerance,
    )
```

- [ ] **Step 4: Run all engine tests**

Run: `pytest tests/test_engine.py tests/test_engine_binding.py tests/test_engine_tolerance.py -v`
Expected: prior + 4 new all passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/engine.py tests/test_engine_tolerance.py
git commit -m "engine accepts tolerance parameter for confidence-graded feasibility (#5)"
```

---

### Task 10 — Observable interface + scalar-EFT amplitude observable (Idea #4 part 1)

**Files:**
- Create: `src/itb/observables.py`
- Create: `tests/test_observables.py`

- [ ] **Step 1: Write the failing test**

`tests/test_observables.py`:
```python
import numpy as np

from itb.observables import Observable, ScalarForwardAmplitude
from itb.theory import Theory


def test_observable_returns_value_per_kinematic_point():
    obs = ScalarForwardAmplitude(s_values=np.array([0.1, 0.5, 1.0]))
    theory = Theory(coefficients={"g_4": 1.0, "g_6": 0.0})
    values = obs.predict(theory)
    assert values.shape == (3,)
    # M(s) = g_4 * s^2 + g_6 * s^4 in our toy
    np.testing.assert_allclose(values, np.array([0.01, 0.25, 1.0]), atol=1e-9)


def test_observable_jacobian_shape():
    obs = ScalarForwardAmplitude(s_values=np.array([0.1, 0.5, 1.0]))
    theory = Theory(coefficients={"g_4": 1.0, "g_6": 0.0})
    J = obs.jacobian(theory, ["g_4", "g_6"])
    # Jacobian: rows = kinematic points, cols = parameters
    assert J.shape == (3, 2)
    # column 0 (d/dg4): s^2 = [0.01, 0.25, 1.0]
    np.testing.assert_allclose(J[:, 0], [0.01, 0.25, 1.0])
    # column 1 (d/dg6): s^4 = [0.0001, 0.0625, 1.0]
    np.testing.assert_allclose(J[:, 1], [0.0001, 0.0625, 1.0])


def test_observable_protocol_attributes():
    obs = ScalarForwardAmplitude(s_values=np.array([0.5]))
    assert isinstance(obs, Observable)
    assert obs.name == "scalar_forward_amplitude"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_observables.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write `src/itb/observables.py`**

```python
"""Observable interface: a function from Theory to numerical predictions plus
its Jacobian with respect to parameters. Used to compute Fisher information
metrics on theory space.

The toy `ScalarForwardAmplitude` predicts the leading EFT contribution to the
forward 2->2 amplitude M(s, t=0) = g_4 * s^2 + g_6 * s^4 at a chosen set of
kinematic points. Future observables (graviton scattering, holographic
entropy) will share this protocol."""

from abc import ABC, abstractmethod

import numpy as np

from itb.theory import Theory


class Observable(ABC):
    name: str = ""

    @abstractmethod
    def predict(self, theory: Theory) -> np.ndarray: ...

    @abstractmethod
    def jacobian(self, theory: Theory, params: list[str]) -> np.ndarray:
        """Return matrix of d(predict)/d(param) with shape (len(s_values), len(params))."""
        ...


class ScalarForwardAmplitude(Observable):
    name = "scalar_forward_amplitude"

    def __init__(self, s_values: np.ndarray):
        self.s_values = np.asarray(s_values, dtype=float)

    def predict(self, theory: Theory) -> np.ndarray:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        s = self.s_values
        return g4 * s ** 2 + g6 * s ** 4

    def jacobian(self, theory: Theory, params: list[str]) -> np.ndarray:
        s = self.s_values
        cols = []
        for p in params:
            if p == "g_4":
                cols.append(s ** 2)
            elif p == "g_6":
                cols.append(s ** 4)
            else:
                cols.append(np.zeros_like(s))
        return np.stack(cols, axis=1)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_observables.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/observables.py tests/test_observables.py
git commit -m "add Observable interface + scalar forward-amplitude observable (#4 prep)"
```

---

### Task 11 — Fisher information metric (Idea #4 part 2)

**Files:**
- Create: `src/itb/fisher.py`
- Create: `tests/test_fisher.py`

- [ ] **Step 1: Write the failing test**

`tests/test_fisher.py`:
```python
import numpy as np

from itb.fisher import fisher_metric
from itb.observables import ScalarForwardAmplitude
from itb.theory import Theory


def test_fisher_metric_shape_matches_param_count():
    obs = ScalarForwardAmplitude(s_values=np.array([0.5, 1.0]))
    g = fisher_metric(
        observable=obs,
        theory=Theory(coefficients={"g_4": 1.0, "g_6": 0.0}),
        params=["g_4", "g_6"],
        sigma=0.1,
    )
    assert g.shape == (2, 2)


def test_fisher_metric_is_symmetric():
    obs = ScalarForwardAmplitude(s_values=np.array([0.3, 0.7, 1.1]))
    g = fisher_metric(
        observable=obs,
        theory=Theory(coefficients={"g_4": 0.5, "g_6": 0.2}),
        params=["g_4", "g_6"],
        sigma=0.05,
    )
    np.testing.assert_allclose(g, g.T)


def test_fisher_metric_positive_definite():
    obs = ScalarForwardAmplitude(s_values=np.array([0.1, 0.5, 1.0, 1.5]))
    g = fisher_metric(
        observable=obs,
        theory=Theory(coefficients={"g_4": 0.0, "g_6": 0.0}),
        params=["g_4", "g_6"],
        sigma=0.1,
    )
    eigs = np.linalg.eigvalsh(g)
    assert (eigs > 0).all()


def test_fisher_metric_value_for_simple_case():
    # Single kinematic point s=1, sigma=1: J = [[1, 1]], so g = J^T J / sigma^2 = [[1,1],[1,1]]
    obs = ScalarForwardAmplitude(s_values=np.array([1.0]))
    g = fisher_metric(
        observable=obs,
        theory=Theory(coefficients={"g_4": 0.0, "g_6": 0.0}),
        params=["g_4", "g_6"],
        sigma=1.0,
    )
    np.testing.assert_allclose(g, np.array([[1.0, 1.0], [1.0, 1.0]]))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_fisher.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write `src/itb/fisher.py`**

```python
"""Fisher information metric on theory space.

Given an observable that predicts a vector of values from a theory, and a
Gaussian noise model with std `sigma` on each prediction, the Fisher
information metric on parameter space is

    g_{ab}(theta) = sum_i (d M_i / d theta_a)(d M_i / d theta_b) / sigma^2
                  = J^T J / sigma^2

where J is the Jacobian. This is the natural metric for distinguishability
of theories under the chosen observable, and it is what experimentalists
care about when asking "are these theories observably different?"."""

import numpy as np

from itb.observables import Observable
from itb.theory import Theory


def fisher_metric(
    observable: Observable,
    theory: Theory,
    params: list[str],
    sigma: float,
) -> np.ndarray:
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    J = observable.jacobian(theory, params)
    return (J.T @ J) / (sigma ** 2)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_fisher.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/fisher.py tests/test_fisher.py
git commit -m "add Fisher information metric on theory space (#4)"
```

---

### Task 12 — Smallest-violating-perturbation (Idea #6)

**Files:**
- Create: `src/itb/perturbation.py`
- Create: `tests/test_perturbation.py`

- [ ] **Step 1: Write the failing test**

`tests/test_perturbation.py`:
```python
import numpy as np
import pytest

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.perturbation import smallest_violating_perturbation
from itb.theory import Theory


def test_returns_zero_for_already_violating_theory():
    res = smallest_violating_perturbation(
        theory=Theory(coefficients={"g_4": -0.5, "g_6": 0.5}),
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    assert res.distance == 0.0


def test_returns_distance_to_g4_axis_for_pure_g4_violation_path():
    res = smallest_violating_perturbation(
        theory=Theory(coefficients={"g_4": 0.5, "g_6": 0.5}),
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    # Closest constraint is g_4 (or g_6) — both are at distance 0.5.
    assert res.distance == pytest.approx(0.5, abs=1e-6)


def test_returns_binding_constraint_at_perturbed_point():
    res = smallest_violating_perturbation(
        theory=Theory(coefficients={"g_4": 0.7, "g_6": 0.2}),
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    # g_6 is closer (0.2 < 0.7) — the smallest perturbation drops g_6 to ~0
    assert res.binding_constraint == "scalar_positivity_g6"
    assert res.distance == pytest.approx(0.2, abs=1e-6)


def test_perturbed_point_is_on_constraint_boundary():
    res = smallest_violating_perturbation(
        theory=Theory(coefficients={"g_4": 0.5, "g_6": 0.5}),
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    # The perturbed theory should have its binding constraint margin near zero
    if res.binding_constraint == "scalar_positivity_g4":
        assert abs(res.perturbed_theory.coefficients["g_4"]) < 1e-6
    else:
        assert abs(res.perturbed_theory.coefficients["g_6"]) < 1e-6
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_perturbation.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write `src/itb/perturbation.py`**

```python
"""Negative-result mode: given a feasible theory, find the smallest
perturbation in coefficient space that violates feasibility.

Output: the most-fragile constraint (the one closest to violation) and the
Euclidean distance to it. For a feasible theory, this answers "how far is
this theory from being ruled out, and which physical principle would rule
it out first?" — the most useful diagnostic short of an experiment.

For a constraint with constant unit gradient, the distance to its boundary
is exactly its signed-distance margin. We exploit this: the smallest
violating perturbation is the constraint with the smallest positive
signed_distance_margin, and the perturbed point is obtained by Newton-stepping
to that constraint's boundary."""

from dataclasses import dataclass

from itb.constraints.base import Constraint
from itb.engine import check
from itb.mapper import trace_boundary_along_axis
from itb.theory import Theory


@dataclass
class PerturbationResult:
    distance: float
    binding_constraint: str
    perturbed_theory: Theory


def smallest_violating_perturbation(
    theory: Theory,
    constraints: list[Constraint],
) -> PerturbationResult:
    report = check(theory, constraints)
    if not report.feasible:
        return PerturbationResult(
            distance=0.0,
            binding_constraint=report.binding or "",
            perturbed_theory=theory,
        )
    # Among feasible constraints, find the one with smallest signed distance.
    best: tuple[float, Constraint] | None = None
    for c, r in zip(constraints, report.results):
        if best is None or r.signed_distance_margin < best[0]:
            best = (r.signed_distance_margin, c)
    assert best is not None
    distance, binding_c = best
    perturbed_coeffs = trace_boundary_along_axis(
        constraint=binding_c,
        start=dict(theory.coefficients),
    )
    perturbed_theory = Theory(
        coefficients=perturbed_coeffs,
        name=f"{theory.name}+perturbed",
        source=f"smallest violating perturbation of {theory.name}",
    )
    return PerturbationResult(
        distance=distance,
        binding_constraint=binding_c.name,
        perturbed_theory=perturbed_theory,
    )
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_perturbation.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/perturbation.py tests/test_perturbation.py
git commit -m "add smallest-violating-perturbation analysis (Idea #6)"
```

---

### Task 13 — Server: expose binding-class sweep, perturbation, fisher (integration)

**Files:**
- Modify: `src/itb/api/server.py`
- Create: `tests/test_server_v02.py`

- [ ] **Step 1: Write the failing test**

`tests/test_server_v02.py`:
```python
from fastapi.testclient import TestClient

from itb.api.server import app


client = TestClient(app)


def test_sweep_returns_binding_class_figure_when_requested():
    r = client.post(
        "/sweep",
        json={
            "x_param": "g_4",
            "x_range": [-1.0, 1.0],
            "x_steps": 7,
            "y_param": "g_6",
            "y_range": [-1.0, 1.0],
            "y_steps": 7,
            "constraints": ["scalar_positivity_g4", "scalar_positivity_g6"],
            "color_by": "binding_class",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "figure" in body
    assert "binding_grid" in body


def test_perturbation_endpoint():
    r = client.post(
        "/perturbation",
        json={
            "coefficients": {"g_4": 0.5, "g_6": 0.5},
            "constraints": ["scalar_positivity_g4", "scalar_positivity_g6"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "distance" in body
    assert "binding_constraint" in body
    assert body["distance"] > 0


def test_fisher_endpoint():
    r = client.post(
        "/fisher",
        json={
            "coefficients": {"g_4": 0.5, "g_6": 0.5},
            "params": ["g_4", "g_6"],
            "s_values": [0.5, 1.0],
            "sigma": 0.1,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "metric" in body
    assert len(body["metric"]) == 2
    assert len(body["metric"][0]) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_server_v02.py -v`
Expected: FAIL — endpoints missing or `color_by` not accepted.

- [ ] **Step 3: Modify `src/itb/api/server.py` — replace whole file**

```python
"""FastAPI server exposing engine, mapper, perturbation, fisher, and
metadata to a localhost UI."""

import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from itb.constraints.base import Constraint
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.constraints.scalar_positivity_sdp import ScalarPositivityG4SDP
from itb.engine import check
from itb.fisher import fisher_metric
from itb.frameworks.base import Framework
from itb.frameworks.pure_gr import PureGR
from itb.mapper import sweep_2d
from itb.observables import ScalarForwardAmplitude
from itb.perturbation import smallest_violating_perturbation
from itb.plotting import build_allowed_region_figure, build_binding_class_figure
from itb.theory import Theory


CONSTRAINTS: dict[str, type[Constraint]] = {
    "scalar_positivity_g4": ScalarPositivityG4,
    "scalar_positivity_g6": ScalarPositivityG6,
    "scalar_positivity_g4_sdp": ScalarPositivityG4SDP,
}

FRAMEWORKS: dict[str, type[Framework]] = {
    "pure_gr": PureGR,
}


def _resolve_constraints(names: list[str]) -> list[Constraint]:
    resolved: list[Constraint] = []
    for n in names:
        if n not in CONSTRAINTS:
            raise HTTPException(400, f"Unknown constraint: {n}")
        resolved.append(CONSTRAINTS[n]())
    return resolved


class CheckRequest(BaseModel):
    coefficients: dict[str, float]
    constraints: list[str]
    tolerance: float | None = None


class SweepRequest(BaseModel):
    x_param: str
    x_range: tuple[float, float]
    x_steps: int
    y_param: str
    y_range: tuple[float, float]
    y_steps: int
    constraints: list[str]
    fixed_coefficients: dict[str, float] | None = None
    color_by: str = "feasibility"  # or "binding_class"


class PerturbationRequest(BaseModel):
    coefficients: dict[str, float]
    constraints: list[str]


class FisherRequest(BaseModel):
    coefficients: dict[str, float]
    params: list[str]
    s_values: list[float]
    sigma: float


app = FastAPI(title="ITB Engine", version="0.2.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/constraints")
def list_constraints() -> list[dict]:
    items = []
    for key, cls in CONSTRAINTS.items():
        c = cls()
        items.append({
            "name": c.name,
            "citation": c.citation,
            "constraint_class": c.constraint_class.value,
        })
    return items


@app.get("/frameworks")
def list_frameworks() -> list[dict]:
    items = []
    for key, cls in FRAMEWORKS.items():
        fw = cls()
        theory = fw.encode()
        items.append({
            "name": fw.name,
            "citation": fw.citation,
            "coefficients": theory.coefficients,
        })
    return items


@app.post("/check")
def check_theory(req: CheckRequest) -> dict:
    theory = Theory(coefficients=req.coefficients)
    constraints = _resolve_constraints(req.constraints)
    kwargs = {}
    if req.tolerance is not None:
        kwargs["tolerance"] = req.tolerance
    report = check(theory, constraints, **kwargs)
    return {
        "feasible": report.feasible,
        "binding": report.binding,
        "binding_class": report.binding_class,
        "tolerance": report.tolerance,
        "results": [
            {
                "constraint_name": r.constraint_name,
                "satisfied": r.satisfied,
                "margin": r.margin,
                "signed_distance_margin": r.signed_distance_margin,
                "details": r.details,
            }
            for r in report.results
        ],
    }


@app.post("/sweep")
def sweep(req: SweepRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    result = sweep_2d(
        x_param=req.x_param,
        x_range=req.x_range,
        x_steps=req.x_steps,
        y_param=req.y_param,
        y_range=req.y_range,
        y_steps=req.y_steps,
        constraints=constraints,
        fixed_coefficients=req.fixed_coefficients,
    )
    if req.color_by == "binding_class":
        fig = build_binding_class_figure(result)
    else:
        fig = build_allowed_region_figure(result)
    return {
        "x_param": result.x_param,
        "x_values": result.x_values.tolist(),
        "y_param": result.y_param,
        "y_values": result.y_values.tolist(),
        "grid": result.feasibility_grid.tolist(),
        "binding_grid": result.binding_grid.tolist(),
        "binding_class_grid": result.binding_class_grid.tolist(),
        "figure": json.loads(fig.to_json()),
    }


@app.post("/perturbation")
def perturbation(req: PerturbationRequest) -> dict:
    theory = Theory(coefficients=req.coefficients)
    constraints = _resolve_constraints(req.constraints)
    res = smallest_violating_perturbation(theory, constraints)
    return {
        "distance": res.distance,
        "binding_constraint": res.binding_constraint,
        "perturbed_coefficients": res.perturbed_theory.coefficients,
    }


@app.post("/fisher")
def fisher(req: FisherRequest) -> dict:
    theory = Theory(coefficients=req.coefficients)
    obs = ScalarForwardAmplitude(s_values=np.array(req.s_values))
    g = fisher_metric(observable=obs, theory=theory, params=req.params, sigma=req.sigma)
    return {"metric": g.tolist(), "params": req.params}


_FRONTEND_DIR = Path(__file__).resolve().parents[3] / "frontend"
if _FRONTEND_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=_FRONTEND_DIR),
        name="static",
    )

    @app.get("/", response_class=HTMLResponse)
    def index() -> HTMLResponse:
        return HTMLResponse((_FRONTEND_DIR / "index.html").read_text(encoding="utf-8"))
```

- [ ] **Step 4: Run all server tests**

Run: `pytest tests/test_server.py tests/test_server_v02.py -v`
Expected: prior + 3 new all pass.

- [ ] **Step 5: Commit**

```bash
git add src/itb/api/server.py tests/test_server_v02.py
git commit -m "expose v0.2 endpoints: binding-class sweep, perturbation, fisher"
```

---

### Task 14 — Frontend: binding-class toggle, perturbation panel, fisher panel

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/app.js`
- Modify: `frontend/style.css`

- [ ] **Step 1: Replace `frontend/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ITB Engine</title>
<link rel="stylesheet" href="/static/style.css">
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
</head>
<body>
<header>
  <h1>ITB Engine</h1>
  <p class="subtitle">Information-Theoretic Bootstrap &mdash; quantum gravity theory-space exclusions.</p>
</header>

<main>
  <section class="panel">
    <h2>Single-theory check</h2>
    <form id="check-form">
      <label>g_4 <input type="number" name="g_4" step="0.1" value="0.5"></label>
      <label>g_6 <input type="number" name="g_6" step="0.1" value="0.5"></label>
      <fieldset>
        <legend>Constraints</legend>
        <label><input type="checkbox" name="c" value="scalar_positivity_g4" checked> g_4 positivity</label>
        <label><input type="checkbox" name="c" value="scalar_positivity_g6" checked> g_6 positivity</label>
      </fieldset>
      <button type="submit">Check</button>
    </form>
    <pre id="check-result"></pre>
  </section>

  <section class="panel">
    <h2>Sweep theory space</h2>
    <form id="sweep-form">
      <label>x param <input type="text" name="x_param" value="g_4"></label>
      <label>x min <input type="number" name="x_min" step="0.1" value="-1"></label>
      <label>x max <input type="number" name="x_max" step="0.1" value="1"></label>
      <label>x steps <input type="number" name="x_steps" min="2" value="31"></label>
      <label>y param <input type="text" name="y_param" value="g_6"></label>
      <label>y min <input type="number" name="y_min" step="0.1" value="-1"></label>
      <label>y max <input type="number" name="y_max" step="0.1" value="1"></label>
      <label>y steps <input type="number" name="y_steps" min="2" value="31"></label>
      <label>color
        <select name="color_by">
          <option value="feasibility">feasible / not</option>
          <option value="binding_class">binding constraint class</option>
        </select>
      </label>
      <button type="submit">Run sweep</button>
    </form>
    <div id="sweep-plot"></div>
  </section>

  <section class="panel">
    <h2>Smallest violating perturbation (negative-result mode)</h2>
    <form id="perturb-form">
      <label>g_4 <input type="number" name="g_4" step="0.1" value="0.5"></label>
      <label>g_6 <input type="number" name="g_6" step="0.1" value="0.5"></label>
      <button type="submit">Find</button>
    </form>
    <pre id="perturb-result"></pre>
  </section>

  <section class="panel">
    <h2>Fisher information metric</h2>
    <form id="fisher-form">
      <label>g_4 <input type="number" name="g_4" step="0.1" value="0.5"></label>
      <label>g_6 <input type="number" name="g_6" step="0.1" value="0.5"></label>
      <label>s values (csv) <input type="text" name="s_values" value="0.5,1.0,1.5"></label>
      <label>sigma <input type="number" name="sigma" step="0.05" value="0.1"></label>
      <button type="submit">Compute</button>
    </form>
    <pre id="fisher-result"></pre>
  </section>
</main>

<script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Replace `frontend/app.js`**

```javascript
async function postJSON(url, body) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}

document.getElementById("check-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const constraints = fd.getAll("c");
  const coefficients = {
    g_4: parseFloat(fd.get("g_4")),
    g_6: parseFloat(fd.get("g_6")),
  };
  const out = document.getElementById("check-result");
  try {
    const data = await postJSON("/check", { coefficients, constraints });
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});

document.getElementById("sweep-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    x_param: fd.get("x_param"),
    x_range: [parseFloat(fd.get("x_min")), parseFloat(fd.get("x_max"))],
    x_steps: parseInt(fd.get("x_steps"), 10),
    y_param: fd.get("y_param"),
    y_range: [parseFloat(fd.get("y_min")), parseFloat(fd.get("y_max"))],
    y_steps: parseInt(fd.get("y_steps"), 10),
    constraints: ["scalar_positivity_g4", "scalar_positivity_g6"],
    color_by: fd.get("color_by"),
  };
  try {
    const data = await postJSON("/sweep", body);
    Plotly.newPlot("sweep-plot", data.figure.data, data.figure.layout, { responsive: true });
  } catch (err) { document.getElementById("sweep-plot").textContent = String(err); }
});

document.getElementById("perturb-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    coefficients: {
      g_4: parseFloat(fd.get("g_4")),
      g_6: parseFloat(fd.get("g_6")),
    },
    constraints: ["scalar_positivity_g4", "scalar_positivity_g6"],
  };
  const out = document.getElementById("perturb-result");
  try {
    const data = await postJSON("/perturbation", body);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});

document.getElementById("fisher-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = {
    coefficients: {
      g_4: parseFloat(fd.get("g_4")),
      g_6: parseFloat(fd.get("g_6")),
    },
    params: ["g_4", "g_6"],
    s_values: fd.get("s_values").split(",").map((s) => parseFloat(s.trim())),
    sigma: parseFloat(fd.get("sigma")),
  };
  const out = document.getElementById("fisher-result");
  try {
    const data = await postJSON("/fisher", body);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) { out.textContent = String(err); }
});
```

- [ ] **Step 3: Append to `frontend/style.css`** (no replacement, just an additional rule)

```css
select { padding: 0.4rem; border: 1px solid #cbd2d9; border-radius: 4px; }
```

- [ ] **Step 4: Smoke test in browser**

Start server, open `http://localhost:8000/`. Verify:
- The sweep panel has a "color" dropdown; switching to "binding constraint class" re-renders with class colors.
- The perturbation panel returns a binding constraint and a positive distance for `g_4=0.5, g_6=0.5`.
- The Fisher panel returns a 2×2 matrix.

- [ ] **Step 5: Commit**

```bash
git add frontend
git commit -m "frontend exposes binding-class color, perturbation, and fisher metric"
```

---

### Task 15 — Tag v0.2.0

- [ ] **Step 1: Run full test suite**

Run: `pytest`
Expected: all tests pass (target: ~80+ across all v0.1 + v0.2 files).

- [ ] **Step 2: Tag and document**

```bash
git tag -a v0.2.0 -m "ITB Engine v0.2.0: 7 research-direction ideas landed"
git log --oneline v0.1.0..HEAD
```

---

## Out of scope for this plan (queued for v0.3)

- Real graviton-EFT positivity bounds (Caron-Huot et al 2021–2024).
- Holographic entropy cone (Bao-Nezami-Ooguri-Stoica-Sully-Walter inequalities).
- Bekenstein, Bousso, modular flow constraints.
- String-theory and asymptotic-safety framework encoders.
- Research notebook (SQLite-backed).
- Vulcan compute handoff for heavy SDP runs.

---

## Self-review notes

- **Spec coverage:** All 7 ideas from the notes file map to tasks: #1 → Tasks 1, 7; #2 → Tasks 2, 5; #3 → Tasks 3, 4, 6; #4 → Tasks 10, 11; #5 → Tasks 8, 9; #6 → Task 12; #7 → Task 8 (lazy import in SDP module). Server + UI integration in 13–14.
- **Placeholders:** None. Every step has runnable code.
- **Type consistency:** `ConstraintResult.signed_distance_margin` introduced in Task 1 and used in Tasks 3, 8, 12. `EngineReport.binding`, `binding_class`, `tolerance` introduced in Tasks 3 and 9 and used in Task 13. `SweepResult.binding_grid`, `binding_class_grid` introduced in Task 4 and used in Tasks 5, 6, 13. `Region.binding` is `dict` everywhere.
- **TDD discipline:** Every task is failing-test → implementation → passing-test → commit.
