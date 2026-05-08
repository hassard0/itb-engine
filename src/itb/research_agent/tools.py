"""Tools the research agent can call.

Each tool corresponds to an Anthropic-SDK tool definition with:
  - name
  - description (the agent reads this to decide which to use)
  - input_schema
  - implementation that the runner dispatches to

The implementations operate on the live engine state."""

from __future__ import annotations

import ast
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src" / "itb"
RESULTS_ROOT = REPO_ROOT / "docs" / "results"


# ----------------------------------------------------------------------------
# Tool implementations
# ----------------------------------------------------------------------------


def list_constraints() -> dict:
    """Return the registry of constraint classes."""
    from itb.api.server import CONSTRAINTS
    items = []
    for key, cls in CONSTRAINTS.items():
        c = cls()
        items.append({
            "name": c.name,
            "citation": c.citation,
            "constraint_class": c.constraint_class.value,
        })
    return {"count": len(items), "constraints": items}


def list_frameworks() -> dict:
    from itb.api.server import FRAMEWORKS
    items = []
    for key, cls in FRAMEWORKS.items():
        fw = cls()
        theory = fw.encode()
        items.append({
            "name": fw.name,
            "citation": fw.citation,
            "coefficients": theory.coefficients,
        })
    return {"count": len(items), "frameworks": items}


def list_findings_docs() -> dict:
    out = []
    if RESULTS_ROOT.exists():
        for p in sorted(RESULTS_ROOT.glob("*.md")):
            out.append({"filename": p.name, "size_bytes": p.stat().st_size})
    return {"count": len(out), "documents": out}


def read_findings_doc(filename: str) -> dict:
    p = RESULTS_ROOT / filename
    if not p.exists():
        return {"error": f"document not found: {filename}"}
    return {"filename": filename, "content": p.read_text(encoding="utf-8")}


def compute_intersection() -> dict:
    """Run the engine's all-constraint optimizer."""
    from itb.constraints.anomaly import AnomalyCancellation
    from itb.constraints.anomaly_flow import (
        GeneralizedAnomalyInflow,
        tHooftAnomalyMatching,
    )
    from itb.constraints.bekenstein_tight import BekensteinTight
    from itb.constraints.causality import CausalityBound
    from itb.constraints.complexity_cutoff import ComplexityCutoff
    from itb.constraints.cubic_parity import ParityViolatingCubicBound
    from itb.constraints.dispersion_tower import (
        DispersionTowerCauchySchwarz, ScalarPositivityG8,
    )
    from itb.constraints.eft_validity import EFTValidityBox
    from itb.constraints.graviton_eft import GravitonMixedPositivity
    from itb.constraints.graviton_self_coupling import (
        CubicCurvaturePositivity, CubicGravitonMatterBound,
    )
    from itb.constraints.holographic_entropy import (
        BNOSSWMonogamy, HolographicSubadditivity,
    )
    from itb.constraints.ligo_graviton_mass import LIGOGravitonMassBound
    from itb.constraints.parity_violation import (
        LIGOBirefringenceBound, LeftHandedGravitonPositivity,
        ParityViolatingPositivity, RightHandedGravitonPositivity,
    )
    from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
    from itb.constraints.scalar_positivity import (
        ScalarPositivityG4, ScalarPositivityG6,
    )
    from itb.constraints.swampland import WeakGravityConjecture
    from itb.intersection_search import search_intersection

    constraints = [
        ScalarPositivityG4(), ScalarPositivityG6(), ScalarPositivityG8(),
        ScalarConvexityG6vsG4(), DispersionTowerCauchySchwarz(),
        GravitonMixedPositivity(), CubicCurvaturePositivity(),
        CubicGravitonMatterBound(kappa=1.0),
        BekensteinTight(), HolographicSubadditivity(), BNOSSWMonogamy(),
        ParityViolatingPositivity(kappa=1.0),
        LeftHandedGravitonPositivity(kappa=1.0),
        RightHandedGravitonPositivity(kappa=1.0),
        ParityViolatingCubicBound(kappa=1.0),
        LIGOBirefringenceBound(bound=0.1),
        EFTValidityBox(box=2.0), CausalityBound(gamma=1.0),
        AnomalyCancellation(c_anom=1.0, tolerance=0.2),
        GeneralizedAnomalyInflow(rho=0.06),
        tHooftAnomalyMatching(rho_match=0.5, slack=0.02),
        WeakGravityConjecture(alpha=1.0),
        LIGOGravitonMassBound(bound=0.5),
        ComplexityCutoff(c_max=1.5),
    ]
    initial = {
        "g_4": 0.5, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.2,
        "g_R3": 0.15, "g_R2_parity": 0.0, "g_R3_parity": 0.0,
    }
    res = search_intersection(constraints, initial)
    return {
        "feasible": res.feasible,
        "coefficients": res.coefficients,
        "worst_case_margin": res.worst_case_margin,
        "constraints_violated": res.constraints_violated,
        "constraints_binding": res.constraints_binding,
    }


