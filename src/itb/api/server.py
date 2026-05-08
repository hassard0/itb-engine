"""FastAPI server exposing engine, mapper, perturbation, fisher, and
metadata to a localhost UI."""

import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from itb.adversarial import adversarial_bootstrap
from itb.completeness import check_boundedness
from itb.duality import cross_class_duality_2d
from itb.fingerprint import (
    fingerprint_distance,
    fingerprint_framework,
    fingerprint_matrix,
)
from itb.sensitivity import feasibility_probability, sensitivity_grid_2d
from itb.voxel import slice_voxel, voxel_sweep_3d
from itb.constraints.base import Constraint
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.causality import CausalityBound
from itb.constraints.dispersion_tower import (
    DispersionTowerCauchySchwarz,
    ScalarPositivityG8,
)
from itb.constraints.holographic_entropy import (
    BNOSSWMonogamy,
    HolographicSubadditivity,
)
from itb.constraints.eft_validity import EFTValidityBox
from itb.constraints.experimental import MeasuredWilsonCoefficient
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.ligo_graviton_mass import LIGOGravitonMassBound
from itb.constraints.swampland import WeakGravityConjecture
from itb.constraints.spin_decomposed import (
    SpinTwoPositivity,
    SpinZeroPositivity,
)
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
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.importance import constraint_importance
from itb.mapper import sweep_2d
from itb.observables import ScalarForwardAmplitude
from itb.battery import run_full_battery
from itb.path_distance import path_through_allowed_region
from itb.perturbation import smallest_violating_perturbation
from itb.phase_components import phase_components
from itb.report import render_framework_comparison
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
    "graviton_mixed_positivity": GravitonMixedPositivity,
    "bekenstein_tight": BekensteinTight,
    "eft_validity_box": EFTValidityBox,
    "spin_zero_positivity": SpinZeroPositivity,
    "spin_two_positivity": SpinTwoPositivity,
    "causality_bound": CausalityBound,
    "anomaly_cancellation": AnomalyCancellation,
    "scalar_positivity_g8": ScalarPositivityG8,
    "dispersion_tower_g6_squared_bound": DispersionTowerCauchySchwarz,
    "weak_gravity_conjecture": WeakGravityConjecture,
    "ligo_graviton_mass_bound": LIGOGravitonMassBound,
    "holographic_subadditivity": HolographicSubadditivity,
    "bnossw_monogamy": BNOSSWMonogamy,
    "scalar_positivity_g4_sdp": ScalarPositivityG4SDP,
}

