"""v2.226 - Black-hole-spectroscopy no-hair consistency test, and how R4 violates it.

A fresh single-event thread (the isospectrality sub-arc closed at v2.225). The no-hair theorem
makes a Schwarzschild black hole's entire QNM spectrum a function of ONE parameter (the mass M),
so the dimensionless frequency RATIOS omega_lmn / omega_220 are universal GR constants -- the
no-hair fingerprint. Black-hole spectroscopy's consistency test: every measured mode must point
to the same M; a beyond-GR operator shifts modes differently and breaks that single-mass
consistency.

This cycle (a) validates the GR no-hair ratios (220, 330, 440, 221) against the in-house solver,
and (b) computes how the R4 quartic operator VIOLATES the consistency of the fundamental + first
overtone (220 vs 221) -- the standard 2-mode no-hair test (Isi et al. used exactly 220+221 on
GW150914) -- using SOURCE-BACKED qEFT coefficients (v2.217), not the cross-multipole WKB
sensitivity (which is unreliable for the sharply-peaked (r_g/r)^10 R4 deformation, v2.212).

Result: R4 shifts the frequency ratio omega_R,221/omega_R,220 by (dwq_1 - dwq_0) = -1.31 per
gamma and the damping ratio omega_I,221/omega_I,220 by -(dtq_1 - dtq_0) = -172 per gamma. The
DAMPING no-hair channel is ~150x more sensitive (it inherits the overtone damping coefficient
dtq_1 = 171.35) -- so the no-hair test, like the R4 reach (v2.217-v2.220), is overtone-damping
dominated.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_wkb_solver import schwarzschild_qnm
from experiments.r4_parspec_qeft_source_asset_audit import (
    QEFT_QNM_DEFORMATION_COEFFICIENTS as QC,
)

VERSION = "v2.226"
DEFAULT_OUT = Path("experiments/results/v2.226/qnm_nohair_consistency.json")

# Berti-Cardoso-Will reference QNMs (M=1)
BERTI = {
    "220": complex(0.373672, -0.088962),
    "221": complex(0.346711, -0.273915),
    "330": complex(0.599443, -0.092703),
    "440": complex(0.809178, -0.094163),
}
MODE_LN = {"220": (2, 0), "221": (2, 1), "330": (3, 0), "440": (4, 0)}
# isolated resolvability coefficients (v2.219/v2.220) for the detectability hook
R_F = {"220": 0.5537, "221": 3.7740}
R_TAU = {"220": 2.0007, "221": 2.5290}


def gr_nohair_ratios() -> dict:
    """Solver-computed GR frequency ratios omega_lmn/omega_220, validated vs Berti."""
    w = {k: schwarzschild_qnm(n=MODE_LN[k][1], L=MODE_LN[k][0], s=2) for k in BERTI}
    w220 = w["220"].real
    rows = {}
    for k in BERTI:
        solver = w[k].real / w220
        berti = BERTI[k].real / BERTI["220"].real
        rows[k] = {"solver": solver, "berti": berti, "rel_err": abs(solver - berti) / berti}
    return rows


def r4_nohair_violation() -> dict:
    """R4 violation of the 220/221 no-hair consistency, from source-backed qEFT coefficients."""
    dwq0 = QC["nmax_0"]["delta_omega_qeft_0"]
    dwq1 = QC["nmax_1"]["delta_omega_qeft_1"]
    dtq0 = QC["nmax_0"]["delta_tau_qeft_0"]
    dtq1 = QC["nmax_1"]["delta_tau_qeft_1"]
    # fractional shift of the ratio = difference of the two modes' fractional shifts
    dfreq_ratio = dwq1 - dwq0                 # d ln(wR_221/wR_220) / d gamma
    ddamp_ratio = -(dtq1 - dtq0)              # d ln(wI_221/wI_220) / d gamma (Delta wI/wI = -dtq)
    # detectability: rho * sigma(ln ratio) = hypot of the two modes' resolvability coefficients
    sig_freq = math.hypot(R_F["220"], R_F["221"])
    sig_damp = math.hypot(R_TAU["220"], R_TAU["221"])
    return {
        "gr_freq_ratio_wR221_over_wR220": BERTI["221"].real / BERTI["220"].real,
        "gr_damp_ratio_wI221_over_wI220": BERTI["221"].imag / BERTI["220"].imag,
        "r4_freq_ratio_violation_per_gamma": dfreq_ratio,
        "r4_damp_ratio_violation_per_gamma": ddamp_ratio,
        "rho_crit_1sigma_freq_channel_per_gamma": sig_freq / abs(dfreq_ratio),
        "rho_crit_1sigma_damp_channel_per_gamma": sig_damp / abs(ddamp_ratio),
        "damp_over_freq_sensitivity": abs(ddamp_ratio) / abs(dfreq_ratio),
    }


def run() -> dict:
    ratios = gr_nohair_ratios()
    viol = r4_nohair_violation()
    max_rel_err = max(r["rel_err"] for r in ratios.values())
    return {
        "version": VERSION,
        "method": ("GR no-hair frequency ratios from the in-house WKB solver (validated vs "
                   "Berti-Cardoso-Will); R4 violation of the 220/221 pair from source-backed "
                   "qEFT deformation coefficients (v2.217); M=1"),
        "gr_nohair_ratios": ratios,
        "gr_ratios_validated": bool(max_rel_err < 5e-3),
        "max_ratio_rel_err": max_rel_err,
        "r4_nohair_violation_220_221": viol,
        "finding": (
            f"GR no-hair fingerprint reproduced to {100*max_rel_err:.2f}% (omega_330/omega_220 = "
            f"{ratios['330']['solver']:.3f}, omega_440/omega_220 = {ratios['440']['solver']:.3f}). "
            f"R4 VIOLATES the 220/221 no-hair consistency: it shifts the frequency ratio by "
            f"{viol['r4_freq_ratio_violation_per_gamma']:+.2f} per gamma and the damping ratio by "
            f"{viol['r4_damp_ratio_violation_per_gamma']:+.0f} per gamma. The DAMPING no-hair "
            f"channel is ~{viol['damp_over_freq_sensitivity']:.0f}x more sensitive (critical SNR "
            f"{viol['rho_crit_1sigma_damp_channel_per_gamma']:.3f}/gamma vs "
            f"{viol['rho_crit_1sigma_freq_channel_per_gamma']:.2f}/gamma) -- it inherits the "
            "overtone damping coefficient dtq_1 = 171.35, so the no-hair test, like the R4 reach "
            "(v2.217-v2.220), is overtone-damping dominated."
        ),
        "honest_scope": (
            "The GR no-hair RATIOS are claim-grade (the solver reproduces Berti to <0.2%). The R4 "
            "VIOLATION of the 220/221 pair is source-backed (published qEFT dwq/dtq, v2.217). The "
            "cross-multipole no-hair violation (330/440 vs 220) is NOT computed: only the n=0,1 "
            "l=2 qEFT coefficients are published, and the in-house cross-l WKB sensitivity to the "
            "(r_g/r)^10 R4 deformation is unreliable (v2.212 overshoot, which does NOT cancel "
            "across different multipoles -- unlike the same-l parity ratio of v2.224). The "
            "detectability uses ISOLATED resolvability (v2.221 covariance would inflate rho_crit a "
            "few-fold). The dtq_1 perturbative-delicacy caveat carries (v2.217, valid for "
            "gamma << 6e-3). Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Berti, Cardoso, Will, PRD 73 (2006) 064030 -- QNM table / no-hair spectroscopy",
            "Isi, Giesler, Farr, Scheel, Teukolsky, PRL 123 (2019) 111102 -- 220+221 no-hair test",
            "Silva, Ghosh, Buonanno, PRD 107 (2023) 044030 -- qEFT coefficients (v2.217)",
            "this repo: v2.219 (resolvability), v2.212 (cross-l WKB sensitivity caveat)",
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
    for k, r in res["gr_nohair_ratios"].items():
        print(f"  omega_{k}/omega_220: solver {r['solver']:.4f}  berti {r['berti']:.4f}  "
              f"(rel.err {r['rel_err']:.1e})")
    v = res["r4_nohair_violation_220_221"]
    print(f"R4 no-hair violation (220/221): freq {v['r4_freq_ratio_violation_per_gamma']:+.2f}/g  "
          f"damp {v['r4_damp_ratio_violation_per_gamma']:+.0f}/g  "
          f"(damp {v['damp_over_freq_sensitivity']:.0f}x more sensitive)")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
