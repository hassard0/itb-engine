"""v1.12 — Systematic robustness map across the most-binding constraints.

For each of five constraints with O(1) prefactors that have shown up as
binding in earlier iterations, sweep the prefactor and record per-framework
transition values. Compile into a single 'robustness map' table.

The map answers: for each (framework, constraint) pair, how robust is the
framework's status to a 50% perturbation of the constraint's prefactor?
A transition near canonical = knife-edge, far from canonical = robust."""

from pathlib import Path

import numpy as np

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4, ScalarPositivityG6,
)
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.prefactor_sensitivity import sweep_prefactor
from itb.theory import Theory


def _result(name, ok, m):
    return ConstraintResult(name, m >= 0, m, m, {})


# Tunable versions of the five constraints we'll sweep.

class TunableBekenstein(Constraint):
    constraint_class = ConstraintClass.B_INFORMATION
    def __init__(self, prefactor: float = 0.5):
        self.prefactor = float(prefactor)
        self.name = f"bekenstein_pref_{prefactor:.3f}"
        self.citation = ""
    def evaluate(self, theory):
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        m = self.prefactor * g4 * g6 - gR2 * gR2
        return _result(self.name, m >= 0, m)
    def gradient(self, theory):
        return {k: 0.0 for k in theory.coefficients}


class TunableMMI(Constraint):
    constraint_class = ConstraintClass.B_INFORMATION
    def __init__(self, prefactor: float = 1.0):
        self.prefactor = float(prefactor)
        self.name = f"mmi_pref_{prefactor:.3f}"
        self.citation = ""
    def evaluate(self, theory):
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        denom = g4 + g6
        if g4 == 0 and g6 == 0 and gR2 == 0:
            return _result(self.name, True, 0.0)
        if denom <= 0:
            mar = -abs(gR2) if gR2 != 0 else 0.0
            return _result(self.name, mar >= 0, mar)
        m = self.prefactor * (g4 * g6) / denom - gR2
        return _result(self.name, m >= 0, m)
    def gradient(self, theory):
        return {k: 0.0 for k in theory.coefficients}


class TunableComplexity(Constraint):
    constraint_class = ConstraintClass.C_UNIVERSALITY
    weights = {"g_4": 1.0, "g_6": 2.0, "g_8": 3.0, "g_R2": 1.0,
               "g_R3": 2.0, "g_R2_parity": 1.0, "g_R3_parity": 2.0}
    def __init__(self, prefactor: float = 1.5):
        self.prefactor = float(prefactor)
        self.name = f"complexity_cmax_{prefactor:.3f}"
        self.citation = ""
    def evaluate(self, theory):
        c = sum(self.weights.get(k, 1.0) * v * v for k, v in theory.coefficients.items())
        m = self.prefactor - c
        return _result(self.name, m >= 0, m)
    def gradient(self, theory):
        return {k: 0.0 for k in theory.coefficients}


