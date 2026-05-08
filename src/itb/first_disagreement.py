"""First-disagreement analysis: given two candidate frameworks, what is the
observable that *first* measurably distinguishes them?

For each available observable, compute |obs(framework_a) - obs(framework_b)|
in units of the observable's natural noise scale (sigma). The observable
with the largest signal-to-noise ratio is the place experimental physicists
should look first.

This is the engine's most experimentally-actionable output: not just "rank
experiments by exclusion power" but "rank observables by which framework
pair they most cleanly distinguish."""

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from itb.frameworks.base import Framework
from itb.observables import Observable


@dataclass
class DisagreementScore:
    framework_a: str
    framework_b: str
    observable: str
    max_signal_to_noise: float
    signal: float
    noise_sigma: float


@dataclass
class DisagreementReport:
    pair_scores: list[DisagreementScore]
    best_pair: DisagreementScore | None


def first_disagreement(
    frameworks: Sequence[Framework],
    observables: dict[str, Observable],
    sigma: float,
) -> DisagreementReport:
    pairs: list[DisagreementScore] = []
    for i in range(len(frameworks)):
        for j in range(i + 1, len(frameworks)):
            fa = frameworks[i]
            fb = frameworks[j]
            ta = fa.encode()
            tb = fb.encode()
            for obs_name, obs in observables.items():
                pred_a = obs.predict(ta)
                pred_b = obs.predict(tb)
                diff = pred_a - pred_b
                signal = float(np.max(np.abs(diff)))
                snr = signal / sigma if sigma > 0 else 0.0
                pairs.append(DisagreementScore(
                    framework_a=fa.name,
                    framework_b=fb.name,
                    observable=obs_name,
                    max_signal_to_noise=snr,
                    signal=signal,
                    noise_sigma=sigma,
                ))
    pairs.sort(key=lambda p: -p.max_signal_to_noise)
    best = pairs[0] if pairs else None
    return DisagreementReport(pair_scores=pairs, best_pair=best)


def render_disagreement_report(report: DisagreementReport) -> str:
    lines: list[str] = []
    lines.append("# First-disagreement observable ranking")
    lines.append("")
    if report.best_pair is None:
        lines.append("_No frameworks supplied._")
        return "\n".join(lines)
    lines.append(
        f"**Best discriminator:** {report.best_pair.observable} between "
        f"{report.best_pair.framework_a} and {report.best_pair.framework_b} "
        f"at {report.best_pair.max_signal_to_noise:.2f}σ.")
    lines.append("")
    lines.append("| pair | observable | signal | sigma | S/N |")
    lines.append("|---|---|---|---|---|")
    for p in report.pair_scores:
        lines.append(
            f"| {p.framework_a} ↔ {p.framework_b} | {p.observable} | "
            f"{p.signal:.4f} | {p.noise_sigma:.4f} | {p.max_signal_to_noise:.2f}σ |"
        )
    return "\n".join(lines)
