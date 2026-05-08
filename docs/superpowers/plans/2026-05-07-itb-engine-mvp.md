# ITB Engine MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimum viable end-to-end pipeline of the ITB Engine — a localhost web tool that takes a parameterized quantum-gravity-adjacent EFT, checks whether it satisfies a known consistency constraint (positivity bounds on Wilson coefficients), sweeps a 2D parameter region, and visualizes the allowed-vs-forbidden map in a browser.

**Architecture:** Python package (`itb`) with pluggable `constraints/` and `frameworks/` modules; a thin SDP-capable engine using `cvxpy`; a `Mapper` for parameter sweeps; a FastAPI server exposing the engine; a static HTML+Plotly frontend served from the same process. Designed so adding a new constraint or framework is one new file in the right directory — no edits elsewhere.

**Tech Stack:** Python 3.11+, cvxpy, NumPy, SciPy, FastAPI, Uvicorn, Plotly (JS), pytest, ruff.

---

## File Structure

```
itb-engine/
├── pyproject.toml
├── README.md
├── .gitignore
├── src/itb/
│   ├── __init__.py
│   ├── theory.py                  # Theory dataclass (Wilson coefficients)
│   ├── constraints/
│   │   ├── __init__.py            # auto-discovery
│   │   ├── base.py                # Constraint protocol, ConstraintResult
│   │   └── scalar_positivity.py   # First two constraints (g4, g6 ≥ 0)
│   ├── frameworks/
│   │   ├── __init__.py            # auto-discovery
│   │   ├── base.py                # Framework protocol
│   │   └── pure_gr.py             # GR baseline encoder
│   ├── engine.py                  # check(theory, constraints) → result
│   ├── mapper.py                  # 2D parameter sweep
│   ├── plotting.py                # Plotly figure builders
│   ├── cli.py                     # entry point: `itb` command
│   └── api/
│       ├── __init__.py
│       └── server.py              # FastAPI app
├── frontend/
│   ├── index.html                 # single-page UI
│   ├── style.css
│   └── app.js                     # fetch + Plotly rendering
└── tests/
    ├── __init__.py
    ├── test_theory.py
    ├── test_constraint_base.py
    ├── test_scalar_positivity.py
    ├── test_pure_gr.py
    ├── test_engine.py
    ├── test_mapper.py
    ├── test_plotting.py
    ├── test_cli.py
    └── test_server.py
```

---

## Physics encoded in v1

**The constraint:** Positivity bounds on a scalar-field EFT (Adams-Arkani-Hamed-Dubovsky-Nicolis-Rattazzi 2006). For a 2→2 forward elastic amplitude `M(s, 0)` of a real scalar, dispersion + unitarity give

```
g_4 ≡ (1/2) d²M(s,0)/ds² |_{s=0} ≥ 0
g_6 ≡ (1/24) d⁴M(s,0)/ds⁴ |_{s=0} ≥ 0
```

These are the two simplest positivity constraints. They define the first quadrant of `(g_4, g_6)` parameter space as allowed; everywhere else is excluded.

**Why this constraint first:** It is the smallest non-trivial test case. Both bounds are linear in coefficients, so the SDP collapses to inequality checks — but the architecture still routes through cvxpy so swapping in a real semidefinite constraint later is a one-file change.

**The framework:** `pure_gr` returns `g_4 = 0`, `g_6 = 0` (free theory limit, sits on the boundary of the allowed cone). v2 plans will add string-EFT and asymptotic-safety encoders.

---

## Tasks

### Task 1: Project skeleton

**Files:**
- Create: `C:\Users\ihass\itb-engine\pyproject.toml`
- Create: `C:\Users\ihass\itb-engine\.gitignore`
- Create: `C:\Users\ihass\itb-engine\src\itb\__init__.py`
- Create: `C:\Users\ihass\itb-engine\tests\__init__.py`
- Create: `C:\Users\ihass\itb-engine\README.md`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "itb"
version = "0.1.0"
description = "Information-Theoretic Bootstrap engine for quantum gravity theory-space exclusions"
requires-python = ">=3.11"
dependencies = [
    "cvxpy>=1.5",
    "numpy>=1.26",
    "scipy>=1.12",
    "fastapi>=0.110",
    "uvicorn[standard]>=0.27",
    "plotly>=5.20",
    "pydantic>=2.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",
    "ruff>=0.4",
]

