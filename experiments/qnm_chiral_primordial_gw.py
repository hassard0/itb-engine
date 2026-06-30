"""v2.319 - Chiral primordial gravitational waves: a CMB parity discriminator for the parity-violating frameworks.

A fresh swing into a new sector -- the CMB parity signature of the parity-violating curvature coupling. The
corrected preferred framework (v2.317/v2.318) carries a mild gravitational Chern-Simons / Pontryagin
coupling g_R2_parity ~ 0.04, driven by anomaly matching. During inflation such a parity-odd curvature term
makes the two circular polarizations of the PRIMORDIAL tensor spectrum unequal -- a net chirality
Pi = (P_R - P_L)/(P_R + P_L) != 0 -- which is observable as parity-odd CMB TB and EB cross-correlations
(the target of LiteBIRD / CMB-S4). Parity-EVEN gravity predicts Pi = 0 exactly (TB = EB = 0), so primordial
GW chirality is a clean discriminator.

This is distinct from the earlier birefringence cycles: v2.252 was photon (EM Chern-Simons) cosmic
birefringence, and v2.269 was GW PROPAGATION amplitude birefringence over astrophysical distances. Here
the effect is in the inflationary PRODUCTION of the tensor spectrum -- a CMB-scale observable.

Model (standard Chern-Simons inflation, Lue-Wang-Kamionkowski 1999 / Alexander-Martin 2004): one helicity
is enhanced and the other suppressed, giving a bounded chirality Pi = tanh(Theta) with the CS parameter
Theta = kappa * g_R2_parity * (k/k_pivot)^n -- linear in the coupling at small coupling, sign set by the
coupling, |Pi| < 1, and CHROMATIC (growing with wavenumber). kappa, n are O(1) schematic (the CS-coupling
-> chirality magnitude is not sourced here); the robust content is the discriminator and the sign.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.stack import frameworks

VERSION = "v2.319"
DEFAULT_OUT = Path("experiments/results/v2.319/qnm_chiral_primordial_gw.json")

KAPPA = 4.0       # O(1) schematic CS-coupling -> chirality conversion
N_CHROMA = 0.5    # schematic chromatic index (Pi grows with k)
K_PIVOT = 1.0


def chirality(g_parity, k=1.0):
    """Pi = (P_R - P_L)/(P_R + P_L) for the primordial tensor spectrum (CS inflation, bounded)."""
    theta = KAPPA * g_parity * (k / K_PIVOT) ** N_CHROMA
    return math.tanh(theta)


def run() -> dict:
    # parity couplings per framework (+ the v2.317 corrected preferred framework)
    theories = {}
    for fw in frameworks():
        theories[fw.name] = fw.encode().coefficients.get("g_R2_parity", 0.0)
    theories["engine_preferred"] = 0.038   # v2.317 corrected preferred framework

    rows = []
    for name, gp in theories.items():
        pi = chirality(gp, k=1.0)
        rows.append({"theory": name, "g_R2_parity": gp,
                     "chirality_Pi": pi,
                     "parity_violating": bool(abs(gp) > 1e-9),
                     "predicts_CMB_TB_EB": bool(abs(pi) > 1e-9),
                     "handedness": ("right" if pi > 1e-9 else ("left" if pi < -1e-9 else "none"))})

    parity_even = [r for r in rows if not r["parity_violating"]]
    parity_odd = [r for r in rows if r["parity_violating"]]

    even_zero = all(abs(r["chirality_Pi"]) < 1e-9 for r in parity_even)
    odd_nonzero = all(abs(r["chirality_Pi"]) > 1e-9 for r in parity_odd)
    sign_tracks = all((r["chirality_Pi"] > 0) == (r["g_R2_parity"] > 0) for r in parity_odd)
    bounded = all(abs(r["chirality_Pi"]) < 1.0 for r in rows)
    # chromatic: chirality grows in magnitude with k for a parity-violating theory
    gp_lqg = theories["lqg_induced"]
    chroma = abs(chirality(gp_lqg, k=4.0)) > abs(chirality(gp_lqg, k=1.0)) + 1e-6
    # discriminator: predicts TB/EB iff parity-violating
    discriminator = all(r["predicts_CMB_TB_EB"] == r["parity_violating"] for r in rows)

    checks = {
        "parity_even_frameworks_zero_chirality": even_zero,
        "parity_violating_frameworks_nonzero_chirality": odd_nonzero,
        "chirality_sign_tracks_parity_coupling": sign_tracks,
        "chirality_bounded_physical": bounded,
        "chirality_is_chromatic": chroma,
        "TB_EB_is_a_clean_parity_discriminator": discriminator,
    }

    chiral_theories = sorted(r["theory"] for r in rows if r["predicts_CMB_TB_EB"])

    return {
        "version": VERSION,
        "model": "Pi = tanh(kappa * g_R2_parity * (k/k_pivot)^n)  (Chern-Simons inflation, bounded, chromatic)",
        "schematic_constants": {"kappa": KAPPA, "n_chroma": N_CHROMA},
        "chirality_table": rows,
        "chiral_theories": chiral_theories,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The corrected new-theory finding -- that the engine's most-robust higher-derivative gravity "
            "is mildly parity-violating, driven by anomaly matching (v2.317/v2.318) -- makes a concrete, "
            "falsifiable COSMOLOGICAL prediction: chiral primordial gravitational waves. A gravitational "
            "Chern-Simons / Pontryagin coupling g_R2_parity during inflation makes the two circular "
            "polarizations of the primordial tensor spectrum unequal, a net chirality "
            "Pi = (P_R - P_L)/(P_R + P_L) = tanh(kappa * g_R2_parity * (k/k_pivot)^n), reproducing the "
            "standard Chern-Simons-inflation features (one helicity enhanced, |Pi| < 1, Pi -> 0 as the "
            "coupling -> 0, and chromatic -- growing with wavenumber). The observable is parity-odd CMB TB "
            "and EB cross-correlations, the target of LiteBIRD and CMB-S4. This is a CLEAN DISCRIMINATOR: "
            "the parity-even frameworks (pure_gr, string_tree_eft, asymptotic_safety, cdt) predict Pi = 0 "
            "exactly -- zero TB, zero EB -- while only the engine-preferred framework (g_R2_parity ~ 0.038) "
            "and lqg_induced (0.080) predict a nonzero chirality, both right-handed (the sign is set by the "
            "positive parity coupling). So a future detection of primordial GW chirality / CMB TB-EB would "
            "favor the parity-violating frameworks -- the engine-preferred one and lqg -- and a null result "
            "tightens the parity coupling toward zero, disfavoring them. The corrected preferred framework "
            "thus comes with its own observational test, in a different sector (CMB tensor parity) from the "
            "constraint-space structure that built it -- and the test cleanly separates it, plus lqg, from "
            "the parity-even proposals."
        ),
        "honest_scope": (
            "The discriminator and the sign are the robust content; the MAGNITUDE is schematic. The map "
            "from the engine's Pontryagin coupling g_R2_parity to the Chern-Simons chirality (kappa) and "
            "the chromatic index n are O(1) placeholders -- the CS-coupling-to-chirality amplitude is not "
            "sourced here, so the actual Pi VALUE (and whether it is within LiteBIRD/CMB-S4 reach) is not "
            "predicted. What IS robust and prefactor-independent: (i) parity-even gravity gives Pi = 0 "
            "exactly (a symmetry statement, TB = EB = 0), (ii) a nonzero g_R2_parity gives Pi != 0 with "
            "sign = sign(g_R2_parity), (iii) the chirality is bounded |Pi| < 1 and chromatic, reproducing "
            "the standard CS-inflation structure. The parity-violating set (engine_preferred, lqg) is "
            "exact (only these two have g_R2_parity != 0). The engine_preferred parity value (0.038) is the "
            "v2.317 approximate optimum (convention-dependent); its SIGN (positive -> right-handed) is the "
            "robust prediction. Single-field CS inflation; back-reaction and the detailed transfer to TB/EB "
            "not modelled. Toy basis, O(1) prefactors. A fresh-sector falsifiable signature of the "
            "corrected parity finding."
        ),
        "references": [
            "Lue, Wang, Kamionkowski 1999; Alexander, Martin 2004 (chiral GW from Chern-Simons inflation); LiteBIRD / CMB-S4 (TB/EB)",
            "this repo: v2.317/v2.318 (parity-violating preferred framework, anomaly mechanism), v2.269 (GW propagation birefringence -- distinct)",
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
    print("chiral primordial GW -- CMB parity discriminator:")
    print(f"  {'theory':<18} {'g_R2_parity':>11} {'chirality Pi':>12}  predicts TB/EB  handedness")
    for r in res["chirality_table"]:
        print(f"  {r['theory']:<18} {r['g_R2_parity']:>11.3f} {r['chirality_Pi']:>+12.4f}  "
              f"{str(r['predicts_CMB_TB_EB']):>13}  {r['handedness']}")
    print(f"  chiral theories (predict CMB TB/EB): {res['chiral_theories']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