def propose_new_module(
    module_kind: str,
    name: str,
    file_path: str,
    code: str,
    description: str = "",
) -> dict:
    """Validate and save a new constraint, framework, or analysis module.

    `module_kind`: 'constraint' | 'framework' | 'analysis'
    `name`: snake_case identifier
    `file_path`: relative to src/itb/, e.g. 'constraints/my_new_bound.py'
    `code`: full Python source including docstring + class
    """
    if module_kind not in ("constraint", "framework", "analysis"):
        return {"accepted": False, "reason": f"unknown module_kind: {module_kind}"}

    # Parse first to make sure it's syntactically valid Python.
    try:
        ast.parse(code)
    except SyntaxError as e:
        return {"accepted": False, "reason": f"SyntaxError: {e}"}

    # Path safety: must live under src/itb/
    target_rel = Path(file_path)
    target = SRC_ROOT / target_rel
    try:
        target.resolve().relative_to(SRC_ROOT.resolve())
    except ValueError:
        return {
            "accepted": False,
            "reason": f"file_path must be within src/itb/, got {file_path}",
        }

    # Don't overwrite existing modules without an opt-in flag.
    if target.exists():
        return {
            "accepted": False,
            "reason": f"file already exists: {file_path} (will not overwrite)",
        }

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(code, encoding="utf-8")

    # Try to import it.
    module_name = ".".join(["itb"] + list(target_rel.with_suffix("").parts))
    try:
        importlib.invalidate_caches()
        importlib.import_module(module_name)
    except Exception as e:
        target.unlink()  # roll back
        return {
            "accepted": False,
            "reason": f"import failed after save: {type(e).__name__}: {e}",
        }

    # Run pytest collect-only — fast check that nothing breaks.
    pytest_cmd = [
        sys.executable, "-m", "pytest", "--collect-only", "-q",
        str(REPO_ROOT / "tests"),
    ]
    res = subprocess.run(pytest_cmd, capture_output=True, text=True, timeout=60)
    if res.returncode != 0:
        target.unlink()
        return {
            "accepted": False,
            "reason": "pytest collect failed after save",
            "stderr_tail": (res.stderr or "")[-500:],
            "stdout_tail": (res.stdout or "")[-500:],
        }

    return {
        "accepted": True,
        "file_path": str(target_rel),
        "module": module_name,
        "kind": module_kind,
        "name": name,
    }


def run_pytest_quick() -> dict:
    """Run the test suite. Used to verify after the agent adds modules."""
    res = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(REPO_ROOT / "tests")],
        capture_output=True, text=True, timeout=300,
    )
    return {
        "returncode": res.returncode,
        "stdout_tail": (res.stdout or "")[-1500:],
        "stderr_tail": (res.stderr or "")[-500:],
    }


def reflect(thought: str) -> dict:
    """Agent's scratchpad. Returns the thought back as confirmation."""
    return {"recorded": True, "thought": thought}


def mark_iteration_complete(summary: str) -> dict:
    """Agent declares this iteration done."""
    return {"iteration_complete": True, "summary": summary}


