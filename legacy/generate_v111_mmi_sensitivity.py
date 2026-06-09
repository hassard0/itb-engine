"""v1.11 — MMI prefactor sensitivity for LQG-induced.

LQG-induced fails BNOSSW MMI as currently encoded. Question: how robust
is this failure to the MMI prefactor? If the threshold is at MMI's
canonical value (1.0), the failure is robust. If it's far below, LQG
fails by a wide margin. If it's just below 1.0, the failure is on a
knife-edge and may not survive publication-grade encoding."""

from pathlib import Path

import numpy as np

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4, ScalarPositivityG6,
)
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.prefactor_sensitivity import (
    render_sensitivity_report,
    sweep_prefactor,
)
from itb.theory import Theory


class TunableBNOSSWMonogamy(Constraint):
    """BNOSSW MMI with a tunable prefactor on the harmonic-mean term:

        prefactor * g_4*g_6/(g_4+g_6) >= g_R2

    Default prefactor 1.0 reproduces v1.1 BNOSSWMonogamy. Lower prefactor
    is stricter (excludes more), higher is looser."""

    constraint_class = ConstraintClass.B_INFORMATION

    def __init__(self, prefactor: float = 1.0):
        self.prefactor = float(prefactor)
        self.name = f"bnossw_monogamy_pref_{prefactor:.3f}"
        self.citation = f"BNOSSW MMI with prefactor {prefactor:.3f}"

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        denom = g4 + g6
        if g4 == 0.0 and g6 == 0.0 and gR2 == 0.0:
            return ConstraintResult(self.name, True, 0.0, 0.0, {})
        if denom <= 0:
            return ConstraintResult(
                self.name,
                gR2 == 0,
                -abs(gR2) if gR2 != 0 else 0.0,
                -abs(gR2) if gR2 != 0 else 0.0,
                {},
            )
        margin = self.prefactor * (g4 * g6) / denom - gR2
        return ConstraintResult(self.name, margin >= 0, margin, margin, {})

    def gradient(self, theory: Theory) -> dict[str, float]:
        return {k: 0.0 for k in theory.coefficients}


def main() -> None:
    other_constraints = [
        ScalarPositivityG4(), ScalarPositivityG6(),
        ScalarConvexityG6vsG4(), BekensteinTight(),
    ]
    frameworks = [
        PureGR(), StringTreeEFT(), AsymptoticSafety(),
        LQGInduced(), CausalDynamicalTriangulation(),
    ]
    prefactor_values = [round(v, 3) for v in np.linspace(0.5, 2.5, 21)]

    results = sweep_prefactor(
        constraint_factory=TunableBNOSSWMonogamy,
        prefactor_values=prefactor_values,
        other_constraints=other_constraints,
        frameworks=frameworks,
    )

    print("BNOSSW MMI prefactor sensitivity:")
    print(f"  Prefactor swept: 0.5 to 2.5 in 21 steps (canonical = 1.0)")
    for r in results:
        trans = (
            f"transitions at prefactor = {r.transition_prefactor:.3f}"
            if r.transition_prefactor is not None
            else "no transition in range"
        )
        print(f"  {r.framework_name:<25} {trans}")

    md = render_sensitivity_report("BNOSSW MMI", results)
    md += "\n\n## Reading\n\n"
    md += (
        "If a framework's transition is at prefactor ≈ 1.0 (the canonical "
        "value), its status is on a knife-edge and may not survive "
        "publication-grade encoding. If the transition is far from 1.0, "
        "the failure is robust to prefactor choice.\n\n"
        "Particular attention: LQG-induced. The transition value tells us "
        "by how much the literal BNOSSW MMI form's prefactor can vary "
        "before LQG passes."
    )
    out = Path("docs/results/2026-05-08-v1.11-mmi-prefactor-sensitivity.md")
    out.write_text(md, encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
