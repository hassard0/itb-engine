"""v1.5 first-disagreement analysis: where do candidate frameworks first
measurably diverge?

For each pair of frameworks, scan a range of observables (forward amplitudes
at different kinematic points) and find the maximum signal-to-noise ratio.
The pair × observable with highest S/N is the experimental target that
first cleanly distinguishes the frameworks.

Output: a markdown ranking + the engine's first answer to 'where would we
see real disagreement between candidate UV completions?'"""

from pathlib import Path

import numpy as np

from itb.first_disagreement import first_disagreement, render_disagreement_report
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.observables import ScalarForwardAmplitude


def main() -> None:
    frameworks = [PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced()]
    # Six observables at different kinematic regimes, each modeling a
    # specific experimental setup (low-energy gravitational tests, mid-s
    # particle physics, high-s collider regimes).
    observables = {
        "low_s_precision_tests": ScalarForwardAmplitude(np.array([0.1, 0.2, 0.3])),
        "mid_s_collider_regime": ScalarForwardAmplitude(np.array([0.5, 1.0, 1.5])),
        "high_s_TeV_regime": ScalarForwardAmplitude(np.array([2.0, 3.0, 4.0])),
    }
    # Use a representative noise floor of 0.05 in our toy units.
    report = first_disagreement(frameworks, observables, sigma=0.05)
    md = render_disagreement_report(report)
    md += "\n\n## Notes\n\n"
    md += (
        "Each row is a candidate-framework pair × observable. S/N gives the "
        "signal-to-noise ratio: how many sigmas of measurement separate the "
        "two frameworks at that observable's strongest kinematic point. "
        "The top row is where to look first.\n\n"
        "Note: noise floor σ=0.05 is illustrative. Real experimental "
        "sensitivities span 6+ orders of magnitude. The architecture is "
        "research-grade; the noise floor needs replacement with publication "
        "values from each experiment's design report."
    )
    out = Path("docs/results/2026-05-08-v1.5-first-disagreement.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"wrote {out}: {len(md)} chars")
    if report.best_pair is not None:
        print(
            f"\nTop pair: {report.best_pair.framework_a} ↔ "
            f"{report.best_pair.framework_b}\n"
            f"Best observable: {report.best_pair.observable}\n"
            f"S/N: {report.best_pair.max_signal_to_noise:.2f}σ"
        )
    print("\nTop 5 disagreements:")
    for p in report.pair_scores[:5]:
        print(
            f"  {p.framework_a} ↔ {p.framework_b} via {p.observable}: "
            f"{p.max_signal_to_noise:.2f}σ"
        )


if __name__ == "__main__":
    main()