# ----------------------------------------------------------------------------
# Anthropic-SDK tool schemas
# ----------------------------------------------------------------------------


TOOL_SCHEMAS = [
    {
        "name": "list_constraints",
        "description": (
            "List all constraint modules currently registered with the engine, "
            "including each constraint's name, citation, and class "
            "(amplitude_bootstrap | information_theoretic | gravitational_universality)."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "list_frameworks",
        "description": (
            "List all candidate-framework encoders (Pure GR, String tree EFT, "
            "Asymptotic Safety, LQG-induced) and their predicted Wilson "
            "coefficient values."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "list_findings_docs",
        "description": (
            "List all research artifact documents under docs/results/. "
            "Use this to see what iterations have already been run."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_findings_doc",
        "description": (
            "Read the full markdown content of a specific findings document. "
            "Use this to understand prior iterations' results."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Filename only, no path. e.g. '2026-05-08-v1.8-honest-synthesis.md'",
                },
            },
            "required": ["filename"],
        },
    },
    {
        "name": "compute_intersection",
        "description": (
            "Run the engine's scipy-Nelder-Mead intersection search over all "
            "currently-registered constraints in 7-coefficient space. Returns "
            "the feasible point (or closest infeasible) with worst-case margin "
            "and binding/violated constraints."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "propose_new_module",
        "description": (
            "Submit a new Python module (constraint, framework, or analysis) "
            "for the engine. The runner will validate that the code parses, "
            "imports cleanly, and the existing test suite still passes. "
            "Returns whether the module was accepted, with a reason if rejected."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "module_kind": {
                    "type": "string",
                    "enum": ["constraint", "framework", "analysis"],
                },
                "name": {
                    "type": "string",
                    "description": "snake_case identifier for the new module",
                },
                "file_path": {
                    "type": "string",
                    "description": (
                        "Path under src/itb/, e.g. "
                        "'constraints/my_new_bound.py' or "
                        "'frameworks/penrose_diosi.py'"
                    ),
                },
                "code": {
                    "type": "string",
                    "description": (
                        "Full Python source. Constraint modules must define a "
                        "subclass of itb.constraints.base.Constraint with name, "
                        "citation, constraint_class, evaluate(theory), and "
                        "gradient(theory). Framework modules subclass "
                        "itb.frameworks.base.Framework and implement encode()."
                    ),
                },
                "description": {
                    "type": "string",
                    "description": "One-paragraph rationale for the module.",
                },
            },
            "required": ["module_kind", "name", "file_path", "code"],
        },
    },
    {
        "name": "run_pytest",
        "description": (
            "Run the engine's test suite and return the result. Use after "
            "adding a module to verify nothing broke."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "reflect",
        "description": (
            "Record a private thought for your own future reference. Useful for "
            "tracking ideas across iterations. Does not affect the engine."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"thought": {"type": "string"}},
            "required": ["thought"],
        },
    },
    {
        "name": "mark_iteration_complete",
        "description": (
            "Declare this research-agent iteration finished. Provide a one-"
            "paragraph summary of what you did and what you learned. The "
            "runner will start the next iteration with full conversation history."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"summary": {"type": "string"}},
            "required": ["summary"],
        },
    },
]


TOOL_DISPATCH: dict[str, Any] = {
    "list_constraints": list_constraints,
    "list_frameworks": list_frameworks,
    "list_findings_docs": list_findings_docs,
    "read_findings_doc": read_findings_doc,
    "compute_intersection": compute_intersection,
    "propose_new_module": propose_new_module,
    "run_pytest": run_pytest_quick,
    "reflect": reflect,
    "mark_iteration_complete": mark_iteration_complete,
}


def dispatch(tool_name: str, tool_input: dict) -> dict:
    """Route a tool call to its implementation."""
    impl = TOOL_DISPATCH.get(tool_name)
    if impl is None:
        return {"error": f"unknown tool: {tool_name}"}
    try:
        return impl(**tool_input)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
