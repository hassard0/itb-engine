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
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.constraints.scalar_positivity_sdp import ScalarPositivityG4SDP
from itb.engine import check
from itb.fisher import fisher_metric
from itb.fragility import fragility_map_2d
from itb.frameworks.base import Framework
from itb.frameworks.pure_gr import PureGR
from itb.importance import constraint_importance
from itb.mapper import sweep_2d
from itb.observables import ScalarForwardAmplitude
from itb.perturbation import smallest_violating_perturbation
from itb.plotting import (
    build_allowed_region_figure,
    build_binding_class_figure,
    build_fragility_figure,
    build_per_constraint_figure,
)
from itb.theory import Theory


CONSTRAINTS: dict[str, type[Constraint]] = {
    "scalar_positivity_g4": ScalarPositivityG4,
    "scalar_positivity_g6": ScalarPositivityG6,
    "scalar_convexity_g6_vs_g4": ScalarConvexityG6vsG4,
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
    color_by: str = "feasibility"  # feasibility | binding_class | per_constraint


class PerturbationRequest(BaseModel):
    coefficients: dict[str, float]
    constraints: list[str]


class FisherRequest(BaseModel):
    coefficients: dict[str, float]
    params: list[str]
    s_values: list[float]
    sigma: float


class FragilityRequest(BaseModel):
    x_param: str
    x_range: tuple[float, float]
    x_steps: int
    y_param: str
    y_range: tuple[float, float]
    y_steps: int
    constraints: list[str]


class ImportanceRequest(BaseModel):
    x_param: str
    x_range: tuple[float, float]
    x_steps: int
    y_param: str
    y_range: tuple[float, float]
    y_steps: int
    constraints: list[str]


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
    elif req.color_by == "per_constraint":
        fig = build_per_constraint_figure(result)
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


@app.post("/fragility")
def fragility(req: FragilityRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    fmap = fragility_map_2d(
        x_param=req.x_param,
        x_range=req.x_range,
        x_steps=req.x_steps,
        y_param=req.y_param,
        y_range=req.y_range,
        y_steps=req.y_steps,
        constraints=constraints,
    )
    fig = build_fragility_figure(fmap)
    return {
        "x_param": fmap.x_param,
        "x_values": fmap.x_values.tolist(),
        "y_param": fmap.y_param,
        "y_values": fmap.y_values.tolist(),
        "distance_grid": fmap.distance_grid.tolist(),
        "most_fragile_grid": fmap.most_fragile_grid.tolist(),
        "figure": json.loads(fig.to_json()),
    }


@app.post("/importance")
def importance(req: ImportanceRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    report = constraint_importance(
        x_param=req.x_param,
        x_range=req.x_range,
        x_steps=req.x_steps,
        y_param=req.y_param,
        y_range=req.y_range,
        y_steps=req.y_steps,
        constraints=constraints,
    )
    return {
        "baseline_allowed_count": report.baseline_allowed_count,
        "total_cells": report.total_cells,
        "scores": [
            {
                "constraint_name": s.constraint_name,
                "allowed_region_growth": s.allowed_region_growth,
                "growth_fraction": s.growth_fraction,
            }
            for s in report.scores
        ],
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
