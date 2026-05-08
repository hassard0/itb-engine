"""Multi-framework comparison report.

Run every available framework against the full constraint stack, plus the
fingerprint matrix, and produce a markdown summary suitable for handing to
a researcher: which frameworks survive, how fragile each is, where the
nearest violation lies, and how observably distinct they are from each other."""

from itb.constraints.base import Constraint
from itb.engine import check
from itb.fingerprint import fingerprint_framework, fingerprint_matrix
from itb.frameworks.base import Framework
from itb.perturbation import smallest_violating_perturbation


def render_framework_comparison(
    frameworks: list[Framework],
    constraints: list[Constraint],
) -> str:
    fingerprints = [fingerprint_framework(fw, constraints) for fw in frameworks]
    matrix = fingerprint_matrix(fingerprints)
    lines: list[str] = []
    lines.append("# ITB framework comparison")
    lines.append("")
    lines.append(f"Constraints: {len(constraints)} ({', '.join(c.name for c in constraints)})")
    lines.append("")
    lines.append("## Per-framework status")
    lines.append("")
    lines.append("| framework | feasible | n_binding | fragility distance | nearest binding constraint |")
    lines.append("|---|---|---|---|---|")
    for fw in frameworks:
        theory = fw.encode()
        report = check(theory, constraints)
        perturb = smallest_violating_perturbation(theory, constraints)
        nearest = perturb.binding_constraint or "—"
        lines.append(
            f"| {fw.name} "
            f"| {report.feasible} "
            f"| {sum(1 for r in report.results if abs(r.margin) < 1e-3)} "
            f"| {perturb.distance:.4f} "
            f"| {nearest} |"
        )
    lines.append("")
    lines.append("## Pairwise fingerprint distances")
    lines.append("")
    header = ["framework"] + [fp.framework_name for fp in fingerprints]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for i, fp in enumerate(fingerprints):
        row = [fp.framework_name] + [f"{matrix[i, j]:.3f}" for j in range(len(fingerprints))]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("## Coefficients")
    lines.append("")
    lines.append("| framework | g_4 | g_6 | g_R2 |")
    lines.append("|---|---|---|---|")
    for fp in fingerprints:
        c = fp.coefficients
        lines.append(
            f"| {fp.framework_name} "
            f"| {c.get('g_4', 0):.3f} "
            f"| {c.get('g_6', 0):.3f} "
            f"| {c.get('g_R2', 0):.3f} |"
        )
    return "\n".join(lines)
