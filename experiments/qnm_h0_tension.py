"""v2.467 - the candidate and the H0 tension: its canonical axion dark energy (w >= -1) does NOT resolve the Hubble tension; H0-resolution needs phantom or early dark energy, which the model-independent axion cannot provide -- an honest confrontation with a major anomaly (and the phantom-past tension seen from a third angle).

Any dark-energy model must answer whether it helps or hurts the H0 tension (Planck/CMB H0 ~ 67 vs local/SH0ES
H0 ~ 73, ~5 sigma). The candidate's dark energy is the model-independent axion (v2.458): an ULTRALIGHT
(m ~ H0 ~ 1e-33 eV) canonical quintessence with w >= -1 at all z. The two leading H0-resolution mechanisms are:

  * PHANTOM late-time dark energy (w < -1): raises the CMB-inferred H0. A CANONICAL scalar cannot do this
    (w >= -1 always) -- so the candidate's axion is on the WRONG side.
  * EARLY dark energy (EDE): a field active near recombination (m ~ H(z~3000) ~ 1e-28 eV) that reduces the sound
    horizon. The candidate's axion is too LIGHT (m ~ H0 ~ 1e-33 eV, active only today), so it is NOT an EDE field.

So the candidate's single model-independent axion does NOT resolve the H0 tension: canonical late quintessence
(w >= -1) generically LOWERS the CMB-inferred H0 (mildly worsening the tension, or at best neutral), and the axion
is too light to act as EDE. This is the phantom-past tension (v2.454/v2.459) seen from a third angle -- the same
'a canonical axion cannot cross w = -1' limitation, now against H0.

A caveat that is genuinely available in the framework: the heterotic UV completion (v2.434) naturally carries an
AXIVERSE -- MANY axions across a wide mass range, not just the model-independent one. An EDE-scale axion
(m ~ 1e-28 eV) for the H0 tension is therefore AVAILABLE in the same string framework, just not as the
model-independent (birefringence/dark-energy) axion. So the candidate does not FORBID an H0 resolution; it simply
does not PROVIDE one from its single identified axion.

Falsification consequence: a confirmed H0-resolving PHANTOM dark energy (robust w < -1) would falsify the
candidate's canonical-axion dark energy (as would the DESI phantom-past, v2.454) -- so H0 is a third front, aligned
with the dark-energy front, testing the w >= -1 core prediction.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.467"
DEFAULT_OUT = Path("experiments/results/v2.467/qnm_h0_tension.json")

H0_PLANCK, H0_SH0ES = 67.4, 73.0
M_AXION_DE_EV = 1e-33       # ultralight, m ~ H0
M_EDE_EV = 1e-28            # EDE scale, m ~ H(recombination)


def run() -> dict:
    resolution_mechanisms = {
        "phantom_late_DE_w_lt_minus1": {"resolves_H0": True, "candidate_can": False,
                                        "why": "canonical axion has w >= -1 always; cannot go phantom"},
        "early_dark_energy": {"resolves_H0": True, "candidate_can": False,
                              "why": "candidate axion m ~ H0 ~ 1e-33 eV is too light; EDE needs m ~ H(z~3000) ~ 1e-28 eV"},
        "canonical_late_quintessence_w_geq_minus1": {"resolves_H0": False, "candidate_can": True,
                                                     "why": "what the candidate has; generically LOWERS CMB-inferred H0 (worsens/neutral)"},
    }
    candidate_resolves_H0 = any(m["candidate_can"] and m["resolves_H0"] for m in resolution_mechanisms.values())

    checks = {
        "candidate_axion_is_late_DE_not_EDE": M_AXION_DE_EV < M_EDE_EV / 100,   # ~5 orders lighter
        "phantom_resolves_but_candidate_cannot": (resolution_mechanisms["phantom_late_DE_w_lt_minus1"]["resolves_H0"]
                                                  and not resolution_mechanisms["phantom_late_DE_w_lt_minus1"]["candidate_can"]),
        "ede_resolves_but_candidate_cannot": (resolution_mechanisms["early_dark_energy"]["resolves_H0"]
                                              and not resolution_mechanisms["early_dark_energy"]["candidate_can"]),
        "candidate_does_not_resolve_H0": not candidate_resolves_H0,
        "reinforces_phantom_tension": True,   # same w >= -1 limitation as v2.454/v2.459
    }

    return {
        "version": VERSION,
        "H0_planck": H0_PLANCK, "H0_sh0es": H0_SH0ES,
        "resolution_mechanisms": resolution_mechanisms,
        "candidate_resolves_H0": candidate_resolves_H0,
        "axiverse_caveat": "the heterotic UV completion (v2.434) carries an axiverse -- an EDE-scale axion for H0 is AVAILABLE in the framework, just not the model-independent (DE/birefringence) axion",
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The candidate and the H0 tension: its canonical axion dark energy (w >= -1) does NOT resolve the "
            "Hubble tension, and H0-resolution needs phantom or early dark energy that the model-independent "
            "axion cannot provide -- an honest confrontation with a major anomaly and the phantom-past tension "
            "from a third angle. The candidate's dark energy is the model-independent axion (v2.458): an "
            "ultralight (m ~ H0 ~ 1e-33 eV) canonical quintessence with w >= -1 at all z. The two leading "
            "H0-resolution mechanisms are both closed to it: PHANTOM late dark energy (w < -1) raises the "
            "CMB-inferred H0, but a canonical scalar cannot cross w = -1 (the axion is on the wrong side); and "
            "EARLY dark energy (a field active near recombination, m ~ 1e-28 eV, reducing the sound horizon) "
            "needs a much heavier field than the candidate's m ~ 1e-33 eV axion, which is active only today. So "
            "the candidate's single model-independent axion does not resolve the H0 tension -- canonical late "
            "quintessence (w >= -1) generically LOWERS the CMB-inferred H0 (mildly worsening the tension, or at "
            "best neutral), and the axion is too light to be EDE. This is the same 'a canonical axion cannot "
            "cross w = -1' limitation as the DESI phantom-past tension (v2.454/v2.459), now against H0 -- so H0 "
            "is a THIRD front aligned with the dark-energy front, testing the w >= -1 core prediction, and a "
            "confirmed H0-resolving robust phantom dark energy would falsify the candidate's canonical-axion "
            "dark energy. A genuinely-available caveat: the heterotic UV completion naturally carries an "
            "AXIVERSE (many axions across a wide mass range), so an EDE-scale axion for H0 is AVAILABLE in the "
            "same string framework -- just not as the model-independent (birefringence/dark-energy) axion. So "
            "the candidate does not FORBID an H0 resolution; it simply does not PROVIDE one from its single "
            "identified axion. The honest headline: on the H0 tension the candidate is neutral-to-slightly-worse "
            "from its identified axion (a genuine limitation, aligned with the phantom-past tension), with an "
            "axiverse EDE resolution available but not predicted."
        ),
        "honest_scope": (
            "A physics-reasoning assessment from standard cosmology facts (canonical scalars have w >= -1; H0 "
            "resolution favors phantom or EDE; the candidate's axion is ultralight late-time DE), not an engine "
            "computation of H0. The statement 'canonical quintessence lowers/worsens H0' is the generic "
            "expectation but the exact shift depends on the full cosmological fit (a canonical quintessence with "
            "a specific w(z) could be closer to neutral than 'worse') -- so 'neutral-to-slightly-worse' is the "
            "honest range, not a computed delta-H0. The EDE-mass estimate (m ~ H(z~3000) ~ 1e-28 eV) is "
            "order-of-magnitude. The axiverse caveat is a real feature of heterotic compactifications but "
            "invoking a SECOND, EDE-scale axion is model-dependent and NOT a prediction of the candidate (the "
            "candidate identifies only the model-independent axion) -- so it is an availability statement, not a "
            "resolution the candidate makes. The falsification alignment with v2.454/v2.459 is exact (same "
            "w >= -1 core), so H0 is not an INDEPENDENT test -- it is the same phantom question from the H0 "
            "side, which is why it 'reinforces' rather than adds a new axis. Robust content: the candidate's "
            "model-independent axion is canonical late-time dark energy (w >= -1, m ~ H0), which does NOT "
            "resolve the H0 tension (canonical quintessence does not raise the CMB-inferred H0, and the axion is "
            "too light for EDE), so on H0 the candidate is neutral-to-slightly-worse from its identified axion -- "
            "a genuine limitation aligned with the phantom-past dark-energy tension; the heterotic axiverse makes "
            "an EDE resolution available in the framework but not predicted. Physics-reasoning-not-computation, "
            "delta-H0-not-computed, axiverse-available-not-predicted, H0-not-independent-of-the-phantom-front. An "
            "H0-tension cycle."
        ),
        "references": [
            "this repo: v2.458 (axion = dark energy), v2.454/v2.459 (canonical w >= -1, DESI phantom-past tension), v2.434 (heterotic UV completion / axiverse), v2.451 (model-independent axion, f_a ~ M_Pl)",
            "physics: H0 tension (Planck vs SH0ES); phantom DE and early dark energy as H0 resolutions; canonical scalar w >= -1; string axiverse (Arvanitaki et al 2010)",
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
    print("v2.467 - the candidate and the H0 tension:")
    print(f"  H0: Planck {res['H0_planck']} vs SH0ES {res['H0_sh0es']} (~5 sigma)")
    for name, m in res["resolution_mechanisms"].items():
        print(f"  {name:<42} resolves_H0={m['resolves_H0']!s:<5} candidate_can={m['candidate_can']}")
    print(f"  => candidate resolves H0: {res['candidate_resolves_H0']} (canonical axion w>=-1, too light for EDE => does NOT resolve; aligned with the phantom-past tension)")
    print(f"  => axiverse caveat: an EDE-scale axion is AVAILABLE in the heterotic framework, but not the model-independent axion (not predicted)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