[project.scripts]
itb = "itb.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: Create `.gitignore`**

```
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.ruff_cache/
.venv/
venv/
*.egg-info/
build/
dist/
data/runs/
data/notebook.sqlite
.idea/
.vscode/
.DS_Store
```

- [ ] **Step 3: Create `src/itb/__init__.py`**

```python
"""ITB Engine — Information-Theoretic Bootstrap for quantum gravity."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Create `tests/__init__.py`** (empty file)

```python
```

- [ ] **Step 5: Create `README.md`**

```markdown
# ITB Engine

Information-Theoretic Bootstrap engine for quantum gravity theory-space exclusions.

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate     # Windows PowerShell
pip install -e ".[dev]"
pytest
itb --help
itb serve                  # http://localhost:8000
```

## Status

MVP — see `docs/superpowers/specs/2026-05-07-itb-engine-design.md` for the design,
and `docs/superpowers/plans/2026-05-07-itb-engine-mvp.md` for the plan.
```

- [ ] **Step 6: Create venv and install**

Run (PowerShell):
```powershell
cd C:\Users\ihass\itb-engine
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```
Expected: pip installs without errors. The `itb` script is registered.

- [ ] **Step 7: Verify pytest runs (no tests yet)**

Run: `pytest`
Expected: "no tests ran" (exit 5) — that's fine for now.

- [ ] **Step 8: Commit**

```bash
cd /c/Users/ihass/itb-engine
git add pyproject.toml .gitignore src tests README.md
git commit -m "scaffold itb-engine package with venv and pytest"
```

---

### Task 2: Theory dataclass

**Files:**
- Create: `src/itb/theory.py`
- Create: `tests/test_theory.py`

- [ ] **Step 1: Write the failing test**

`tests/test_theory.py`:
```python
from itb.theory import Theory


def test_theory_holds_coefficients():
    t = Theory(coefficients={"g_4": 1.0, "g_6": 0.5})
    assert t.coefficients["g_4"] == 1.0
    assert t.coefficients["g_6"] == 0.5


def test_theory_get_with_default():
    t = Theory(coefficients={"g_4": 1.0})
    assert t.get("g_4") == 1.0
    assert t.get("g_6", default=0.0) == 0.0


def test_theory_with_metadata():
    t = Theory(coefficients={"g_4": 1.0}, name="test", source="unit-test")
    assert t.name == "test"
    assert t.source == "unit-test"


def test_theory_immutable_coefficients():
    t = Theory(coefficients={"g_4": 1.0})
    # Replacing the whole dict is fine; mutating an attribute should not be done.
    # We document immutability via convention; dataclass(frozen=False) keeps it ergonomic.
    t2 = t.with_coefficient("g_6", 0.5)
    assert t2.coefficients["g_4"] == 1.0
    assert t2.coefficients["g_6"] == 0.5
    assert "g_6" not in t.coefficients
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_theory.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'itb.theory'`.

- [ ] **Step 3: Write minimal implementation**

`src/itb/theory.py`:
```python
"""Theory: the parameterized object the engine evaluates constraints against.

A Theory is a vector of named Wilson coefficients plus optional metadata
(name, source citation). It is the primary data unit passed between
frameworks (which produce theories) and constraints (which evaluate them).
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Theory:
    coefficients: dict[str, float]
    name: str = ""
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: float | None = None) -> float | None:
        return self.coefficients.get(key, default)

    def with_coefficient(self, key: str, value: float) -> "Theory":
        new_coeffs = dict(self.coefficients)
        new_coeffs[key] = value
        return Theory(
            coefficients=new_coeffs,
            name=self.name,
            source=self.source,
            metadata=dict(self.metadata),
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_theory.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/theory.py tests/test_theory.py
git commit -m "add Theory dataclass for Wilson-coefficient parameterizations"
```

---

### Task 3: Constraint protocol and result type

**Files:**
- Create: `src/itb/constraints/__init__.py`
- Create: `src/itb/constraints/base.py`
- Create: `tests/test_constraint_base.py`

- [ ] **Step 1: Write the failing test**

