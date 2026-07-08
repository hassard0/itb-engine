"""v2.477 - superstring correction to v2.476: the PHYSICAL open superstring forward residues are r_n = 1/n (not flat), giving double-ratio zeta(3)zeta(5)/zeta(4)^2 = 1.064 -- so v2.476's ~7% match was to the BOSONIC (tachyonic, unphysical) Veneziano; the physically-relevant superstring differs (~24%) and additionally needs a kinematic prefactor. An honest self-correction, fast on the heels of the bold swing.

v2.476 executed the exact fingerprint for the BOSONIC Veneziano amplitude A = Gamma(-s)Gamma(-t)/Gamma(-s-t), whose
forward residues telescope to flat (|r_n| = 1) -> a_k = zeta(k) -> double-ratio 1.232, matching the candidate's
1.322 to ~7%. But the bosonic open string is TACHYONIC and is NOT the heterotic gauge sector. The physically-relevant
amplitude is the open SUPERSTRING (GSO-projected), whose Veneziano factor carries a SUSY shift:

    A_susy = K(s,t) * Gamma(-s) Gamma(-t) / Gamma(1 - s - t)      (K = t_8 F^4 kinematic prefactor)

The Gamma(1-s-t) (vs bosonic Gamma(-s-t)) changes the forward residues from flat to r_n = 1/n (verified
numerically). So the bare-Gamma-factor superstring forward moments are a_k = sum_n (1/n)/n^k = zeta(k+1), and the
scale-clean low double-ratio is

    (a_2 a_4)/a_3^2 = zeta(3) zeta(5)/zeta(4)^2 = 1.064,

which the candidate's 1.322 matches only to ~24% -- FAR worse than the bosonic 1.232 (~7%). Two corrections to
v2.476:
  1. The candidate matched the BOSONIC (tachyonic, unphysical) string better than the physical superstring. v2.476's
     '~7% match to a real string amplitude' overstated -- the real (super)string value is 1.064, ~24% off.
  2. Even 1.064 is only the BARE Gamma-factor; the physical superstring amplitude has a kinematic prefactor K ~
     t_8 F^4 that shifts the effective moments further, so the physical fingerprint is not cleanly pinned here.

So the honest final status: the scale-clean fingerprint TEST is executable (v2.464-466), and the flat-residue result
is an exact fact about the BOSONIC Veneziano Gamma-factor (v2.476) -- but the physically-relevant superstring
fingerprint is DIFFERENT (1.064 bare, plus an uncomputed kinematic prefactor) and does NOT cleanly match the
candidate. The exact-string match is amplitude-dependent and remains an open, honestly-scoped item, not a
established ~7% pass.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.477"
DEFAULT_OUT = Path("experiments/results/v2.477/qnm_superstring_fingerprint_correction.json")

CAND_LOW = 1.322


def susy_forward_residue(n: int, t: float) -> float:
    """Res_{s=n} of Gamma(-s)Gamma(-t)/Gamma(1-s-t), forward -> 1/n."""
    return (-(-1) ** n / math.factorial(n)) * (math.gamma(-t) / math.gamma(1 - n - t))


def run() -> dict:
    z = {2: math.pi ** 2 / 6, 3: 1.2020569, 4: math.pi ** 4 / 90, 5: 1.0369278}
    # numerically confirm susy residues ~ 1/n
    susy_res = {n: abs(susy_forward_residue(n, 1e-6)) for n in range(1, 7)}
    susy_is_one_over_n = all(abs(susy_res[n] - 1.0 / n) < 1e-3 for n in susy_res)

    bosonic_dr = z[2] * z[4] / z[3] ** 2          # a_k = zeta(k)   -> 1.232 (v2.476)
    susy_dr = z[3] * z[5] / z[4] ** 2             # a_k = zeta(k+1) -> 1.064
    d_bosonic = abs(CAND_LOW - bosonic_dr) / bosonic_dr
    d_susy = abs(CAND_LOW - susy_dr) / susy_dr

    checks = {
        "susy_forward_residues_are_one_over_n": susy_is_one_over_n,
        "susy_double_ratio_is_zeta3_zeta5_over_zeta4sq": abs(susy_dr - 1.064) < 0.005,
        "susy_differs_from_bosonic": abs(susy_dr - bosonic_dr) > 0.1,
        "candidate_matches_bosonic_better_than_physical_susy": d_bosonic < d_susy,
        "physical_match_not_established": d_susy > 0.15,   # ~24% is not a clean match
    }

    return {
        "version": VERSION,
        "bosonic_double_ratio": round(bosonic_dr, 4),
        "susy_double_ratio": round(susy_dr, 4),
        "candidate_low_double_ratio": CAND_LOW,
        "match_bosonic_pct": round(d_bosonic * 100, 1),
        "match_susy_pct": round(d_susy * 100, 1),
        "susy_forward_residues": {str(k): round(v, 4) for k, v in susy_res.items()},
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Superstring correction to v2.476: the physical open superstring forward residues are r_n = 1/n (not "
            "flat), giving double-ratio zeta(3)zeta(5)/zeta(4)^2 = 1.064 -- so v2.476's ~7% match was to the "
            "bosonic (tachyonic, unphysical) Veneziano, and the physically-relevant superstring differs (~24%) "
            "and additionally needs a kinematic prefactor. v2.476 executed the exact fingerprint for the bosonic "
            "Veneziano A = Gamma(-s)Gamma(-t)/Gamma(-s-t) (flat forward residues -> a_k = zeta(k) -> 1.232, "
            "matching the candidate's 1.322 to ~7%), but the bosonic open string is tachyonic and is not the "
            "heterotic gauge sector. The physical open superstring has the GSO/SUSY-shifted factor "
            "Gamma(-s)Gamma(-t)/Gamma(1-s-t) (times a t_8 F^4 kinematic prefactor), whose forward residues are "
            "r_n = 1/n (verified numerically), so its bare-factor moments are a_k = zeta(k+1) and the low "
            "double-ratio is zeta(3)zeta(5)/zeta(4)^2 = 1.064 -- which the candidate's 1.322 matches only to "
            "~24%, far worse than the bosonic 1.232. Two corrections: (1) the candidate matched the bosonic "
            "(unphysical) string better than the physical superstring, so v2.476's 'exact match to a real string "
            "amplitude to ~7%' overstated -- the real (super)string value is 1.064; (2) even 1.064 is only the "
            "bare Gamma-factor, and the physical amplitude's kinematic prefactor K ~ t_8 F^4 shifts the effective "
            "moments further, so the physical fingerprint is not cleanly pinned. Honest final status: the "
            "scale-clean fingerprint TEST is executable and the flat-residue result is an exact fact about the "
            "BOSONIC Veneziano Gamma-factor, but the physically-relevant superstring fingerprint is different "
            "(1.064 bare, plus an uncomputed prefactor) and does NOT cleanly match the candidate -- the "
            "exact-string match is amplitude-dependent and remains an open item, not an established ~7% pass. "
            "This is a fast honest self-correction on the heels of the bold v2.476 swing."
        ),
        "honest_scope": (
            "A self-correction from a clean numerical computation (the susy Gamma-factor forward residues are "
            "r_n = 1/n, exact). What is now clear: the 'exact string fingerprint' is amplitude-dependent -- "
            "bosonic Veneziano gives 1.232, the superstring bare Gamma-factor gives 1.064, and the full physical "
            "superstring gauge amplitude additionally has a kinematic prefactor (t_8 F^4) NOT computed here that "
            "shifts it further. So NEITHER 1.232 nor 1.064 is definitively 'the' physical fingerprint; the "
            "prefactor bookkeeping is exactly the error-prone step flagged all along, and it is genuinely "
            "unresolved. The robust content is the CORRECTION: v2.476's ~7% match was to the bosonic (tachyonic) "
            "string, not the physical superstring (which gives 1.064, ~24%), so the 'candidate matches a real "
            "string amplitude to ~7%' claim is retracted/tempered. This does NOT say the candidate is "
            "string-INCONSISTENT -- 1.064 vs 1.322 is a ~24% mismatch at the bare-factor level with the prefactor "
            "uncomputed and the candidate's 1.322 carrying the g_6=g_8 Chebyshev artifact, so the fingerprint "
            "comparison is simply not cleanly established either way. The still-robust prior content: the "
            "double-ratios are scale-independent (v2.464), the candidate's tower is multi-state/string-like in "
            "SHAPE (v2.438/v2.466), and the heterotic ID rests on its OTHER supports (required R^2, "
            "parity/Green-Schwarz). Robust content: the physical open-superstring forward residues are r_n = 1/n "
            "(SUSY shift), so its double-ratio is 1.064 not the bosonic 1.232; v2.476's ~7% candidate match was "
            "to the unphysical bosonic string, the physical superstring is ~24% off and needs an uncomputed "
            "kinematic prefactor, so the exact-string fingerprint match is NOT established -- an amplitude-"
            "dependent open item, honestly retracted from v2.476's headline. Self-correction-of-v2476, "
            "bosonic-vs-super-1.232-vs-1.064, prefactor-uncomputed, not-string-inconsistent-just-not-established, "
            "shape-and-other-supports-still-stand. A superstring-correction cycle."
        ),
        "references": [
            "this repo: v2.476 (bosonic Veneziano fingerprint -- corrected here), v2.466 (flat-Regge), v2.464-465 (scale-clean fingerprint), v2.438 (string-like shape), v2.434 (heterotic ID other supports)",
            "physics: open superstring 4-gauge amplitude K * Gamma(-s)Gamma(-t)/Gamma(1-s-t) (GSO/SUSY shift); bosonic vs super Veneziano; t_8 F^4 kinematic prefactor (uncomputed)",
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
    print("v2.477 - superstring correction to v2.476:")
    print(f"  susy forward residues r_n: {res['susy_forward_residues']}  (= 1/n, NOT flat -- SUSY shift Gamma(1-s-t))")
    print(f"  bosonic double-ratio = {res['bosonic_double_ratio']} (v2.476, candidate match {res['match_bosonic_pct']}%)")
    print(f"  SUPERSTRING double-ratio = {res['susy_double_ratio']} (zeta(3)zeta(5)/zeta(4)^2, candidate match {res['match_susy_pct']}%)")
    print("  => v2.476's ~7% match was to the BOSONIC (tachyonic, unphysical) string; physical superstring is ~24% off + needs a kinematic prefactor")
    print("  => exact-string fingerprint match is NOT established (amplitude-dependent) -- v2.476 headline retracted/tempered")
    print("  HONEST: not string-INCONSISTENT (prefactor uncomputed, Chebyshev caveat); shape + other heterotic supports still stand")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
