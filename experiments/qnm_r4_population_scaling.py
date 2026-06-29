"""v2.223 - Population scaling of R4 ringdown bounds: why multi-event stacking is a weak lever.

The single-event ringdown lever was mapped end to end in v2.217-v2.222. This cycle pivots to the
POPULATION question, using data the repo already holds (source-backed, Silva-Ghosh-Buonanno
2205.05132): the per-event 90%-credible upper bounds on the qEFT higher-curvature length scale
ell (GW150914: 51.7 km, GW200129: 54.8 km), the published COMBINED bound (51.3 km), and the
ParSpec power p = 6 (the QNM deformation scales as gamma ~ (ell/M)^p, so the measurement is
~Gaussian in x = ell^p -- the Fisher regime characterized in v2.219-v2.222).

Key consequence of the steep p = 6 power: combining N independent events tightens the ell bound
only as

    ell_bound ~ N^{-1/(2p)} = N^{-1/12}     (equal events),

an extraordinarily weak lever -- to HALVE the ell bound takes N = 2^12 = 4096 comparable events.
By contrast a single louder event with Fisher gamma_bound ~ 1/rho (v2.219) gives
ell_bound ~ rho^{-1/p} = rho^{-1/6}, so a k-times-louder event is worth k^2 events. Per-event SNR
is a QUADRATICALLY stronger lever than event count for higher-curvature length scales.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.r4_parspec_qeft_source_asset_audit import (
    PARSPEC_QEFT_BOUND_KM_90,
    QEFT_EVENT_BOUNDS_KM_90,
    QEFT_POWER,
)

VERSION = "v2.223"
DEFAULT_OUT = Path("experiments/results/v2.223/qnm_r4_population_scaling.json")

P = QEFT_POWER                       # 6
EVENTS = {k: v for k, v in QEFT_EVENT_BOUNDS_KM_90.items() if k != "combined"}
PUBLISHED_COMBINED = PARSPEC_QEFT_BOUND_KM_90   # 51.3 km


def inverse_variance_combination(bounds: list[float], p: int = P) -> float:
    """Combine independent one-sided (half-normal) ell-bounds in x = ell^p space.

    Each 90% upper bound L_i fixes sigma_{x,i} = L_i^p / 1.6449 (half-normal, mean 0); the
    inverse-variance combined 90% bound is x_comb = (sum_i L_i^{-2p})^{-1/2}, i.e.
    L_comb = (sum_i L_i^{-2p})^{-1/(2p)}. (The 1.6449 z-factor cancels.)
    """
    s = sum(L ** (-2 * p) for L in bounds)
    return s ** (-1.0 / (2 * p))


def n_events_to_improve(factor: float, p: int = P) -> float:
    """Equal-event count needed to tighten the ell bound by `factor` (N^{1/(2p)} = factor)."""
    return factor ** (2 * p)


def snr_event_equivalence(k_louder: float, p: int = P) -> float:
    """One event k-times louder in SNR is worth this many equal events for the ell bound.

    ell ~ rho^{-1/p} (single, Fisher) vs ell ~ N^{-1/(2p)} (population): N^{1/(2p)} = k^{1/p}
    -> N = k^2 (independent of p).
    """
    return k_louder ** 2


def run() -> dict:
    bounds = list(EVENTS.values())
    L_iv = inverse_variance_combination(bounds)
    best_single = min(bounds)
    return {
        "version": VERSION,
        "source": "Silva-Ghosh-Buonanno (2205.05132); per-event + combined qEFT ell bounds, p=6",
        "qeft_power_p": P,
        "per_event_bounds_km": EVENTS,
        "population_scaling_law": {
            "ell_bound_scales_as": "N^{-1/(2p)} = N^{-1/12}  (equal events)",
            "N_to_halve_ell_bound": n_events_to_improve(2.0),
            "N_to_improve_ell_10x": n_events_to_improve(10.0),
            "interpretation": (
                "Because the QNM deformation scales as the 6th power of the length scale, "
                "multi-event stacking is an extraordinarily weak lever on ell: halving the bound "
                f"needs ~{int(n_events_to_improve(2.0))} comparable events."
            ),
        },
        "snr_vs_population_lever": {
            "single_event_ell_scales_as": "rho^{-1/p} = rho^{-1/6}",
            "event_k_louder_worth_N_events": "N = k^2",
            "example_2x_louder_equals_events": snr_event_equivalence(2.0),
            "example_10x_louder_equals_events": snr_event_equivalence(10.0),
            "interpretation": (
                "Per-event SNR is a QUADRATICALLY stronger lever than event count: a 2x-louder "
                "event is worth 4 events, a 10x-louder event worth 100. This is why a single loud "
                "ringdown (v2.219 reach ~ 1/rho) dominates the R4 constraint over a large quiet "
                "population -- consistent with the whole single-event ringdown arc (v2.217-v2.222)."
            ),
        },
        "two_event_combination_check": {
            "inverse_variance_estimate_km": L_iv,
            "best_single_event_km": best_single,
            "published_combined_km": PUBLISHED_COMBINED,
            "iv_improvement_vs_best_single": 1.0 - L_iv / best_single,
            "published_improvement_vs_best_single": 1.0 - PUBLISHED_COMBINED / best_single,
            "iv_vs_published_relative_diff": abs(L_iv - PUBLISHED_COMBINED) / PUBLISHED_COMBINED,
            "finding": (
                f"The naive independent-half-normal inverse-variance combination gives "
                f"{L_iv:.1f} km (a {100*(1-L_iv/best_single):.1f}% improvement over the best "
                f"single event, {best_single} km). The PUBLISHED combined bound is "
                f"{PUBLISHED_COMBINED} km -- only a {100*(1-PUBLISHED_COMBINED/best_single):.1f}% "
                "improvement. Both confirm the headline (combining two comparable events barely "
                "tightens the ell bound, as the N^{-1/12} law demands), but the published "
                f"combination is ~{100*abs(L_iv-PUBLISHED_COMBINED)/PUBLISHED_COMBINED:.0f}% LESS "
                "tight than naive inverse-variance."
            ),
        },
        "claim_gate": (
            "The SCALING LAW (ell ~ N^{-1/12}; SNR k-louder = k^2 events) is claim-grade -- it "
            "follows from the source-backed power p=6 and the Fisher-Gaussian-in-gamma regime, "
            "method-independent. The specific 2-event NUMBER (50.0 km) is an approximation: it "
            "assumes independent half-normal posteriors, and it lands ~2-3% tighter than the "
            "published combined bound (51.3 km), a residual that reflects the un-sourced posterior "
            "shapes / the paper's actual combination method (the machine-readable likelihoods are "
            "not in the cached source package). Negative preserved; not tuned. The single-event "
            "ell<->gamma map normalization (v2.215) and parity-odd g_R4_c3 darkness (v2.209) carry."
        ),
        "references": [
            "Silva, Ghosh, Buonanno, PRD 107 (2023) 044030 (arXiv:2205.05132) -- ell bounds, p=6",
            "this repo: v2.219 (single-event Fisher reach ~ 1/rho)",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()
    res = run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    sl = res["population_scaling_law"]
    c = res["two_event_combination_check"]
    print(f"ell ~ N^-1/12: halving needs {int(sl['N_to_halve_ell_bound'])} events; "
          f"k-louder event = k^2 events")
    print(f"2-event: inverse-variance {c['inverse_variance_estimate_km']:.1f} km vs "
          f"published combined {c['published_combined_km']} km "
          f"(best single {c['best_single_event_km']} km)")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