class TunableWGC(Constraint):
    constraint_class = ConstraintClass.C_UNIVERSALITY
    def __init__(self, prefactor: float = 1.0):
        self.prefactor = float(prefactor)
        self.name = f"wgc_alpha_{prefactor:.3f}"
        self.citation = ""
    def evaluate(self, theory):
        g4 = theory.coefficients.get("g_4", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        if g4 < 0:
            return _result(self.name, False, -1.0)
        m = self.prefactor * (g4 ** 0.5) - gR2
        return _result(self.name, m >= 0, m)
    def gradient(self, theory):
        return {k: 0.0 for k in theory.coefficients}


class TunableCubicGM(Constraint):
    """g_R3 <= prefactor * g_4^2"""
    constraint_class = ConstraintClass.A_AMPLITUDE
    def __init__(self, prefactor: float = 1.0):
        self.prefactor = float(prefactor)
        self.name = f"cubic_gm_{prefactor:.3f}"
        self.citation = ""
    def evaluate(self, theory):
        g4 = theory.coefficients.get("g_4", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        m = self.prefactor * g4 * g4 - gR3
        return _result(self.name, m >= 0, m)
    def gradient(self, theory):
        return {k: 0.0 for k in theory.coefficients}


def main() -> None:
    other_constraints = [
        ScalarPositivityG4(), ScalarPositivityG6(),
        ScalarConvexityG6vsG4(),
    ]
    frameworks = [
        PureGR(), StringTreeEFT(), AsymptoticSafety(),
        LQGInduced(), CausalDynamicalTriangulation(),
    ]
    sweeps = [
        ("BNOSSW MMI",       TunableMMI,       1.0,  np.linspace(0.5, 2.5, 21)),
        ("Bekenstein-tight", TunableBekenstein, 0.5,  np.linspace(0.1, 1.5, 15)),
        ("Complexity cutoff", TunableComplexity, 1.5, np.linspace(0.5, 3.0, 26)),
        ("Weak Gravity",     TunableWGC,       1.0,  np.linspace(0.2, 2.0, 19)),
        ("Cubic graviton-matter", TunableCubicGM, 1.0, np.linspace(0.2, 2.0, 19)),
    ]

    rows = []
    for label, factory, canonical, vals in sweeps:
        results = sweep_prefactor(
            constraint_factory=factory,
            prefactor_values=[round(v, 3) for v in vals],
            other_constraints=other_constraints,
            frameworks=frameworks,
        )
        for r in results:
            rel = (
                None if r.transition_prefactor is None
                else (r.transition_prefactor / canonical) - 1.0
            )
            rows.append({
                "framework": r.framework_name,
                "constraint": label,
                "canonical": canonical,
                "transition": r.transition_prefactor,
                "relative_margin": rel,
            })

    # Pivot to a per-framework table
    print("=" * 80)
    print(f"{'framework':<22} | {'constraint':<25} | transition | rel margin")
    print("-" * 80)
    for row in rows:
        trans = f"{row['transition']:.3f}" if row['transition'] is not None else "(no flip)"
        rel = (
            f"{row['relative_margin']*100:+5.1f}%"
            if row['relative_margin'] is not None else "  (n/a)"
        )
        print(f"{row['framework']:<22} | {row['constraint']:<25} | {trans:<10} | {rel}")

    md_lines: list[str] = []
    md_lines.append("# v1.12 — Robustness Map (5 constraints x 5 frameworks)")
    md_lines.append("")
    md_lines.append(
        "Per (framework, constraint) pair: the prefactor at which the "
        "framework's status flips, and the relative margin from canonical."
    )
    md_lines.append("")
    md_lines.append(
        "**Reading:** `+10%` = framework would still pass at 10% tighter "
        "prefactor (robust). `-10%` = framework currently passes a 10%-looser "
        "prefactor than canonical (knife-edge). `(no flip)` = framework's "
        "status doesn't change across the swept range (very robust)."
    )
    md_lines.append("")
    constraint_labels = [c[0] for c in sweeps]
    framework_names = [f.name for f in frameworks]
    md_lines.append("| framework | " + " | ".join(constraint_labels) + " |")
    md_lines.append("|---|" + "|".join(["---"] * len(constraint_labels)) + "|")
    by_fw_const = {(r["framework"], r["constraint"]): r for r in rows}
    for fw in framework_names:
        cells = []
        for cl in constraint_labels:
            row = by_fw_const.get((fw, cl))
            if row is None:
                cells.append("—")
                continue
            if row["transition"] is None:
                cells.append("(no flip)")
                continue
            margin_pct = row["relative_margin"] * 100
            cells.append(f"{row['transition']:.3f} ({margin_pct:+.0f}%)")
        md_lines.append(f"| {fw} | " + " | ".join(cells) + " |")
    md_lines.append("")
    md_lines.append("## Knife-edges (relative margin within ±10%)")
    md_lines.append("")
    md_lines.append("| framework | constraint | transition | margin |")
    md_lines.append("|---|---|---|---|")
    knife_count = 0
    for r in rows:
        if r["relative_margin"] is None:
            continue
        if abs(r["relative_margin"]) <= 0.10:
            knife_count += 1
            md_lines.append(
                f"| {r['framework']} | {r['constraint']} | "
                f"{r['transition']:.3f} | {r['relative_margin']*100:+.1f}% |"
            )
    if knife_count == 0:
        md_lines.append("| (none in this sweep) | | | |")
    md_lines.append("")
    md_lines.append(f"**Knife-edges found:** {knife_count}")
    md_lines.append("")
    md_lines.append(
        "## What this means for the next research-grade encoding pass\n\n"
        "Knife-edge findings are the ones whose status would flip under a "
        "10% perturbation of the constraint's prefactor. They are the "
        "highest-priority targets for replacing toy prefactors with "
        "publication-grade values: a 5% better number could change the "
        "engine's framework discrimination."
    )

    out = Path("docs/results/2026-05-08-v1.12-robustness-map.md")
    out.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
