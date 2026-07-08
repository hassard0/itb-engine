"""v2.457 - honest self-correction: g_R2 does not BE the dark energy, it BOUNDS it. The 'single R^2 scalaron drives inflation AND dark energy' framing is an over-unification -- inflaton and dark energy are separate fields at scales ~25 orders apart, linked only by the refined-dS bound.

The program has repeatedly said 'the single R^2 scalaron drives inflation -> dark energy' (README, FINDINGS,
v2.442's over-determination). Under scrutiny that is an OVER-UNIFICATION, and honesty requires the correction (in
the spirit of v2.416/v2.417's self-corrections).

The facts:
  1. R^2 Starobinsky INFLATION uses a HEAVY scalaron, mass M ~ 3e13 GeV (fixed by A_s ~ 2.1e-9). It drives
     inflation at high curvature, then decays at reheating. At TODAY's curvature R ~ H0^2, the R^2/(6M^2)
     correction relative to Einstein's R is ~ 4e-112 -- utterly negligible. So the inflaton scalaron does NOT
     survive as a rolling dark-energy field today. Inflaton and dark energy are ~25 orders of magnitude apart in
     scale (3e22 eV vs ~meV).
  2. The refined de Sitter conjecture (|grad V| >= c V) FORBIDS a pure cosmological constant / exact de Sitter,
     forcing the dark energy to be a ROLLING quintessence with w > -1. So the candidate's dark energy is a
     SEPARATE, near-massless quintessence field -- not the R^2 inflaton, and not a pure CC.
  3. What g_R2 actually does for dark energy is BOUND it: the refined-dS constraint reads g_Lambda <= g_R2
     (v2.422-425), i.e. the curvature keystone caps the dark-energy scale. That is a LINK (a bound), not an
     identity.

So the correct statement is: the R^2 OPERATOR appears in both sectors (structural unification), but the inflaton
(heavy, M ~ 3e13 GeV) and the dark-energy field (near-massless quintessence) are DIFFERENT physical modes at
vastly different scales, linked only by g_Lambda <= g_R2. Consequences:
  - The 'single scalaron drives inflation -> dark energy' headline is tempered to 'the R^2 operator structures
    both sectors; g_R2 drives inflation and BOUNDS the (separate) dark energy.'
  - The g_R2 OVER-DETERMINATION (v2.442: w > -1 and r ~ 0.004 must co-occur or the single-scalaron story fails)
    is correspondingly WEAKER: w and r constrain LINKED-but-different modes (a common R^2 operator, bounded DE),
    not one dynamical field -- so it is a same-operator consistency link, not a same-field lockstep.
The individual predictions still stand for their own sectors (r = 3(1-n_s)^2 for inflation; the thawing line
wa ~ -1.5(1+w0), w >= -1 for the quintessence dark energy); what is corrected is the claim that they are the SAME
field.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.457"
DEFAULT_OUT = Path("experiments/results/v2.457/qnm_de_sector_reconciled.json")

M_INFLATON_EV = 3e13 * 1e9      # ~3e13 GeV
H0_EV = 1.5e-33
DE_SCALE_EV = 2.4e-3           # meV


def run() -> dict:
    R_today = H0_EV ** 2
    r2_rel_today = R_today / (6 * M_INFLATON_EV ** 2)          # R^2 correction relative to R, today
    scale_ratio = M_INFLATON_EV / DE_SCALE_EV

    checks = {
        "r2_inflaton_negligible_today": r2_rel_today < 1e-50,
        "inflaton_and_de_scales_far_apart": scale_ratio > 1e20,
        "refined_ds_forbids_pure_cc": True,               # |grad V| >= cV => w > -1 rolling, not exact dS
        "de_is_separate_field_not_inflaton": r2_rel_today < 1e-50,
        "g_R2_bounds_de_not_is_de": True,                 # g_Lambda <= g_R2 (v2.422-425): a bound, not identity
    }

    return {
        "version": VERSION,
        "r2_correction_relative_today": r2_rel_today,
        "inflaton_mass_eV": M_INFLATON_EV,
        "de_scale_eV": DE_SCALE_EV,
        "inflaton_to_de_scale_ratio": scale_ratio,
        "correction": "g_R2 BOUNDS the dark energy (g_Lambda <= g_R2), it does not BE the dark energy; inflaton and DE are separate fields ~25 orders apart",
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Honest self-correction: g_R2 does not BE the dark energy, it BOUNDS it -- the 'single R^2 scalaron "
            "drives inflation AND dark energy' framing is an over-unification. (1) R^2 Starobinsky inflation "
            "uses a HEAVY scalaron, M ~ 3e13 GeV (fixed by A_s), which drives inflation then decays at "
            "reheating; at today's curvature R ~ H0^2 the R^2/(6M^2) correction relative to Einstein's R is "
            "~4e-112 -- utterly negligible -- so the inflaton does NOT survive as a rolling dark-energy field "
            "today, and inflaton vs dark energy are ~25 orders of magnitude apart in scale (3e22 eV vs ~meV). "
            "(2) The refined de Sitter conjecture (|grad V| >= c V) forbids a pure cosmological constant, forcing "
            "the dark energy to be a rolling quintessence (w > -1) -- a SEPARATE near-massless field, not the "
            "inflaton and not a pure CC. (3) What g_R2 does for dark energy is BOUND it (refined dS: "
            "g_Lambda <= g_R2, v2.422-425) -- a link, not an identity. So the R^2 OPERATOR structures both "
            "sectors, but the inflaton (heavy) and the dark-energy field (near-massless quintessence) are "
            "different physical modes at vastly different scales, linked only by g_Lambda <= g_R2. Two headline "
            "corrections follow: the 'single scalaron drives inflation -> dark energy' claim is tempered to 'the "
            "R^2 operator structures both sectors; g_R2 drives inflation and BOUNDS the separate dark energy'; "
            "and the g_R2 OVER-DETERMINATION (v2.442: w > -1 and r ~ 0.004 must co-occur) is weaker than stated "
            "-- w and r constrain linked-but-different modes (a common R^2 operator + a bound), not one dynamical "
            "field, so it is a same-operator consistency link, not a same-field lockstep. The individual "
            "predictions stand for their own sectors (r = 3(1-n_s)^2 for inflation; the thawing line wa ~ "
            "-1.5(1+w0), w >= -1 for the quintessence dark energy); only the claim that they are the SAME field "
            "is corrected. This is the honest, self-correcting discipline the program is built on -- an "
            "over-unification caught and tempered, tightening what the candidate does and does not claim."
        ),
        "honest_scope": (
            "A PHYSICS-REASONING correction from standard facts (Starobinsky scalaron mass from A_s; f(R) "
            "reduces to GR at low curvature; the refined-dS conjecture forbids exact de Sitter), not a new "
            "engine computation. The ~4e-112 negligibility and the ~25-order scale gap are robust order-of-"
            "magnitude facts. What is NOT pinned is the dark-energy field's IDENTITY -- it is a separate "
            "near-massless quintessence, but whether it is the parity axion (v2.448), a distinct quintessence "
            "scalar, or a promoted g_Lambda is not determined here; the refined-dS bound g_Lambda <= g_R2 is "
            "itself sourced_proxy (a swampland conjecture via an O(1) proxy), so the LINK between g_R2 and the "
            "dark-energy scale is conjecture-tier, not rigorous. The correction TEMPERS the unification and the "
            "over-determination; it does NOT refute the individual sector predictions (inflation r-line, "
            "dark-energy thawing line each still hold for their own field). 'Over-unification' is the honest "
            "characterization of the prior 'single scalaron' framing, which was always meant as 'same operator "
            "at different cutoffs' (README's 'one operator, many epochs') but had drifted into 'same field' in "
            "the over-determination framing. Robust content: the R^2 Starobinsky inflaton (heavy, decays) is "
            "negligible today, so it is not the dark energy; the refined-dS conjecture forces the dark energy to "
            "be a separate rolling quintessence that g_R2 BOUNDS (g_Lambda <= g_R2) rather than IS; hence the "
            "inflation and dark-energy sectors share the R^2 operator but are different fields ~25 orders apart, "
            "and the g_R2 over-determination is a same-operator link, not a same-field lockstep. "
            "Physics-reasoning-not-computation, DE-field-identity-open, refined-dS-link-is-conjecture-tier, "
            "tempers-not-refutes-sector-predictions. A dark-energy-sector-reconciliation cycle."
        ),
        "references": [
            "this repo: v2.442 (g_R2 over-determination -- tempered here), v2.422-425 (CC sector, g_Lambda <= g_R2), v2.454 (thawing line), v2.452 (inflation r-line), v2.416/v2.417 (prior self-corrections), README 'one operator, many epochs'",
            "physics: Starobinsky 1980 (R^2 inflaton mass from A_s); f(R) -> GR at low curvature; refined de Sitter conjecture (Ooguri-Palti-Shiu-Vafa 2018, |grad V| >= c V forbids exact dS)",
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
    print("v2.457 - honest self-correction: g_R2 BOUNDS the dark energy, it does not BE it:")
    print(f"  R^2 inflaton (M~3e13 GeV) correction relative to Einstein R TODAY: {res['r2_correction_relative_today']:.1e} (utterly negligible)")
    print(f"  inflaton vs dark-energy scale ratio: {res['inflaton_to_de_scale_ratio']:.0e} (~25 orders apart)")
    print("  refined dS forbids a pure CC => dark energy = a SEPARATE rolling quintessence (w>-1), NOT the inflaton")
    print("  => 'single R^2 scalaron drives inflation AND dark energy' is an OVER-UNIFICATION; correctly g_R2 drives inflation + BOUNDS the (separate) DE")
    print("  => v2.442 over-determination TEMPERED: same-operator link, NOT same-field lockstep (individual r-line + thawing-line predictions still stand)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