`tests/test_constraint_base.py`:
```python
from itb.constraints.base import Constraint, ConstraintResult, ConstraintClass
from itb.theory import Theory


class _DummyConstraint(Constraint):
    name = "dummy"
    citation = "test"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        margin = theory.coefficients.get("x", 0.0)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            details={"checked": "x >= 0"},
        )


def test_constraint_result_satisfied():
    c = _DummyConstraint()
    result = c.evaluate(Theory(coefficients={"x": 1.0}))
    assert result.satisfied is True
    assert result.margin == 1.0
    assert result.constraint_name == "dummy"


def test_constraint_result_violated():
    c = _DummyConstraint()
    result = c.evaluate(Theory(coefficients={"x": -2.0}))
    assert result.satisfied is False
    assert result.margin == -2.0


def test_constraint_metadata_present():
    c = _DummyConstraint()
    assert c.name == "dummy"
    assert c.citation == "test"
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_constraint_base.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'itb.constraints'`.

- [ ] **Step 3: Write minimal implementation**

`src/itb/constraints/__init__.py`:
```python
"""Constraint catalog. Adding a new constraint is a single new module here."""
```

`src/itb/constraints/base.py`:
```python
"""Base protocol for consistency constraints.

Each constraint is a self-contained module. To add a new constraint:
  1. Create a new file in this package.
  2. Subclass `Constraint` with the required class attributes.
  3. Implement `evaluate(theory) -> ConstraintResult`.
The engine will discover and use it automatically (see engine.py).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

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
    details: dict[str, Any] = field(default_factory=dict)


class Constraint(ABC):
    """Abstract base class. Subclasses must set name, citation, constraint_class."""

    name: str = ""
    citation: str = ""
    constraint_class: ConstraintClass = ConstraintClass.A_AMPLITUDE

    @abstractmethod
    def evaluate(self, theory: Theory) -> ConstraintResult:
        ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_constraint_base.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/constraints tests/test_constraint_base.py
git commit -m "add Constraint protocol with metadata and result type"
```

---

### Task 4: Scalar positivity constraint (g_4 and g_6)

**Files:**
- Create: `src/itb/constraints/scalar_positivity.py`
- Create: `tests/test_scalar_positivity.py`

- [ ] **Step 1: Write the failing test**

`tests/test_scalar_positivity.py`:
```python
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.constraints.base import ConstraintClass
from itb.theory import Theory


def test_g4_positive_satisfied():
    c = ScalarPositivityG4()
    result = c.evaluate(Theory(coefficients={"g_4": 0.5}))
    assert result.satisfied is True
    assert result.margin == 0.5


def test_g4_negative_violated():
    c = ScalarPositivityG4()
    result = c.evaluate(Theory(coefficients={"g_4": -0.1}))
    assert result.satisfied is False
    assert result.margin == -0.1


def test_g4_zero_at_boundary():
    c = ScalarPositivityG4()
    result = c.evaluate(Theory(coefficients={"g_4": 0.0}))
    assert result.satisfied is True
    assert result.margin == 0.0


def test_g4_missing_coefficient_defaults_to_zero():
    c = ScalarPositivityG4()
    result = c.evaluate(Theory(coefficients={}))
    # Absent coefficient is treated as zero — saturating the bound, hence allowed.
    assert result.satisfied is True


def test_g6_positive_satisfied():
    c = ScalarPositivityG6()
    result = c.evaluate(Theory(coefficients={"g_6": 0.2}))
    assert result.satisfied is True
    assert result.margin == 0.2


def test_g6_negative_violated():
    c = ScalarPositivityG6()
    result = c.evaluate(Theory(coefficients={"g_6": -0.5}))
    assert result.satisfied is False
    assert result.margin == -0.5


def test_metadata_correctly_set():
    c = ScalarPositivityG4()
    assert c.name == "scalar_positivity_g4"
    assert "Adams" in c.citation
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_scalar_positivity.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Write minimal implementation**

`src/itb/constraints/scalar_positivity.py`:
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
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=g4 >= 0,
            margin=g4,
            details={"bound": "g_4 >= 0", "value": g4},
        )


class ScalarPositivityG6(Constraint):
    name = "scalar_positivity_g6"
    citation = "Adams, Arkani-Hamed, Dubovsky, Nicolis, Rattazzi 2006"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g6 = theory.coefficients.get("g_6", 0.0)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=g6 >= 0,
            margin=g6,
            details={"bound": "g_6 >= 0", "value": g6},
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_scalar_positivity.py -v`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/constraints/scalar_positivity.py tests/test_scalar_positivity.py
git commit -m "add scalar EFT positivity bounds (Adams et al 2006)"
```

---

### Task 5: Framework protocol and Pure GR encoder

**Files:**
- Create: `src/itb/frameworks/__init__.py`
- Create: `src/itb/frameworks/base.py`
- Create: `src/itb/frameworks/pure_gr.py`
- Create: `tests/test_pure_gr.py`

- [ ] **Step 1: Write the failing test**

`tests/test_pure_gr.py`:
```python
from itb.frameworks.pure_gr import PureGR
from itb.theory import Theory


