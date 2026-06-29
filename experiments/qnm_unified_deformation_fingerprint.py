"""v2.238 - Unified deformation fingerprint: one non-Kerr parameter, all strong-field observables.

Capstone of the v2.229-v2.237 strong-field-test sub-program. The photon sphere, shadow, ringdown,
ISCO, and accretion efficiency are all geodesic/eikonal functionals of the SAME metric f(r). A
single non-Kerr / higher-curvature deformation (f = 1 - 2/r + eps/r^3, M=1) therefore shifts ALL of
them coherently. This cycle assembles the complete fractional-response vector -- the multi-observable
EM + GW fingerprint a real exotic / quantum-corrected compact object would imprint -- from the
already-validated machinery (v2.231 photon sphere, v2.237 ISCO), each channel reproducing its GR
baseline.

Channels (and their messenger):
  shadow radius b_c            EM   (the imaged photon ring)
  ringdown frequency Omega_c   GW   (eikonal QNM real part; locked to 1/b_c)
  ringdown damping lambda      GW   (eikonal QNM imaginary part; Lyapunov rate)
  ISCO radius r_ISCO           --   (geometric)
  accretion efficiency eta     EM   (thin-disk luminosity, = 1 - E_ISCO)
  ISCO / merger frequency      GW   (inspiral-to-merger transition)

The fingerprint is the joint pattern of fractional shifts: which observables move together (the
shadow<->ringdown-frequency locking, v2.231), which independently (damping, ISCO, efficiency), and
the EM/GW correlations that make a single deformation falsifiable across both channels.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_isco_accretion import isco
from experiments.qnm_photon_sphere_deviation import geodesics

VERSION = "v2.238"
DEFAULT_OUT = Path("experiments/results/v2.238/qnm_unified_deformation_fingerprint.json")
K = 3          # deformation f = 1 - 2/r + eps/r^K
H = 1e-4


def observables(eps: float) -> dict:
    g = geodesics(eps, K)          # b_c, Omega_c (photon), lambda
    i = isco(eps, K)               # r_isco, E_isco, efficiency, Omega_isco
    return {
        "shadow_b_c": g["b_c"],
        "ringdown_freq_Omega_c": g["Omega_c"],
        "ringdown_damping_lambda": g["lambda"],
        "isco_radius": i["r_isco"],
        "accretion_efficiency": i["efficiency"],
        "merger_freq_Omega_isco": i["Omega_isco"],
    }


CHANNEL = {
    "shadow_b_c": "EM", "ringdown_freq_Omega_c": "GW", "ringdown_damping_lambda": "GW",
    "isco_radius": "geom", "accretion_efficiency": "EM", "merger_freq_Omega_isco": "GW",
}


def run() -> dict:
    base = observables(0.0)
    p, m = observables(H), observables(-H)
    # fractional sensitivity d ln(obs)/d eps (use absolute d/d eps for efficiency to avoid 0-div issues)
    frac = {}
    absd = {}
    for k in base:
        d = (p[k] - m[k]) / (2 * H)
        absd[k] = d
        frac[k] = d / base[k]
    # the shadow<->ringdown-frequency locking (Omega_c = 1/b_c): fractional shifts equal & opposite
    locking_residual = frac["ringdown_freq_Omega_c"] + frac["shadow_b_c"]
    return {
        "version": VERSION,
        "method": ("single deformation f=1-2/r+eps/r^3; assemble the fractional response of all "
                   "geodesic/eikonal strong-field observables (v2.231 photon sphere + v2.237 ISCO); "
                   "M=1"),
        "gr_baseline": base,
        "channel": CHANNEL,
        "fractional_sensitivity_d_ln_d_eps": frac,
        "absolute_sensitivity_d_d_eps": absd,
        "shadow_ringdown_locking_residual": locking_residual,
        "fingerprint": {
            "EM_channels": {k: frac[k] for k in base if CHANNEL[k] == "EM"},
            "GW_channels": {k: frac[k] for k in base if CHANNEL[k] == "GW"},
        },
        "finding": (
            "A single non-Kerr deformation (eps/r^3) imprints a COHERENT fingerprint across every "
            "strong-field observable, each reproduced at its GR baseline (shadow b_c=5.196, "
            "ringdown Omega_c=lambda=0.1925, ISCO r=6, efficiency 5.72%, merger Omega=0.0680). The "
            "fractional responses d ln/d eps: shadow shrinks (-0.056) while the ringdown frequency "
            "rises (+0.056) -- EXACTLY locked (residual "
            f"{locking_residual:.1e}, the Omega_c=1/b_c identity, v2.231); the ringdown damping "
            f"({frac['ringdown_damping_lambda']:+.3f}), ISCO radius "
            f"({frac['isco_radius']:+.3f}), accretion efficiency "
            f"({frac['accretion_efficiency']:+.3f}), and merger frequency "
            f"({frac['merger_freq_Omega_isco']:+.3f}) respond INDEPENDENTLY. So the same deformation "
            "raises the disk efficiency and merger frequency (both up) while shrinking the shadow "
            "and pulling the ISCO inward -- a correlated EM+GW signature: the shadow (EM imaging), "
            "ringdown (GW post-merger), disk efficiency (EM luminosity), and merger frequency (GW "
            "inspiral) are NOT independent knobs but one deformation seen six ways, which is what "
            "makes it falsifiable across channels."
        ),
        "honest_scope": (
            "Eikonal (large-l) ringdown + static-spherical Schwarzschild baseline + linear "
            "deformation response (the v2.229-v2.237 caveats compound here). The deformation eps/r^3 "
            "is illustrative, not a derived QG metric; Kerr/rotation would split the locked channels "
            "and add frame-dragging. This is a SYNTHESIS of the prior validated cycles (each channel "
            "reproduces its baseline), assembling the joint fingerprint -- not a new measurement or "
            "bound. The static tidal Love number (v2.235/v2.236) is the complementary static channel "
            "(different machinery), also lifted by the deformation. Parity-odd g_R4_c3 stays dark "
            "(v2.209)."
        ),
        "references": [
            "this repo: v2.229-v2.232 (photon sphere / shadow / deviation), v2.237 (ISCO), v2.235-236 (tidal)",
            "Cardoso et al., PRD 79 (2009) 064016; Bardeen-Press-Teukolsky, ApJ 178 (1972) 347",
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
    print("observable                  channel   GR baseline    d ln/d eps")
    for k, v in res["gr_baseline"].items():
        print(f"  {k:26s} {res['channel'][k]:5s}   {v:9.5f}    {res['fractional_sensitivity_d_ln_d_eps'][k]:+.4f}")
    print(f"shadow<->ringdown-freq locking residual = {res['shadow_ringdown_locking_residual']:.1e}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