FRAMEWORKS: dict[str, type[Framework]] = {
    "pure_gr": PureGR,
    "string_tree_eft": StringTreeEFT,
    "asymptotic_safety": AsymptoticSafety,
    "lqg_induced": LQGInduced,
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
    overlay_frameworks: list[str] | None = None


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


class AdversarialRequest(BaseModel):
    initial_guess: dict[str, float]
    constraints: list[str]


class PathRequest(BaseModel):
    start: dict[str, float]
    end: dict[str, float]
    x_param: str
    x_range: tuple[float, float]
    x_steps: int
    y_param: str
    y_range: tuple[float, float]
    y_steps: int
    constraints: list[str]


class CompletenessRequest(BaseModel):
    constraints: list[str]
    params: list[str]
    starting_box: float = 2.0
    max_box: float = 8.0
    steps_per_axis: int = 11


class SensitivityProbabilityRequest(BaseModel):
    coefficients: dict[str, float]
    constraints: list[str]
    sigma: float = 0.1
    n_samples: int = 200


class SensitivityGridRequest(BaseModel):
    x_param: str
    x_range: tuple[float, float]
    x_steps: int
    y_param: str
    y_range: tuple[float, float]
    y_steps: int
    constraints: list[str]
    sigma: float = 0.1
    n_samples: int = 80
    fixed_coefficients: dict[str, float] | None = None


class DualityRequest(BaseModel):
    constraints: list[str]
    x_param: str
    x_range: tuple[float, float]
    x_steps: int
    y_param: str
    y_range: tuple[float, float]
    y_steps: int
    fixed_coefficients: dict[str, float] | None = None


class VoxelRequest(BaseModel):
    x_param: str; x_range: tuple[float, float]; x_steps: int
    y_param: str; y_range: tuple[float, float]; y_steps: int
    z_param: str; z_range: tuple[float, float]; z_steps: int
    constraints: list[str]
    slice_axis: str | None = None
    slice_value: float | None = None


class FingerprintRequest(BaseModel):
    frameworks: list[str]
    constraints: list[str]


class MeasurementRequest(BaseModel):
    coefficient_name: str
    central_value: float
    sigma: float
    sigma_threshold: float = 2.0
    experiment_label: str = "synthetic"
    coefficients: dict[str, float]


class FrameworkReportRequest(BaseModel):
    frameworks: list[str]
    constraints: list[str]


class BatteryRequest(BaseModel):
    constraints: list[str]
    frameworks: list[str]
    x_param: str = "g_4"
    x_range: tuple[float, float] = (-1.0, 2.0)
    x_steps: int = 21
    y_param: str = "g_6"
    y_range: tuple[float, float] = (-1.0, 2.0)
    y_steps: int = 21
    fixed_coefficients: dict[str, float] | None = None
    label: str = "battery"


class PhasesRequest(BaseModel):
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

    overlay = []
    if req.overlay_frameworks:
        import plotly.graph_objects as go
        for fw_name in req.overlay_frameworks:
            if fw_name not in FRAMEWORKS:
                continue
            theory = FRAMEWORKS[fw_name]().encode()
            x_val = theory.coefficients.get(req.x_param)
            y_val = theory.coefficients.get(req.y_param)
            if x_val is None or y_val is None:
                continue
            fig.add_trace(go.Scatter(
                x=[x_val],
                y=[y_val],
                mode="markers+text",
                marker=dict(size=14, color="#1f1f1f", symbol="star"),
                text=[fw_name],
                textposition="top center",
                name=fw_name,
                hovertemplate=(
                    f"{fw_name}<br>"
                    f"{req.x_param}=%{{x:.3f}}<br>"
                    f"{req.y_param}=%{{y:.3f}}<extra></extra>"
                ),
            ))
            overlay.append({
                "name": fw_name,
                "coefficients": theory.coefficients,
                req.x_param: x_val,
                req.y_param: y_val,
            })

    return {
        "x_param": result.x_param,
        "x_values": result.x_values.tolist(),
        "y_param": result.y_param,
        "y_values": result.y_values.tolist(),
        "grid": result.feasibility_grid.tolist(),
        "binding_grid": result.binding_grid.tolist(),
        "binding_class_grid": result.binding_class_grid.tolist(),
        "figure": json.loads(fig.to_json()),
        "overlay_frameworks": overlay,
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


@app.post("/adversarial")
def adversarial(req: AdversarialRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    res = adversarial_bootstrap(constraints=constraints, initial_guess=req.initial_guess)
    return {
        "coefficients": res.theory.coefficients,
        "n_binding": res.n_binding,
        "binding_names": res.binding_names,
        "objective_value": res.objective_value,
    }


@app.post("/path")
def path(req: PathRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    res = path_through_allowed_region(
        start=req.start,
        end=req.end,
        x_param=req.x_param,
        x_range=req.x_range,
        x_steps=req.x_steps,
        y_param=req.y_param,
        y_range=req.y_range,
        y_steps=req.y_steps,
        constraints=constraints,
    )
    return {
        "connected": res.connected,
        "distance": res.distance if res.connected else None,
        "path_points": res.path_points,
    }


@app.post("/completeness")
def completeness(req: CompletenessRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    report = check_boundedness(
        constraints=constraints,
        params=req.params,
        starting_box=req.starting_box,
        max_box=req.max_box,
        steps_per_axis=req.steps_per_axis,
    )
    return {
        "bounded": report.bounded,
        "final_box_size": report.final_box_size,
        "unbounded_directions": report.unbounded_directions,
        "fraction_allowed_at_final_box": report.fraction_allowed_at_final_box,
    }


@app.post("/sensitivity/probability")
def sensitivity_probability(req: SensitivityProbabilityRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    res = feasibility_probability(
        nominal=req.coefficients,
        constraints=constraints,
        sigma=req.sigma,
        n_samples=req.n_samples,
    )
    return {
        "nominal_feasible": res.nominal_feasible,
        "p_feasible": res.p_feasible,
        "n_samples": res.n_samples,
        "margin_mean": res.margin_mean,
        "margin_std": res.margin_std,
    }


@app.post("/sensitivity/grid")
def sensitivity_grid(req: SensitivityGridRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    res = sensitivity_grid_2d(
        x_param=req.x_param, x_range=req.x_range, x_steps=req.x_steps,
        y_param=req.y_param, y_range=req.y_range, y_steps=req.y_steps,
        constraints=constraints,
        sigma=req.sigma, n_samples=req.n_samples,
        fixed_coefficients=req.fixed_coefficients,
    )
    return {
        "x_param": res["x_param"],
        "x_values": res["x_values"].tolist(),
        "y_param": res["y_param"],
        "y_values": res["y_values"].tolist(),
        "p_grid": res["p_grid"].tolist(),
    }


@app.post("/duality")
def duality(req: DualityRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    rep = cross_class_duality_2d(
        constraints=constraints,
        x_param=req.x_param, x_range=req.x_range, x_steps=req.x_steps,
        y_param=req.y_param, y_range=req.y_range, y_steps=req.y_steps,
        fixed_coefficients=req.fixed_coefficients,
    )
    return {
        "iou": rep.iou,
        "a_only_count": rep.a_only_count,
        "b_only_count": rep.b_only_count,
        "both_count": rep.both_count,
        "x_values": rep.x_values.tolist(),
        "y_values": rep.y_values.tolist(),
    }


@app.post("/voxel")
def voxel(req: VoxelRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    res = voxel_sweep_3d(
        x_param=req.x_param, x_range=req.x_range, x_steps=req.x_steps,
        y_param=req.y_param, y_range=req.y_range, y_steps=req.y_steps,
        z_param=req.z_param, z_range=req.z_range, z_steps=req.z_steps,
        constraints=constraints,
    )
    out: dict = {
        "axes": {k: v.tolist() for k, v in res.axes.items()},
        "shape": list(res.feasibility_voxels.shape),
        "total_feasible_voxels": int(res.feasibility_voxels.sum()),
    }
    if req.slice_axis is not None and req.slice_value is not None:
        sl = slice_voxel(res, fixed_axis=req.slice_axis, fixed_value=req.slice_value)
        out["slice"] = {
            "fixed_axis": sl["fixed_axis"],
            "fixed_value": sl["fixed_value"],
            "x_param": sl["x_param"],
            "x_values": sl["x_values"].tolist(),
            "y_param": sl["y_param"],
            "y_values": sl["y_values"].tolist(),
            "feasibility_grid": sl["feasibility_grid"].tolist(),
        }
    return out


@app.post("/fingerprint")
def fingerprint(req: FingerprintRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    fps = []
    for fname in req.frameworks:
        if fname not in FRAMEWORKS:
            raise HTTPException(400, f"Unknown framework: {fname}")
        fps.append(fingerprint_framework(FRAMEWORKS[fname](), constraints))
    matrix = fingerprint_matrix(fps).tolist()
    return {
        "fingerprints": [
            {
                "framework_name": fp.framework_name,
                "coefficients": fp.coefficients,
                "feasible": fp.feasible,
                "fragility_distance": fp.fragility_distance,
                "n_binding": fp.n_binding,
            }
            for fp in fps
        ],
        "distance_matrix": matrix,
    }


@app.post("/battery")
def battery(req: BatteryRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    fws = []
    for n in req.frameworks:
        if n not in FRAMEWORKS:
            raise HTTPException(400, f"Unknown framework: {n}")
        fws.append(FRAMEWORKS[n]())
    md = run_full_battery(
        constraints=constraints, frameworks=fws,
        x_param=req.x_param, x_range=req.x_range, x_steps=req.x_steps,
        y_param=req.y_param, y_range=req.y_range, y_steps=req.y_steps,
        fixed_coefficients=req.fixed_coefficients,
        label=req.label,
    )
    return {"markdown": md, "length": len(md)}


@app.post("/measurement")
def measurement(req: MeasurementRequest) -> dict:
    c = MeasuredWilsonCoefficient(
        coefficient_name=req.coefficient_name,
        central_value=req.central_value,
        sigma=req.sigma,
        sigma_threshold=req.sigma_threshold,
        experiment_label=req.experiment_label,
    )
    r = c.evaluate(Theory(coefficients=req.coefficients))
    return {
        "constraint_name": r.constraint_name,
        "satisfied": r.satisfied,
        "margin": r.margin,
        "details": r.details,
    }


@app.post("/framework-report")
def framework_report(req: FrameworkReportRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    fws = []
    for n in req.frameworks:
        if n not in FRAMEWORKS:
            raise HTTPException(400, f"Unknown framework: {n}")
        fws.append(FRAMEWORKS[n]())
    md = render_framework_comparison(fws, constraints)
    return {"markdown": md, "framework_count": len(fws)}


@app.post("/phases")
def phases(req: PhasesRequest) -> dict:
    constraints = _resolve_constraints(req.constraints)
    sweep = sweep_2d(
        x_param=req.x_param,
        x_range=req.x_range,
        x_steps=req.x_steps,
        y_param=req.y_param,
        y_range=req.y_range,
        y_steps=req.y_steps,
        constraints=constraints,
    )
    dec = phase_components(sweep)
    return {
        "n_components": dec.n_components,
        "component_sizes": dec.component_sizes,
        "label_grid": dec.label_grid.tolist(),
        "x_values": sweep.x_values.tolist(),
        "y_values": sweep.y_values.tolist(),
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