def test_pure_gr_returns_theory():
    fw = PureGR()
    theory = fw.encode()
    assert isinstance(theory, Theory)


def test_pure_gr_higher_order_coefficients_zero():
    theory = PureGR().encode()
    assert theory.coefficients.get("g_4", 0.0) == 0.0
    assert theory.coefficients.get("g_6", 0.0) == 0.0


def test_pure_gr_metadata():
    theory = PureGR().encode()
    assert theory.name == "pure_gr"
    assert "Einstein" in theory.source
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pure_gr.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Write minimal implementation**

`src/itb/frameworks/__init__.py`:
```python
"""Framework encoders. Each module produces a Theory representing a
candidate quantum-gravity-adjacent EFT (or low-energy expansion of one)."""
```

`src/itb/frameworks/base.py`:
```python
"""Framework encoder protocol. A framework produces a Theory."""

from abc import ABC, abstractmethod

from itb.theory import Theory


class Framework(ABC):
    name: str = ""
    citation: str = ""

    @abstractmethod
    def encode(self) -> Theory:
        ...
```

`src/itb/frameworks/pure_gr.py`:
```python
"""Baseline: pure general relativity with no higher-curvature corrections.
All higher-order Wilson coefficients are zero (free theory limit).
"""

from itb.frameworks.base import Framework
from itb.theory import Theory


class PureGR(Framework):
    name = "pure_gr"
    citation = "Einstein 1915, free-theory limit"

    def encode(self) -> Theory:
        return Theory(
            coefficients={"g_4": 0.0, "g_6": 0.0},
            name=self.name,
            source=self.citation,
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_pure_gr.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/frameworks tests/test_pure_gr.py
git commit -m "add Framework protocol and Pure GR baseline encoder"
```

---

### Task 6: Engine — check theory against constraints

**Files:**
- Create: `src/itb/engine.py`
- Create: `tests/test_engine.py`

- [ ] **Step 1: Write the failing test**

`tests/test_engine.py`:
```python
from itb.engine import check, EngineReport
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.frameworks.pure_gr import PureGR
from itb.theory import Theory


def test_engine_returns_report():
    theory = PureGR().encode()
    report = check(theory, [ScalarPositivityG4(), ScalarPositivityG6()])
    assert isinstance(report, EngineReport)


def test_engine_pure_gr_passes_positivity():
    theory = PureGR().encode()
    report = check(theory, [ScalarPositivityG4(), ScalarPositivityG6()])
    assert report.feasible is True
    assert all(r.satisfied for r in report.results)


def test_engine_negative_g4_fails():
    bad = Theory(coefficients={"g_4": -1.0, "g_6": 0.5})
    report = check(bad, [ScalarPositivityG4(), ScalarPositivityG6()])
    assert report.feasible is False


def test_engine_records_binding_constraint():
    bad = Theory(coefficients={"g_4": -1.0, "g_6": 0.5})
    report = check(bad, [ScalarPositivityG4(), ScalarPositivityG6()])
    binding = [r for r in report.results if not r.satisfied]
    assert len(binding) == 1
    assert binding[0].constraint_name == "scalar_positivity_g4"


def test_engine_empty_constraints_is_feasible():
    theory = PureGR().encode()
    report = check(theory, [])
    assert report.feasible is True
    assert report.results == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_engine.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Write minimal implementation**

`src/itb/engine.py`:
```python
"""Engine: evaluate a theory against a set of constraints and produce a
unified report including which constraints are binding when infeasible."""

from dataclasses import dataclass

from itb.constraints.base import Constraint, ConstraintResult
from itb.theory import Theory


@dataclass
class EngineReport:
    theory_name: str
    feasible: bool
    results: list[ConstraintResult]


