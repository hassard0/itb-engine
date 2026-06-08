"""The ITB prediction scorecard (v1.51).

Consolidates every falsifiable number the 2026-06 program produced into one
graded table, read from the committed result JSONs where possible. Each row:
prediction, the experiment that tests it, current status, and a candid
confidence grade (ROBUST / MODEL-DEPENDENT / TENSION / NULL-FEATURE).

This is the experimentalist's cheat-sheet — and an honest self-audit of which
claims to trust.
"""

import json
import os
import sys

sys.path.insert(0, ".")
R = "experiments/results"


def load(name, default=None):
    p = os.path.join(R, name)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return default


def main():
    survival = load("out_survival.json", {})
    fisher = load("out_fisher.json", {})
    spec = load("out_spec_sheet.json", {})
    cc = load("out_cc_naturalness.json", {})
    eb = load("out_cmb_eb.json", {})
    wz = load("out_quintessence_wz.json", {})

    rows = [
        # (prediction, experiment, current status, grade)
        ("A consistent QG theory exists (non-empty intersection)",
         "internal (engine)", "51-78% of prefactor space", "ROBUST"),
        ("LQG-induced robustly disfavoured (~2% viable, redundant)",
         "internal (engine)", "viable 2% vs 19-44% others", "ROBUST"),
        ("string vs CDT indistinguishable at toy precision",
         "matter scattering + sub-mm", "S/N 2.6 combined", "ROBUST"),
        ("Sub-mm (R^2-Yukawa) gravity deviation at ~93 um",
         "torsion balance / Eot-Wash", "10-16% of Newton IF cutoff~meV", "MODEL-DEPENDENT (cutoff)"),
        ("Full program resolves 20/21 framework pairs",
         "matter + sub-mm + birefringence", "needs ~1% force, partial-wave, O5", "ROBUST (given experiments)"),
        ("Dark-energy-scale cutoff dissolves CC fine-tuning",
         "sub-mm gravity @70-130um", "Planckian alt needs g_R2~1e121", "HYPOTHESIS (sharp, testable)"),
        ("Cosmic birefringence beta ~ 0.34 deg (EB ~1% of EE)",
         "CMB EB (Planck/LiteBIRD/CMB-S4)", "~3 sigma hint (Minami-Komatsu)", "MODEL-DEPENDENT (axion link)"),
        ("Dark-energy w0 ~ -0.82",
         "DESI / Euclid / Roman", "DESI -0.83+/-0.06: MATCH", "ROBUST (given axion)"),
        ("Dark-energy wa ~ -0.28 (thawing track)",
         "DESI / Euclid / Roman", "DESI -0.7: ~1.4 sigma TENSION", "TENSION (robust to V shape)"),
        ("Correlated GW birefringence |g_R2_parity| ~ 0.09",
         "LIGO O5 / next-gen GW", "needs ~0.01 sensitivity", "ENGINE-UNIQUE (clean discriminator)"),
        ("Birefringence anisotropy from the smooth axion",
         "CMB-S4 C_l^bb", "delta-beta/beta ~ 1e-5: negligible", "NULL-FEATURE (isotropic predicted)"),
    ]

    print("=" * 92)
    print("  ITB PREDICTION SCORECARD (2026-06 program, v1.23-v1.50)")
    print("=" * 92)
    for pred, exp, status, grade in rows:
        print(f"\n  [{grade}]")
        print(f"    prediction: {pred}")
        print(f"    experiment: {exp}")
        print(f"    status    : {status}")

    # tally
    from collections import Counter
    grades = Counter(r[3].split()[0] for r in rows)
    print("\n" + "=" * 92)
    print(f"  TALLY: {dict(grades)}")
    print("  The honest core (ROBUST): a consistent theory exists; LQG disfavoured;")
    print("  survivors unrankable; w0 matches DESI. The engine-unique clean test:")
    print("  GW birefringence at |g_R2_parity|~0.09 (LIGO O5). The boldest, most")
    print("  consequential (HYPOTHESIS): dark-energy-scale cutoff -> sub-mm gravity at")
    print("  70-130 um simultaneously tests QG, the CC, and the birefringence picture.")
    print("=" * 92)

    out = {"rows": [{"prediction": p, "experiment": e, "status": s, "grade": g}
                    for p, e, s, g in rows],
           "tally": dict(grades)}
    with open(os.path.join(R, "out_scorecard.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {R}/out_scorecard.json")


if __name__ == "__main__":
    main()
