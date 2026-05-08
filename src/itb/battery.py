"""Full-battery pipeline: run every analysis the engine has against a
chosen scenario and produce a single comprehensive markdown report.

This is the engine in "produce a research artifact" mode: one input scenario
(constraint set + framework set + 2D sweep window) → one self-contained
report covering: per-framework feasibility, fragility, fingerprints,
constraint importance, A/B duality, allowed-region size, phase decomposition,
boundedness, and adversarial bootstrap.

The output is a single markdown string; the writer commits it to the repo
as a versioned `docs/results/...md` artifact."""

from datetime import datetime, timezone

from itb.adversarial import adversarial_bootstrap
from itb.completeness import check_boundedness
from itb.constraints.base import Constraint
from itb.duality import cross_class_duality_2d
from itb.engine import check
from itb.fingerprint import fingerprint_framework, fingerprint_matrix
from itb.frameworks.base import Framework
from itb.importance import constraint_importance
from itb.mapper import sweep_2d
from itb.phase_components import phase_components
from itb.perturbation import smallest_violating_perturbation


def run_full_battery(
    *,
    constraints: list[Constraint],
    frameworks: list[Framework],
    x_param: str = "g_4",
    x_range: tuple[float, float] = (-1.0, 2.0),
    x_steps: int = 31,
    y_param: str = "g_6",
    y_range: tuple[float, float] = (-1.0, 2.0),
    y_steps: int = 31,
    fixed_coefficients: dict[str, float] | None = None,
    label: str = "default-scenario",
) -> str:
    fixed = dict(fixed_coefficients or {})
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out: list[str] = []
    out.append(f"# ITB Engine — Full Battery: {label}")
    out.append("")
    out.append(f"_Generated: {timestamp}_")
    out.append("")
    out.append(f"- Constraints: {len(constraints)}")
    out.append(f"- Frameworks: {len(frameworks)}")
    out.append(f"- Sweep: ({x_param} ∈ {x_range}, {x_steps} steps) × ({y_param} ∈ {y_range}, {y_steps} steps)")
    if fixed:
        out.append(f"- Fixed coefficients: {fixed}")
    out.append("")

    out.append("## Constraints in scope")
    out.append("")
    out.append("| name | class |")
    out.append("|---|---|")
    for c in constraints:
        out.append(f"| {c.name} | {c.constraint_class.value} |")
    out.append("")

    out.append("## Per-framework status")
    out.append("")
    out.append("| framework | feasible | n_binding | fragility distance | nearest binding |")
    out.append("|---|---|---|---|---|")
    for fw in frameworks:
        theory = fw.encode()
        report = check(theory, constraints)
        fragility = smallest_violating_perturbation(theory, constraints).distance
        nearest = (
            smallest_violating_perturbation(theory, constraints).binding_constraint
            if report.feasible else (report.binding or "—")
        )
        n_binding = sum(1 for r in report.results if abs(r.margin) < 1e-3)
        out.append(
            f"| {fw.name} | {report.feasible} | {n_binding} | {fragility:.4f} | {nearest} |"
        )
    out.append("")

    out.append("## Coefficients")
    out.append("")
    out.append("| framework | g_4 | g_6 | g_R2 |")
    out.append("|---|---|---|---|")
    for fw in frameworks:
        c = fw.encode().coefficients
        out.append(
            f"| {fw.name} | {c.get('g_4', 0):.3f} | {c.get('g_6', 0):.3f} | {c.get('g_R2', 0):.3f} |"
        )
    out.append("")

    out.append("## Pairwise framework distance (fingerprint)")
    out.append("")
    fps = [fingerprint_framework(fw, constraints) for fw in frameworks]
    matrix = fingerprint_matrix(fps)
    header = ["framework"] + [fp.framework_name for fp in fps]
    out.append("| " + " | ".join(header) + " |")
    out.append("|" + "|".join(["---"] * len(header)) + "|")
    for i, fp in enumerate(fps):
        row = [fp.framework_name] + [f"{matrix[i, j]:.3f}" for j in range(len(fps))]
        out.append("| " + " | ".join(row) + " |")
    out.append("")

    out.append("## 2D sweep summary")
    out.append("")
    sweep = sweep_2d(
        x_param=x_param, x_range=x_range, x_steps=x_steps,
        y_param=y_param, y_range=y_range, y_steps=y_steps,
        constraints=constraints, fixed_coefficients=fixed,
    )
    n_total = sweep.feasibility_grid.size
    n_feasible = int(sweep.feasibility_grid.sum())
    out.append(f"- Allowed cells: {n_feasible} / {n_total} ({100 * n_feasible / n_total:.1f} %)")
    phases = phase_components(sweep)
    out.append(f"- Phase components: {phases.n_components} (sizes {phases.component_sizes})")
    out.append("")

    out.append("## Constraint importance ranking")
    out.append("")
    imp = constraint_importance(
        x_param=x_param, x_range=x_range, x_steps=x_steps,
        y_param=y_param, y_range=y_range, y_steps=y_steps,
        constraints=constraints, fixed_coefficients=fixed,
    )
    out.append(f"- Baseline allowed: {imp.baseline_allowed_count} / {imp.total_cells}")
    out.append("")
    out.append("| constraint | growth (cells) | growth fraction |")
    out.append("|---|---|---|")
    for s in imp.scores:
        out.append(f"| {s.constraint_name} | {s.allowed_region_growth} | {s.growth_fraction:.3f} |")
    out.append("")

    try:
        dual = cross_class_duality_2d(
            constraints=constraints,
            x_param=x_param, x_range=x_range, x_steps=x_steps,
            y_param=y_param, y_range=y_range, y_steps=y_steps,
            fixed_coefficients=fixed,
        )
        out.append("## Cross-class duality (A vs B)")
        out.append("")
        out.append(f"- IoU(A, B): {dual.iou:.4f}")
        out.append(f"- A only: {dual.a_only_count} cells")
        out.append(f"- B only: {dual.b_only_count} cells")
        out.append(f"- Both: {dual.both_count} cells")
        out.append("")
    except ValueError:
        out.append("## Cross-class duality (A vs B)")
        out.append("")
        out.append("_skipped: requires at least one constraint in each of class A and class B_")
        out.append("")

    out.append("## Boundedness")
    out.append("")
    bound_report = check_boundedness(
        constraints=constraints,
        params=[x_param, y_param],
        starting_box=2.0,
        max_box=8.0,
        steps_per_axis=11,
    )
    out.append(f"- Bounded: {bound_report.bounded}")
    out.append(f"- Final box size tested: {bound_report.final_box_size}")
    if not bound_report.bounded:
        out.append(f"- Unbounded directions: {bound_report.unbounded_directions}")
    out.append("")

    out.append("## Adversarial bootstrap (analytic center)")
    out.append("")
    initial = {x_param: 0.5, y_param: 0.5}
    if "g_R2" in fixed:
        initial["g_R2"] = fixed["g_R2"]
    elif any(p == "g_R2" for fw in frameworks for p in fw.encode().coefficients):
        initial["g_R2"] = 0.2
    adv = adversarial_bootstrap(constraints=constraints, initial_guess=initial)
    out.append(f"- Adversarial point: {adv.theory.coefficients}")
    out.append(f"- Simultaneously binding constraints: {adv.n_binding}")
    out.append(f"  - {', '.join(adv.binding_names) if adv.binding_names else '—'}")
    out.append(f"- Objective value: {adv.objective_value:.6e}")
    out.append("")

    out.append("---")
    out.append("")
    out.append("_End of full-battery report._")
    return "\n".join(out)