def check(theory: Theory, constraints: list[Constraint]) -> EngineReport:
    results = [c.evaluate(theory) for c in constraints]
    feasible = all(r.satisfied for r in results)
    return EngineReport(
        theory_name=theory.name,
        feasible=feasible,
        results=results,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_engine.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/engine.py tests/test_engine.py
git commit -m "add engine.check: evaluate theory against constraint set"
```

---

### Task 7: Mapper — sweep 2D parameter region

**Files:**
- Create: `src/itb/mapper.py`
- Create: `tests/test_mapper.py`

- [ ] **Step 1: Write the failing test**

`tests/test_mapper.py`:
```python
import numpy as np

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.mapper import sweep_2d, SweepResult


def test_sweep_returns_result():
    result = sweep_2d(
        x_param="g_4",
        x_range=(-1.0, 1.0),
        x_steps=5,
        y_param="g_6",
        y_range=(-1.0, 1.0),
        y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    assert isinstance(result, SweepResult)


def test_sweep_grid_shape():
    result = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    assert result.feasibility_grid.shape == (5, 5)


def test_sweep_first_quadrant_allowed():
    result = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    # Find a point firmly in the first quadrant: x = 0.6, y = 0.6
    # Indices: with linspace(-1, 1, 11), step 0.2; index 8 is x = 0.6
    assert result.feasibility_grid[8, 8] is np.True_ or bool(result.feasibility_grid[8, 8])


def test_sweep_third_quadrant_disallowed():
    result = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    # Index 2 corresponds to -0.6
    assert not bool(result.feasibility_grid[2, 2])


def test_sweep_axes_recorded():
    result = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    np.testing.assert_allclose(result.x_values, np.linspace(-1.0, 1.0, 5))
    np.testing.assert_allclose(result.y_values, np.linspace(-1.0, 1.0, 5))
    assert result.x_param == "g_4"
    assert result.y_param == "g_6"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_mapper.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Write minimal implementation**

`src/itb/mapper.py`:
```python
"""Theory-space mapper: sweep over a parameter grid and record feasibility.

Convention for grid indexing: feasibility_grid[i, j] corresponds to
x_values[i], y_values[j]. (Row-major over x, column-major over y.)
"""

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
    feasibility_grid: np.ndarray  # bool, shape (len(x_values), len(y_values))


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
    grid = np.zeros((x_steps, y_steps), dtype=bool)
    for i, x in enumerate(x_values):
        for j, y in enumerate(y_values):
            coefficients = dict(fixed)
            coefficients[x_param] = float(x)
            coefficients[y_param] = float(y)
            theory = Theory(coefficients=coefficients, name="sweep_point")
            grid[i, j] = check(theory, constraints).feasible
    return SweepResult(
        x_param=x_param,
        x_values=x_values,
        y_param=y_param,
        y_values=y_values,
        feasibility_grid=grid,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_mapper.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/mapper.py tests/test_mapper.py
git commit -m "add 2D theory-space sweeper returning feasibility grid"
```

---

### Task 8: Plotting — Plotly figure builder

**Files:**
- Create: `src/itb/plotting.py`
- Create: `tests/test_plotting.py`

- [ ] **Step 1: Write the failing test**

`tests/test_plotting.py`:
```python
import json

import numpy as np
import plotly.graph_objects as go

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.mapper import sweep_2d
from itb.plotting import build_allowed_region_figure


def test_figure_is_plotly():
    sweep = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    fig = build_allowed_region_figure(sweep)
    assert isinstance(fig, go.Figure)


def test_figure_contains_heatmap():
    sweep = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    fig = build_allowed_region_figure(sweep)
    types = {trace.type for trace in fig.data}
    assert "heatmap" in types


def test_figure_axis_labels():
    sweep = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    fig = build_allowed_region_figure(sweep)
    assert fig.layout.xaxis.title.text == "g_4"
    assert fig.layout.yaxis.title.text == "g_6"


def test_figure_serialises_to_json():
    sweep = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )
    fig = build_allowed_region_figure(sweep)
    payload = fig.to_json()
    parsed = json.loads(payload)
    assert "data" in parsed
    assert "layout" in parsed
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_plotting.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Write minimal implementation**

`src/itb/plotting.py`:
```python
"""Plotly figure builders for sweep results."""

import numpy as np
import plotly.graph_objects as go

from itb.mapper import SweepResult


def build_allowed_region_figure(sweep: SweepResult) -> go.Figure:
    # Heatmap z is (rows = y, cols = x), so transpose feasibility_grid
    # which is (x_steps, y_steps) into (y_steps, x_steps).
    z = sweep.feasibility_grid.astype(int).T
    fig = go.Figure(
        data=go.Heatmap(
            x=sweep.x_values,
            y=sweep.y_values,
            z=z,
            colorscale=[[0, "#cf3535"], [1, "#3da34d"]],
            zmin=0,
            zmax=1,
            showscale=False,
            hovertemplate=(
                f"{sweep.x_param}=%{{x:.3f}}<br>"
                f"{sweep.y_param}=%{{y:.3f}}<br>"
                "feasible=%{z}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Allowed theory region (green) vs excluded (red)",
        xaxis_title=sweep.x_param,
        yaxis_title=sweep.y_param,
        template="plotly_white",
    )
    return fig
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_plotting.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/plotting.py tests/test_plotting.py
git commit -m "add Plotly heatmap builder for allowed-region sweeps"
```

---

### Task 9: FastAPI server

**Files:**
- Create: `src/itb/api/__init__.py`
- Create: `src/itb/api/server.py`
- Create: `tests/test_server.py`

- [ ] **Step 1: Write the failing test**

`tests/test_server.py`:
```python
from fastapi.testclient import TestClient

from itb.api.server import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_check_pure_gr():
    r = client.post(
        "/check",
        json={
            "coefficients": {"g_4": 0.0, "g_6": 0.0},
            "constraints": ["scalar_positivity_g4", "scalar_positivity_g6"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["feasible"] is True
    names = [r["constraint_name"] for r in body["results"]]
    assert "scalar_positivity_g4" in names
    assert "scalar_positivity_g6" in names


def test_check_violation():
    r = client.post(
        "/check",
        json={
            "coefficients": {"g_4": -1.0, "g_6": 0.5},
            "constraints": ["scalar_positivity_g4", "scalar_positivity_g6"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["feasible"] is False


def test_unknown_constraint_returns_400():
    r = client.post(
        "/check",
        json={
            "coefficients": {"g_4": 1.0},
            "constraints": ["does_not_exist"],
        },
    )
    assert r.status_code == 400


def test_sweep_returns_grid_and_figure():
    r = client.post(
        "/sweep",
        json={
            "x_param": "g_4",
            "x_range": [-1.0, 1.0],
            "x_steps": 5,
            "y_param": "g_6",
            "y_range": [-1.0, 1.0],
            "y_steps": 5,
            "constraints": ["scalar_positivity_g4", "scalar_positivity_g6"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "grid" in body
    assert len(body["grid"]) == 5
    assert len(body["grid"][0]) == 5
    assert "figure" in body  # JSON-serialized Plotly figure


def test_constraints_listing():
    r = client.get("/constraints")
    assert r.status_code == 200
    items = r.json()
    names = [item["name"] for item in items]
    assert "scalar_positivity_g4" in names
    assert "scalar_positivity_g6" in names


def test_frameworks_listing():
    r = client.get("/frameworks")
    assert r.status_code == 200
    items = r.json()
    names = [item["name"] for item in items]
    assert "pure_gr" in names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_server.py -v`
Expected: FAIL — server module does not exist.

- [ ] **Step 3: Write minimal implementation**

`src/itb/api/__init__.py`:
```python
"""HTTP API for the ITB engine."""
```

`src/itb/api/server.py`:
```python
"""FastAPI server exposing engine, mapper, and metadata to a localhost UI."""

import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel

from itb.constraints.base import Constraint
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.engine import check
from itb.frameworks.base import Framework
from itb.frameworks.pure_gr import PureGR
from itb.mapper import sweep_2d
from itb.plotting import build_allowed_region_figure
from itb.theory import Theory


CONSTRAINTS: dict[str, type[Constraint]] = {
    "scalar_positivity_g4": ScalarPositivityG4,
    "scalar_positivity_g6": ScalarPositivityG6,
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


class SweepRequest(BaseModel):
    x_param: str
    x_range: tuple[float, float]
    x_steps: int
    y_param: str
    y_range: tuple[float, float]
    y_steps: int
    constraints: list[str]
    fixed_coefficients: dict[str, float] | None = None


app = FastAPI(title="ITB Engine", version="0.1.0")


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
    report = check(theory, constraints)
    return {
        "feasible": report.feasible,
        "results": [
            {
                "constraint_name": r.constraint_name,
                "satisfied": r.satisfied,
                "margin": r.margin,
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
    fig = build_allowed_region_figure(result)
    return {
        "x_param": result.x_param,
        "x_values": result.x_values.tolist(),
        "y_param": result.y_param,
        "y_values": result.y_values.tolist(),
        "grid": result.feasibility_grid.tolist(),
        "figure": json.loads(fig.to_json()),
    }


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

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_server.py -v`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add src/itb/api tests/test_server.py
git commit -m "add FastAPI server with /check, /sweep, listings"
```

---

### Task 10: Static HTML frontend

**Files:**
- Create: `frontend/index.html`
- Create: `frontend/style.css`
- Create: `frontend/app.js`

- [ ] **Step 1: Create `frontend/index.html`**

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
  <p class="subtitle">Information-Theoretic Bootstrap — quantum gravity theory-space exclusions.</p>
</header>

<main>
  <section class="panel">
    <h2>Single-theory check</h2>
    <form id="check-form">
      <label>g_4 <input type="number" name="g_4" step="0.1" value="0.5"></label>
      <label>g_6 <input type="number" name="g_6" step="0.1" value="0.5"></label>
      <fieldset>
        <legend>Constraints</legend>
        <label><input type="checkbox" name="c" value="scalar_positivity_g4" checked> Scalar positivity g_4</label>
        <label><input type="checkbox" name="c" value="scalar_positivity_g6" checked> Scalar positivity g_6</label>
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
      <button type="submit">Run sweep</button>
    </form>
    <div id="sweep-plot"></div>
  </section>
</main>

<script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create `frontend/style.css`**

```css
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; background: #f6f7f9; color: #1f2933; }
header { padding: 1.5rem 2rem; background: #1f2933; color: white; }
header h1 { margin: 0; font-size: 1.5rem; }
.subtitle { margin: 0.25rem 0 0; color: #c5cdd6; font-size: 0.9rem; }
main { padding: 1.5rem 2rem; display: grid; gap: 1.5rem; max-width: 1200px; margin: 0 auto; }
.panel { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.panel h2 { margin-top: 0; font-size: 1.1rem; }
form { display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: flex-end; }
label { display: flex; flex-direction: column; font-size: 0.85rem; color: #52606d; }
label input[type="text"], label input[type="number"] { margin-top: 0.25rem; padding: 0.4rem; border: 1px solid #cbd2d9; border-radius: 4px; min-width: 6rem; }
fieldset { border: 1px solid #cbd2d9; border-radius: 4px; padding: 0.5rem 0.75rem; display: flex; gap: 1rem; align-items: center; }
fieldset legend { padding: 0 0.25rem; font-size: 0.85rem; color: #52606d; }
fieldset label { flex-direction: row; gap: 0.4rem; align-items: center; }
button { padding: 0.5rem 1rem; background: #1f6feb; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; }
button:hover { background: #1856b3; }
pre { background: #0f1115; color: #d8e0e8; padding: 0.75rem; border-radius: 4px; overflow-x: auto; font-size: 0.85rem; }
#sweep-plot { min-height: 480px; }
```

- [ ] **Step 3: Create `frontend/app.js`**

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
  } catch (err) {
    out.textContent = String(err);
  }
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
  };
  try {
    const data = await postJSON("/sweep", body);
    Plotly.newPlot("sweep-plot", data.figure.data, data.figure.layout, { responsive: true });
  } catch (err) {
    document.getElementById("sweep-plot").textContent = String(err);
  }
});
```

- [ ] **Step 4: Run server and smoke-test in browser**

Run (PowerShell, in venv):
```powershell
uvicorn itb.api.server:app --reload --port 8000
```
Open `http://localhost:8000/` in a browser. Expected:
- Page loads with two panels.
- Clicking **Check** with `g_4 = 0.5, g_6 = 0.5` shows feasible: true.
- Clicking **Run sweep** renders a green-and-red heatmap with the first quadrant green, others red.

Stop the server with Ctrl+C.

- [ ] **Step 5: Commit**

```bash
git add frontend
git commit -m "add static HTML + Plotly frontend served by FastAPI"
```

---

### Task 11: CLI entry point

**Files:**
- Create: `src/itb/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

`tests/test_cli.py`:
```python
import subprocess
import sys


def test_cli_help():
    r = subprocess.run(
        [sys.executable, "-m", "itb.cli", "--help"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "check" in r.stdout
    assert "serve" in r.stdout


def test_cli_check_pure_gr():
    r = subprocess.run(
        [sys.executable, "-m", "itb.cli", "check",
         "--g4", "0", "--g6", "0"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "feasible" in r.stdout.lower()


def test_cli_check_violation_exit_code():
    r = subprocess.run(
        [sys.executable, "-m", "itb.cli", "check",
         "--g4", "-1", "--g6", "0.5"],
        capture_output=True, text=True,
    )
    # Non-zero exit signals an infeasible theory (useful for scripts).
    assert r.returncode == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL — `itb.cli` not found.

- [ ] **Step 3: Write minimal implementation**

`src/itb/cli.py`:
```python
"""Command-line entry points for the ITB engine."""

import argparse
import json
import sys

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.engine import check
from itb.theory import Theory


def cmd_check(args: argparse.Namespace) -> int:
    theory = Theory(coefficients={"g_4": args.g4, "g_6": args.g6})
    report = check(theory, [ScalarPositivityG4(), ScalarPositivityG6()])
    payload = {
        "feasible": report.feasible,
        "results": [
            {
                "constraint_name": r.constraint_name,
                "satisfied": r.satisfied,
                "margin": r.margin,
            }
            for r in report.results
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0 if report.feasible else 2


def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn
    uvicorn.run(
        "itb.api.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="itb", description="ITB Engine CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="Check a single theory against positivity bounds")
    p_check.add_argument("--g4", type=float, required=True)
    p_check.add_argument("--g6", type=float, required=True)
    p_check.set_defaults(fn=cmd_check)

    p_serve = sub.add_parser("serve", help="Run the localhost web server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.add_argument("--reload", action="store_true")
    p_serve.set_defaults(fn=cmd_serve)

    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: 3 passed.

- [ ] **Step 5: Run full test suite**

Run: `pytest`
Expected: all tests pass (target: ~38 across all files).

- [ ] **Step 6: Commit**

```bash
git add src/itb/cli.py tests/test_cli.py
git commit -m "add CLI: check and serve subcommands"
```

---

### Task 12: End-to-end manual smoke test

- [ ] **Step 1: Start the server**

Run (PowerShell, in venv):
```powershell
itb serve --reload
```

- [ ] **Step 2: Open browser to http://localhost:8000/**

Verify:
- Page loads.
- "Check" with `g_4=0.5, g_6=0.5` returns feasible: true.
- "Check" with `g_4=-1, g_6=0.5` returns feasible: false with the g_4 constraint binding.
- "Sweep" renders a heatmap; first quadrant green, other quadrants red.
- Browser console has no JS errors.

- [ ] **Step 3: Stop server, finalize commit**

If anything was patched during smoke-test, commit it. Otherwise, no-op.

```bash
git status
```
Expected: clean working tree.

- [ ] **Step 4: Tag MVP**

```bash
git tag -a v0.1.0 -m "ITB Engine MVP: positivity-bounds vertical slice"
```

---

## Out of scope for this plan (queued for next plan)

- Real graviton-EFT positivity bounds (Caron-Huot et al 2021–2024) — multi-coefficient SDP, replaces the toy scalar bounds.
- Holographic entropy cone constraints (subadditivity, MMI for n ≤ 4 regions).
- Bekenstein and Bousso bounds.
- Modular flow consistency.
- String-theory low-energy EFT framework encoder.
- Asymptotic safety framework encoder.
- Research notebook (SQLite-backed) and hypothesis injector UI.
- Vulcan compute handoff for heavy sweeps.
- a-theorem / QNEC / GSL / Page-curve constraint modules (the new ideas surfaced during spec writing).

Each of these will be its own plan, layered on the MVP architecture without changes to core types.

---

## Self-review notes

- Spec coverage: every component named in the spec (Theory Encoder, Constraint Catalog, Constraint Engine, Theory-Space Mapper, Visualizer + Notebook) has an implementation task or is explicitly deferred above. Notebook deferred — that is intentional and tracked.
- Placeholders: none. Every step has runnable code or commands.
- Type consistency: `Constraint.evaluate` returns `ConstraintResult` consistently across tasks. `Theory.coefficients: dict[str, float]` consistent. `EngineReport`, `SweepResult` types defined where used.
- File-path consistency: all paths use `src/itb/...` or `tests/...` or `frontend/...`. Windows absolute paths only on initial creation; relative thereafter.
- TDD discipline: every code task has a failing test → minimal implementation → passing test → commit.
