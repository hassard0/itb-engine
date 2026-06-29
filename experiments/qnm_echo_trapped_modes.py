"""v2.248 - The frequency-domain face of echoes: the ECO trapped-mode comb.

v2.247 gave the time-domain echo delay of a horizon-replacing reflective surface. This cycle gives
its frequency-domain face. A train of echoes repeating with period Delta t_echo is, in the frequency
domain, a COMB of narrow resonances -- the trapped quasi-bound modes of the cavity between the
surface and the photon-sphere barrier -- with spacing

    Delta f_comb = 1 / Delta t_echo .

The broad General-Relativity quasinormal mode (the single damped ringdown tone at f_QNM with width
~|omega_I|) is REPLACED by this comb of long-lived trapped modes sitting under the QNM as an
envelope; the number of teeth within the ringdown band is

    N_trapped ~ f_QNM * Delta t_echo

(the number of QNM oscillations in one echo round-trip). So the ECO's ringdown spectrum is
qualitatively different from a black hole's -- a dense set of narrow lines instead of one broad
resonance -- the spectral signature that complements the time-domain echo search.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_black_hole_echoes import echo_delay_M
from experiments.qnm_wkb_solver import schwarzschild_qnm

VERSION = "v2.248"
DEFAULT_OUT = Path("experiments/results/v2.248/qnm_echo_trapped_modes.json")
M_SEC = 4.925e-6
OMEGA_R_220 = schwarzschild_qnm(0).real     # ~0.3737 (M=1)


def f_qnm_hz(mass_solar: float) -> float:
    """Fundamental l=2 ringdown frequency f = omega_R/(2 pi M) in Hz."""
    return OMEGA_R_220 / (2 * math.pi * mass_solar * M_SEC)


def comb_spacing_hz(mass_solar: float, eps: float) -> float:
    """Echo-comb tooth spacing Delta f = 1/Delta t_echo (Hz)."""
    dt = echo_delay_M(eps) * mass_solar * M_SEC
    return 1.0 / dt


def n_trapped(mass_solar: float, eps: float) -> float:
    """Number of trapped-mode teeth within the ringdown band ~ f_QNM * Delta t_echo."""
    dt = echo_delay_M(eps) * mass_solar * M_SEC
    return f_qnm_hz(mass_solar) * dt


def run() -> dict:
    eps = 1e-40                       # Planck-scale surface
    systems = [(30.0, "30 Msun stellar BH"), (62.0, "GW150914 remnant"),
               (4.3e6, "Sgr A* (4.3e6 Msun)")]
    rows = []
    for M, label in systems:
        rows.append({"system": label, "mass_solar": M, "f_QNM_hz": f_qnm_hz(M),
                     "comb_spacing_hz": comb_spacing_hz(M, eps),
                     "n_trapped_modes": n_trapped(M, eps)})
    # N_trapped is scale-invariant (f_QNM ~ 1/M, Delta t ~ M) -> depends only on eps
    n_inv = abs(n_trapped(30.0, eps) - n_trapped(4.3e6, eps)) < 1e-6
    return {
        "version": VERSION,
        "method": ("frequency comb of the echo train: spacing Delta f = 1/Delta t_echo "
                   "(Delta t_echo from v2.247); N_trapped ~ f_QNM Delta t_echo; Planck-scale "
                   "eps=1e-40, l=2 n=0 ringdown"),
        "epsilon": eps,
        "omega_R_220": OMEGA_R_220,
        "trapped_mode_comb": rows,
        "n_trapped_scale_invariant": bool(n_inv),
        "finding": (
            "The reflective surface replaces the black hole's single broad quasinormal mode with a "
            "COMB of narrow trapped modes spaced by Delta f = 1/Delta t_echo. For a Planck-scale "
            f"surface the spacing is {rows[0]['comb_spacing_hz']:.1f} Hz for a 30 Msun hole "
            f"(ringing at f_QNM ~ {rows[0]['f_QNM_hz']:.0f} Hz), so ~{rows[0]['n_trapped_modes']:.0f} "
            "trapped lines sit under the QNM envelope. The number of teeth N ~ f_QNM Delta t_echo is "
            "SCALE-INVARIANT (f_QNM ~ 1/M, Delta t_echo ~ M, so the product depends only on the "
            "surface location epsilon, NOT the black-hole mass): every horizon-replacing ECO with a "
            f"Planck-scale surface shows ~{rows[0]['n_trapped_modes']:.0f} trapped lines in its "
            "ringdown, whether stellar or supermassive. This is the spectral signature -- a dense set "
            "of long-lived narrow resonances instead of one decaying tone -- that the frequency-domain "
            "echo searches look for, complementing the v2.247 time-domain delay."
        ),
        "honest_scope": (
            "The comb spacing Delta f = 1/Delta t_echo and the count N ~ f_QNM Delta t_echo are the "
            "leading cavity-resonance relations (exact for the round-trip phase condition); the "
            "precise trapped-mode FREQUENCIES and WIDTHS require solving the wave equation with the "
            "reflective inner boundary (the modes leak through the barrier, so they have finite width "
            "and are 'quasi-bound', not exactly the comb -- but the spacing is robust). The "
            "geometric-optics/WKB echo delay (v2.247) and its eps<->Planck convention dependence "
            "carry. Schwarzschild (non-rotating); Kerr trapped modes differ. Reconstruction of a real "
            "QG-at-the-horizon observable, not a detection claim. Parity-odd g_R4_c3 stays dark "
            "(v2.209)."
        ),
        "references": [
            "Cardoso, Franzin, Pani, PRL 116 (2016) 171101 -- ringdown / echoes / trapped modes",
            "Maggio, Pani, Ferrari -- ECO quasi-bound mode spectra",
            "this repo: v2.247 (echo delay), v2.210 (QNM solver / tortoise coordinate)",
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
    print(f"Planck-scale eps={res['epsilon']:.0e}:")
    print(" system                 f_QNM (Hz)   comb spacing (Hz)   N trapped")
    for r in res["trapped_mode_comb"]:
        print(f"  {r['system']:22s} {r['f_QNM_hz']:9.2e}   {r['comb_spacing_hz']:9.2e}        "
              f"{r['n_trapped_modes']:.0f}")
    print(f"N_trapped scale-invariant (mass-independent) = {res['n_trapped_scale_invariant']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
