"""v2.228 - End-to-end R4 detectability forecast: single-event covariance + population, combined.

The v2.217-v2.227 ringdown program built each piece of the R4 detectability chain separately.
This cycle integrates them into one forecast: given a per-event ringdown SNR rho and a network of
N detected events, what is the reach on the ParSpec R4 coupling gamma?

Chain (all source-backed / first-principles from prior cycles):
  - v2.217: the n=1 overtone DAMPING channel is the dominant R4 lever (dtq_1 = 171.35).
  - v2.227: the covariance-corrected (realistic two-mode) no-hair damping critical SNR is
    rho_crit(1 sigma) = 0.133 / gamma, i.e. the 1-sigma detectable coupling is
    gamma_min(1 sigma) = 0.133 / rho per event.
  - v2.223: N independent events combine the Gaussian-in-gamma constraint as 1/sqrt(N), and the
    length-scale ell ~ gamma^{1/p} (p = 6) tightens only as N^{-1/(2p)} = N^{-1/12}.

So the network reach (n-sigma) is gamma_reach = n_sigma * 0.133 / (rho * sqrt(N)), and the
companion ell-scale reach improves as (rho sqrt(N))^{-1/6}. This is the program's bottom line:
a concrete, integrated R4 reach number for any (rho, N).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

VERSION = "v2.228"
DEFAULT_OUT = Path("experiments/results/v2.228/qnm_r4_end_to_end_forecast.json")

# v2.227 covariance-corrected no-hair damping-channel critical SNR (1 sigma) = RHO_SIGMA / gamma
RHO_SIGMA_DAMP = 0.1333          # rho * sigma(gamma) on the no-hair damping ratio
P_QEFT = 6                       # v2.223 / source-backed ParSpec power


def gamma_reach(rho: float, n_events: int = 1, n_sigma: float = 5.0) -> float:
    """n-sigma reach on the ParSpec R4 coupling gamma for N events at per-event SNR rho."""
    return n_sigma * RHO_SIGMA_DAMP / (rho * (n_events ** 0.5))


def ell_scaling(rho: float, n_events: int = 1) -> float:
    """Relative length-scale reach ell/ell_ref ~ (rho sqrt(N))^{-1/p} (lower = deeper)."""
    return (rho * n_events ** 0.5) ** (-1.0 / P_QEFT)


def run() -> dict:
    scenarios = [
        {"label": "current single event", "rho": 10, "N": 1},
        {"label": "loud single event", "rho": 30, "N": 1},
        {"label": "O4-era network", "rho": 10, "N": 50},
        {"label": "3G/LISA loud event", "rho": 100, "N": 1},
        {"label": "3G network", "rho": 30, "N": 1000},
    ]
    rows = []
    for s in scenarios:
        g5 = gamma_reach(s["rho"], s["N"], 5.0)
        rows.append({**s, "gamma_reach_5sigma": g5,
                     "effective_snr": s["rho"] * s["N"] ** 0.5,
                     "ell_relative_reach": ell_scaling(s["rho"], s["N"])})
    # the lever comparison (v2.223): SNR is quadratically stronger than event count
    return {
        "version": VERSION,
        "method": ("integrate v2.227 (covariance-corrected single-event no-hair damping reach, "
                   "gamma_min(1 sigma)=0.133/rho) with v2.223 (population 1/sqrt(N) in gamma, "
                   "ell~N^{-1/12}); n-sigma network reach gamma = n*0.133/(rho sqrt(N))"),
        "single_event_1sigma_coupling": "gamma_min = 0.133 / rho  (damping no-hair channel)",
        "scenarios": rows,
        "lever_comparison": {
            "gamma_reach_scales_as": "1 / (rho * sqrt(N))",
            "ell_reach_scales_as": "(rho * sqrt(N))^{-1/6}",
            "snr_vs_count": ("per-event SNR and sqrt(N) enter gamma identically, but for the "
                             "ELL scale a k-louder event equals k^2 events (v2.223) -- chase SNR"),
        },
        "finding": (
            "Integrated bottom line: the R4 ParSpec coupling reach is "
            "gamma_reach(5 sigma) = 0.665 / (rho sqrt(N)). A current single event (rho~10) reaches "
            f"gamma ~ {gamma_reach(10,1):.3f}; an O4-era network (rho~10, N~50) reaches "
            f"gamma ~ {gamma_reach(10,50):.4f}; a 3G network (rho~30, N~1000) reaches "
            f"gamma ~ {gamma_reach(30,1000):.5f}. The reach is dominated by the overtone damping "
            "channel (v2.217-v2.227) and limited on the length-scale axis by the steep p=6 power "
            "(ell ~ (rho sqrt N)^{-1/6}), so loud events dominate quiet populations (v2.223)."
        ),
        "honest_scope": (
            "Integrates prior-cycle results, each with its caveats: the covariance-corrected "
            "single-event number (v2.227, equal-amplitude white-noise two-mode Fisher), the "
            "population 1/sqrt(N) (v2.223, independent half-normal posteriors), and the "
            "source-backed overtone qEFT coefficient (v2.217, dtq_1=171.35, perturbatively valid "
            "for gamma << 6e-3 -- so the larger gamma_reach values at low rho*sqrt(N) are at the "
            "edge of linear validity). gamma is the ParSpec coupling; converting to an absolute "
            "ell in km needs the v2.215 normalization (not claimed here -- ell is reported as a "
            "relative scaling). Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "leaver_solver_foundation": (
            "A high-accuracy Leaver continued-fraction solver (to close the v2.212 cross-multipole "
            "WKB-sensitivity gap) was scoped this cycle on Vulcan: the exact Regge-Wheeler "
            "recurrence polynomials were DERIVED symbolically (sympy, 2M=1 ansatz "
            "psi = e^{iwr}(r-1)^{-iw}r^{2iw} sum a_n ((r-1)/r)^n). The derivation reveals a "
            "5-TERM recurrence (coupling a_k..a_{k-4}), not the textbook 3-term, so a validated "
            "solver requires a matrix continued fraction / Gaussian-elimination-to-3-term step "
            "(Leaver 1990). Foundation laid; the validated solver is deferred to a dedicated cycle "
            "rather than shipped unvalidated."
        ),
        "references": [
            "this repo: v2.217 (overtone sensitivity), v2.223 (population), v2.227 (covariance no-hair)",
            "Silva, Ghosh, Buonanno, PRD 107 (2023) 044030 -- qEFT coefficients / ParSpec power",
            "Leaver, Proc. R. Soc. Lond. A 402 (1985) 285; J. Math. Phys. 27 (1990) 1238 (elimination)",
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
    for s in res["scenarios"]:
        print(f"  {s['label']:24s} rho={s['rho']:3d} N={s['N']:4d}  "
              f"gamma_reach(5sig)={s['gamma_reach_5sigma']:.5f}  "
              f"ell_rel={s['ell_relative_reach']:.3f}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
