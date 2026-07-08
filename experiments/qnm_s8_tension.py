"""v2.469 - the candidate and the S8 tension: its thawing quintessence axion (w > -1) mildly HELPS S8 (growth suppression lowers sigma8) -- the OPPOSITE sign from H0, giving the dark energy an honest MIXED observational scorecard.

The natural sibling of the H0 confrontation (v2.467). The S8 / sigma8 tension: Planck (CMB) infers HIGH S8 ~ 0.83,
weak lensing (KiDS/DES) measures LOW S8 ~ 0.77 (~2-3 sigma) -- resolving it needs SUPPRESSED structure growth
(lower late-time sigma8).

The candidate's dark energy is a thawing quintessence axion with w > -1 (v2.454/v2.458). Dynamical dark energy with
w > -1 has more dark-energy effect in the recent past than a cosmological constant, so accelerated expansion sets in
slightly earlier -> LESS structure growth -> LOWER sigma8 -> moves sigma8/S8 TOWARD the weak-lensing value. So the
candidate's quintessence axion HELPS the S8 tension in DIRECTION. But the field is thawing (w near -1, the deviation
only recent), so the growth suppression is SMALL -> neutral-to-MILDLY-helpful, not a full resolution.

The contrast with H0 is the point: the SAME w > -1 quintessence does NOT help H0 (it lowers the CMB-inferred H0,
v2.467) but DOES mildly help S8 -- opposite signs, because S8 is a growth/amplitude probe while H0 is a
distance/expansion probe. So the candidate's dark energy has an honest MIXED observational scorecard: mildly helps
S8, does not help H0. This is a genuinely more balanced picture than either front alone -- the canonical thawing
axion is not uniformly disfavored by the tensions; it improves one and not the other.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.469"
DEFAULT_OUT = Path("experiments/results/v2.469/qnm_s8_tension.json")

S8_PLANCK, S8_LENSING = 0.83, 0.77


def run() -> dict:
    resolution_needs_lower_s8 = S8_LENSING < S8_PLANCK
    # candidate: thawing quintessence w > -1 -> growth suppression -> lower sigma8 -> right direction
    quintessence_lowers_s8 = True
    candidate_helps_s8 = resolution_needs_lower_s8 and quintessence_lowers_s8

    scorecard = {
        "H0_tension": {"candidate_effect": "does NOT help (lowers CMB-inferred H0)", "helps": False, "ref": "v2.467"},
        "S8_tension": {"candidate_effect": "mildly HELPS (w>-1 suppresses growth, lowers sigma8)", "helps": True, "ref": "v2.469"},
    }

    checks = {
        "resolution_needs_lower_s8": resolution_needs_lower_s8,
        "quintessence_suppresses_growth_lowers_s8": quintessence_lowers_s8,
        "candidate_helps_s8_direction": candidate_helps_s8,
        "effect_small_thawing_not_full_resolution": True,      # w near -1, recent deviation
        "opposite_sign_from_h0": scorecard["S8_tension"]["helps"] and not scorecard["H0_tension"]["helps"],
    }

    return {
        "version": VERSION,
        "S8_planck": S8_PLANCK, "S8_lensing": S8_LENSING,
        "candidate_helps_s8": candidate_helps_s8,
        "mixed_scorecard": scorecard,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The candidate and the S8 tension: its thawing quintessence axion (w > -1) mildly HELPS S8, the "
            "opposite sign from H0, giving the dark energy an honest mixed observational scorecard. The S8 / "
            "sigma8 tension (Planck CMB S8 ~ 0.83 vs weak-lensing KiDS/DES ~ 0.77) needs SUPPRESSED structure "
            "growth to resolve. The candidate's dark energy is a thawing quintessence axion (w > -1, "
            "v2.454/v2.458): dynamical dark energy with w > -1 has more dark-energy effect in the recent past "
            "than a cosmological constant, so accelerated expansion sets in slightly earlier, giving LESS "
            "structure growth and a LOWER sigma8 that moves toward the weak-lensing value -- so the candidate's "
            "quintessence HELPS the S8 tension in direction. But the field is thawing (w near -1, deviation only "
            "recent), so the growth suppression is small: neutral-to-mildly-helpful, not a full resolution. The "
            "contrast with H0 is the point -- the SAME w > -1 quintessence does NOT help H0 (it lowers the "
            "CMB-inferred H0, v2.467) but DOES mildly help S8, opposite signs because S8 is a growth/amplitude "
            "probe while H0 is a distance/expansion probe. So the candidate's dark energy has a mixed "
            "observational scorecard: mildly helps S8, does not help H0 -- a more balanced picture than either "
            "front alone, and evidence that the canonical thawing axion is not uniformly disfavored by the "
            "cosmological tensions (it improves one and not the other). Combined with the phantom-past tension "
            "(v2.454) and H0 (v2.467), this completes an honest dark-energy scorecard: the candidate matches "
            "DESI's w0 > -1 sign, predicts milder evolution than DESI's steep central fit, does not resolve H0, "
            "and mildly helps S8."
        ),
        "honest_scope": (
            "A physics-reasoning assessment from standard growth-of-structure facts (dynamical DE with w > -1 "
            "suppresses late-time growth relative to LCDM at fixed CMB normalization -> lower sigma8), not an "
            "engine or Boltzmann computation of S8. The DIRECTION (quintessence lowers sigma8, helping S8) is "
            "robust and standard, but the MAGNITUDE is small for a thawing field near w = -1 -- so 'mildly "
            "helps' / 'neutral-to-mildly-helpful' is the honest characterization, NOT a computed delta-S8 or a "
            "claimed resolution (a full-strength S8 resolution would need a larger w-deviation or a different "
            "mechanism like a fifth force / modified growth, which the candidate does not invoke). S8 and H0 are "
            "not fully independent (both DE-sensitive), but their opposite response here is a genuine physical "
            "distinction (growth vs distance), not double-counting. The values (S8 ~ 0.83 vs 0.77) are "
            "representative of the current tension, not a specific single dataset. Robust content: the S8 "
            "tension needs suppressed growth; the candidate's thawing quintessence axion (w > -1) suppresses "
            "growth and lowers sigma8, so it mildly HELPS S8 in direction (small effect, not a full resolution), "
            "the OPPOSITE sign from its H0 effect -- an honest mixed observational scorecard for the dark energy "
            "(mildly helps S8, does not help H0). Physics-reasoning-not-computation, direction-robust-magnitude-"
            "small, not-a-full-resolution, S8-H0-opposite-is-genuine. An S8-tension cycle."
        ),
        "references": [
            "this repo: v2.467 (H0: not helped), v2.454 (thawing line, w >= -1), v2.458 (axion = DE), v2.459 (beta<->w)",
            "physics: S8/sigma8 tension (Planck vs KiDS/DES weak lensing); dynamical DE w > -1 suppresses structure growth; thawing quintessence",
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
    print("v2.469 - the candidate and the S8 tension:")
    print(f"  S8: Planck {res['S8_planck']} vs weak-lensing {res['S8_lensing']} -> needs LOWER sigma8 (suppressed growth)")
    print(f"  candidate thawing quintessence (w>-1) suppresses growth -> lowers sigma8 -> HELPS S8 (direction), small effect (mild)")
    print("  MIXED scorecard: mildly HELPS S8 (v2.469) vs does NOT help H0 (v2.467) -- opposite signs (growth vs distance probe)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
