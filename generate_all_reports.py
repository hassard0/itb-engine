"""Generate every scenario report and a cross-scenario synthesis."""

from itb.battery import run_full_battery
from itb.engine import check
from itb.frameworks.base import Framework
from itb.perturbation import smallest_violating_perturbation
from itb.scenarios import SCENARIOS


def per_scenario_report(scenario_factory):
    s = scenario_factory()
    md = run_full_battery(
        constraints=s.constraints,
        frameworks=s.frameworks,
        x_param="g_4", x_range=s.x_range, x_steps=21,
        y_param="g_6", y_range=s.y_range, y_steps=21,
        fixed_coefficients=s.fixed_coefficients,
        label=s.label,
    )
    header = f"# Scenario: {s.label}\n\n_{s.description}_\n\n"
    return s.label, header + md


def synthesis():
    rows: list[dict] = []
    for factory in SCENARIOS:
        s = factory()
        for fw in s.frameworks:
            theory = fw.encode()
            report = check(theory, s.constraints)
            fragility = smallest_violating_perturbation(theory, s.constraints).distance
            rows.append({
                "scenario": s.label,
                "framework": fw.name,
                "feasible": report.feasible,
                "fragility": fragility,
                "binding": report.binding or "—",
            })

    md_lines = ["# Cross-scenario synthesis", "", "Per-framework feasibility across all scenarios.", ""]
    md_lines.append("| scenario | framework | feasible | fragility | binding |")
    md_lines.append("|---|---|---|---|---|")
    for row in rows:
        md_lines.append(
            f"| {row['scenario']} | {row['framework']} | {row['feasible']} "
            f"| {row['fragility']:.4f} | {row['binding']} |"
        )

    md_lines.append("")
    md_lines.append("## Survival rates")
    md_lines.append("")
    survival: dict[str, dict[str, int]] = {}
    for row in rows:
        survival.setdefault(row["framework"], {"survived": 0, "total": 0})
        survival[row["framework"]]["total"] += 1
        if row["feasible"]:
            survival[row["framework"]]["survived"] += 1
    md_lines.append("| framework | survived / total | rate |")
    md_lines.append("|---|---|---|")
    for fw, s in sorted(survival.items()):
        rate = s["survived"] / s["total"] if s["total"] else 0
        md_lines.append(f"| {fw} | {s['survived']} / {s['total']} | {rate:.0%} |")

    md_lines.append("")
    md_lines.append("## Mean fragility per framework")
    md_lines.append("")
    fragilities: dict[str, list[float]] = {}
    for row in rows:
        fragilities.setdefault(row["framework"], []).append(row["fragility"])
    md_lines.append("| framework | mean fragility | min fragility | max fragility |")
    md_lines.append("|---|---|---|---|")
    for fw, vals in sorted(fragilities.items()):
        if vals:
            md_lines.append(
                f"| {fw} | {sum(vals)/len(vals):.4f} | {min(vals):.4f} | {max(vals):.4f} |"
            )
    return "\n".join(md_lines)


def main():
    import os
    os.makedirs("docs/results/scenarios", exist_ok=True)
    for factory in SCENARIOS:
        label, md = per_scenario_report(factory)
        path = f"docs/results/scenarios/2026-05-08-scenario-{label}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)
        print("wrote", path, len(md), "chars")
    syn = synthesis()
    with open("docs/results/2026-05-08-cross-scenario-synthesis.md", "w", encoding="utf-8") as f:
        f.write(syn)
    print("wrote synthesis", len(syn), "chars")


if __name__ == "__main__":
    main()
