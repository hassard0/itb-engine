"""v2.295 - When does the shared spectrum bite? The cross-sector constraint as a function of w.

FOURTH SLICE of the new-theory arc. v2.293 proposed the shared-spectral-density cross-sector principle
(calibrated ratio band); v2.294 found the rigorous 2x2 tilted-Hankel adds nothing. This cycle settles
the question structurally and RESCUES the real content.

STRUCTURAL NEGATIVE (generalizes v2.294 to ALL orders). The tilted measure (1 + t w) dmu has Hankel
matrix H(t) = H_matter + t H_curv, a nonnegative combination of two PSD matrices (each a valid moment
Hankel). A nonnegative combination of PSD matrices is PSD, so H(t) is PSD for all t >= 0 AUTOMATICALLY
once the matter and curvature towers hold -- at every moment order. So the BARE shared-measure hypothesis
(w >= 0 on a common support) can NEVER add a cross-sector constraint; it is exactly the two separate
towers. The v2.294 2x2 result was not special.

THE RESCUE (what genuinely bites). New cross-sector information requires a STRONGER statement about the
relative weight w(M^2) than mere positivity. The physically motivated one (a Regge tower: higher-mass
states couple to curvature monotonically relative to matter) is that w is MONOTONE in the spectral
variable. Then the ratios r_k = c_k/m_k = <w>_k -- x^k-weighted averages of one monotone w -- are
themselves MONOTONE in k. That is a genuine new constraint: a coupling set with NON-monotone r_k cannot
come from a monotone shared weight, even though it satisfies both towers. The engine's frameworks all
have monotone r_k (v2.293), i.e. they behave as if the shared weight is monotone.

So the cross-sector constraint's strength is exactly the structure assumed on w:
  w >= 0            -> nothing new (the two towers)
  w monotone        -> ratio monotonicity r_k monotone (the genuine, premise-correct v2.293 content)
  w <= W (cutoff)   -> a one-sided bracket W m_k - c_k Hankel-PSD (uses the EFT cutoff scale W)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from experiments.stack import frameworks

VERSION = "v2.295"
DEFAULT_OUT = Path("experiments/results/v2.295/qnm_cross_sector_weight_structure.json")


def moments(weights, masses, w_vals, kmax):
    """Matter moments m_k = sum p x^k and curvature moments c_k = sum p w x^k, k=0..kmax."""
    p, x, w = np.array(weights, float), np.array(masses, float), np.array(w_vals, float)
    m = np.array([np.sum(p * x**k) for k in range(kmax + 1)])
    c = np.array([np.sum(p * w * x**k) for k in range(kmax + 1)])
    return m, c


def hankel(seq, n):
    return np.array([[seq[i + j] for j in range(n + 1)] for i in range(n + 1)])


def is_psd(M, tol=-1e-9):
    return bool(np.min(np.linalg.eigvalsh((M + M.T) / 2)) >= tol)


def run() -> dict:
    # a positive 4-point spectral measure (guarantees valid moment sequences)
    p = [0.4, 0.3, 0.2, 0.1]
    x = [0.2, 0.5, 0.9, 1.4]
    w_mono = [0.30, 0.40, 0.55, 0.75]          # monotone-increasing relative weight
    w_peak = [0.30, 0.95, 0.90, 0.32]          # NON-monotone (peaked) relative weight

    out = {}
    for label, w in (("monotone", w_mono), ("peaked", w_peak)):
        m, c = moments(p, x, w, kmax=4)        # 5 moments -> up to 3x3 Hankel
        # 1. tilted-Hankel decomposition: H(t) = H_m + t H_c PSD for all t>=0 (2x2 and 3x3)
        decomposes = True
        for n in (1, 2):                       # 2x2 and 3x3
            Hm, Hc = hankel(m, n), hankel(c, n)
            for t in (0.0, 0.5, 1.0, 3.0, 10.0):
                if not is_psd(Hm + t * Hc):
                    decomposes = False
        # 2. ratio monotonicity
        r = [float(c[k] / m[k]) for k in range(3)]   # r_0, r_1, r_2 (the engine's observable depth)
        mono = (r[0] <= r[1] <= r[2]) or (r[0] >= r[1] >= r[2])
        out[label] = {"r": r, "ratios_monotone": bool(mono),
                      "tilted_hankel_decomposes": decomposes,
                      "matter_tower_ok": is_psd(hankel(m, 1)), "curv_tower_ok": is_psd(hankel(c, 1))}

    # 3. the engine frameworks: are their r_k monotone (consistent with a monotone shared weight)?
    fw_rows = []
    for fw in frameworks():
        cf = fw.encode().coefficients
        g4, g6, g8 = cf.get("g_4", 0.0), cf.get("g_6", 0.0), cf.get("g_8", 0.0)
        gR2, gR3 = cf.get("g_R2", 0.0), cf.get("g_R3", 0.0)
        if gR2 <= 0 or g4 <= 0:
            continue
        gR4 = gR3 * gR3 / gR2
        r = [gR2 / g4, gR3 / g6, gR4 / g8]
        fw_rows.append({"framework": fw.name, "r": r,
                        "ratios_monotone": (r[0] >= r[1] >= r[2]) or (r[0] <= r[1] <= r[2])})

    checks = {
        "tilted_hankel_decomposes_at_all_orders": out["monotone"]["tilted_hankel_decomposes"]
                                                  and out["peaked"]["tilted_hankel_decomposes"],
        "w_ge_0_adds_nothing": (out["peaked"]["matter_tower_ok"] and out["peaked"]["curv_tower_ok"]
                                and out["peaked"]["tilted_hankel_decomposes"]),
        "monotone_w_gives_monotone_ratios": out["monotone"]["ratios_monotone"],
        "nonmonotone_w_breaks_monotone_ratios": not out["peaked"]["ratios_monotone"],
        "frameworks_have_monotone_ratios": all(r["ratios_monotone"] for r in fw_rows),
    }

    return {
        "version": VERSION,
        "method": ("construct positive 4-point spectral measures with monotone vs peaked relative "
                   "weight w; verify the tilted-Hankel H(t)=H_m+t H_c is PSD for all t (so w>=0 adds "
                   "nothing at 2x2 and 3x3); show monotone w => monotone ratios r_k=c_k/m_k while "
                   "peaked w (passing both towers) breaks it; test the engine frameworks' r_k"),
        "weight_cases": out,
        "framework_ratios": fw_rows,
        "constraint_by_assumption_on_w": {
            "w_ge_0": "no new cross-sector constraint (exactly the two separate towers)",
            "w_monotone": "ratio monotonicity r_k = c_k/m_k monotone (the genuine v2.293 content)",
            "w_le_W_cutoff": "one-sided bracket: W m_k - c_k Hankel-PSD (uses the EFT cutoff scale W)"},
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The cross-sector question is now settled, and the real constraint identified. The "
            "STRUCTURAL fact is decisive: the tilted measure's Hankel is H(t) = H_matter + t H_curv, a "
            "nonnegative combination of two PSD matrices, hence PSD for all t >= 0 automatically (verified "
            "at 2x2 AND 3x3). So the BARE shared-measure hypothesis 'w >= 0 on a common support' can "
            "NEVER add a cross-sector constraint at any moment order -- it is exactly the two separate "
            "towers, and v2.294's 2x2 negative was not special but structural. The genuine new "
            "information requires a STRONGER statement about the relative weight w(M^2). The physically "
            "motivated one -- a Regge-like tower where higher-mass states couple to curvature "
            "monotonically relative to matter -- is that w is MONOTONE; then the ratios r_k = c_k/m_k, "
            "x^k-weighted averages of one monotone w, are themselves monotone in k. This BITES: a "
            "constructed coupling set from a PEAKED (non-monotone) weight satisfies BOTH towers (its "
            "matter and curvature Hankels are PSD) yet has non-monotone r_k, so it cannot come from a "
            "monotone shared weight -- a genuine constraint the towers miss. And the engine's frameworks "
            "all have monotone r_k (string, asymptotic-safety, cdt decreasing; lqg increasing), so they "
            "behave exactly as if the shared spectral weight is monotone. So v2.293's ratio "
            "monotonicity was real after all -- but its correct premise is 'w monotone', not 'w >= 0', "
            "and v2.294 was right that the bare hypothesis is empty. The honest synthesis: the "
            "cross-sector constraint's strength is precisely the structure assumed on w (nothing / "
            "ratio-monotonicity / cutoff-bracket), a clean map of where new theory can be extracted."
        ),
        "honest_scope": (
            "Rigorous results: the tilted-Hankel decomposition H(t)=H_m+t H_c (hence 'w>=0 adds nothing "
            "at all orders') is an exact linear-algebra fact, verified numerically at 2x2 and 3x3 on "
            "constructed positive measures. The monotone-w => monotone-r_k implication is exact (x^k "
            "weighting moves mass monotonically along the support), and the peaked-weight counterexample "
            "is exact (built from a valid positive measure, passes both towers, breaks ratio "
            "monotonicity). The ASSUMPTION 'w monotone' is a physical refinement (motivated by the "
            "Regge tower), NOT a theorem -- a UV completion with a non-monotone curvature/matter "
            "coupling ratio would evade the ratio-monotonicity constraint while remaining consistent. So "
            "the honest status of the cross-sector constraint is conditional on that structural "
            "assumption about w, now stated explicitly (correcting v2.293's implicit premise and "
            "completing v2.294's negative). The engine couplings are the toy basis with O(1) prefactors; "
            "g_R4 at the v2.234 forced minimum. A new-engine-theory result: a definitive structural "
            "characterization of when the shared-spectrum idea adds information."
        ),
        "references": [
            "this repo: v2.293 (ratio band), v2.294 (rigorous 2x2 negative), v2.292 (g_R4 tower), v2.261 (Stieltjes moments)",
            "Caron-Huot, Mazac, Rastelli, Simmons-Duffin, JHEP 07 (2021) 110 (moment problem)",
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
    print("cross-sector constraint as a function of the relative weight w:")
    for k, v in res["constraint_by_assumption_on_w"].items():
        print(f"  {k:14s} -> {v}")
    print("\n  constructed weights:")
    for label, d in res["weight_cases"].items():
        print(f"    {label:9s} r={[round(x,3) for x in d['r']]} monotone={d['ratios_monotone']} "
              f"towers_ok={d['matter_tower_ok'] and d['curv_tower_ok']} tilted_decomposes={d['tilted_hankel_decomposes']}")
    print("  engine frameworks (r_k = [gR2/g4, gR3/g6, gR4/g8]):")
    for r in res["framework_ratios"]:
        print(f"    {r['framework']:18s} r={[round(x,3) for x in r['r']]} monotone={r['ratios_monotone']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
