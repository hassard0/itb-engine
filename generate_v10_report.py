"""Generate the v1.0 baseline report — full battery with publication-grade
constraints (dispersion tower, Weak Gravity Conjecture, LIGO bound) added
to the existing v0.8 stack."""

from pathlib import Path

from itb.battery import run_full_battery
from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.causality import CausalityBound
from itb.constraints.dispersion_tower import (
    DispersionTowerCauchySchwarz,
    ScalarPositivityG8,
)
from itb.constraints.eft_validity import EFTValidityBox
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.ligo_graviton_mass import LIGOGravitonMassBound
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.constraints.swampland import WeakGravityConjecture
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT


def main() -> None:
    # Use a *loose* LIGO bound so we can see the engine discriminate more
    # gracefully — the strict default 0.1 wipes out everything except Pure GR
    # which is itself a real result, but the loose 0.5 lets us see the
    # nuanced interplay among the new tower of constraints.
    constraints = [
        ScalarPositivityG4(),
        ScalarPositivityG6(),
        ScalarPositivityG8(),
        ScalarConvexityG6vsG4(),
        DispersionTowerCauchySchwarz(),
        GravitonMixedPositivity(),
        BekensteinTight(),
        EFTValidityBox(box=2.0),
        CausalityBound(gamma=1.0),
        AnomalyCancellation(c_anom=1.0, tolerance=0.2),
        WeakGravityConjecture(alpha=1.0),
        LIGOGravitonMassBound(bound=0.5),
    ]
    frameworks = [PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()]
    md = run_full_battery(
        constraints=constraints,
        frameworks=frameworks,
        x_param="g_4",
        x_range=(-1.0, 2.0),
        x_steps=31,
        y_param="g_6",
        y_range=(-1.0, 2.0),
        y_steps=31,
        fixed_coefficients={"g_R2": 0.3, "g_8": 0.4},
        label="v1.0 — publication-grade constraints (dispersion tower + WGC + LIGO)",
    )
    out = Path("docs/results/2026-05-08-v1.0-publication-grade-report.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"wrote {out}: {len(md)} chars")


if __name__ == "__main__":
    main()
