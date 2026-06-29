"""v2.247 - Black-hole echoes: the ringdown delay that probes horizon-scale new physics.

A fresh QG-at-the-horizon thread. If the event horizon is replaced by a quantum-corrected REFLECTIVE
surface at r = 2M(1 + epsilon) -- a firewall, fuzzball, gravastar, or any "exotic compact object"
(ECO) motivated by the black-hole information paradox -- then waves that would have fallen through the
horizon instead reflect and bounce between the surface and the photon-sphere potential barrier. The
ringdown is then followed by a train of ECHOES, delayed by the round-trip light-crossing time in the
tortoise coordinate:

    Delta t_echo = 2 [ r*(barrier) - r*(surface) ] ,   r*(r) = r + 2M ln(r/2M - 1),

with the barrier at the photon sphere (r = 3M) and the surface at r = 2M(1+epsilon). Because
r*(surface) = 2M(1+epsilon) + 2M ln(epsilon) diverges only LOGARITHMICALLY as epsilon -> 0, the echo
delay is

    Delta t_echo ~ -4M ln(epsilon)    (leading) ,

so even a PLANCK-SCALE surface (epsilon ~ 1e-40) gives only Delta t ~ M * O(few hundred) -- a long but
finite, observable delay. That logarithmic sensitivity is what makes ringdown echoes a probe of
horizon-scale quantum structure: the LIGO/Virgo echo searches look for exactly this delayed repetition.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VERSION = "v2.247"
DEFAULT_OUT = Path("experiments/results/v2.247/qnm_black_hole_echoes.json")
M_SEC = 4.925e-6        # G M_sun / c^3 in seconds


def rstar(r: float) -> float:
    """Tortoise coordinate (M=1): r* = r + 2 ln(r/2 - 1)."""
    return r + 2 * math.log(r / 2 - 1)


def rstar_surface(eps: float) -> float:
    """r* at the reflective surface r = 2(1+eps); r/2-1 = eps exactly (avoids cancellation)."""
    return 2 * (1 + eps) + 2 * math.log(eps)


def echo_delay_M(eps: float) -> float:
    """Echo time delay in units of M (round-trip surface <-> photon-sphere barrier)."""
    return 2 * (rstar(3.0) - rstar_surface(eps))


def run() -> dict:
    eps_grid = [1e-4, 1e-10, 1e-20, 1e-40]
    scaling = [{"epsilon": e, "echo_delay_M": echo_delay_M(e), "minus_4_ln_eps": -4 * math.log(e)}
               for e in eps_grid]
    # log-sensitivity check: 1e36x change in epsilon only ~10x the delay
    log_sensitive = echo_delay_M(1e-40) / echo_delay_M(1e-4) < 12
    # physical echo delays for a Planck-scale surface (eps ~ 1e-40)
    systems = [(30.0, "30 Msun stellar BH (LIGO)"), (62.0, "GW150914 remnant"),
               (4.3e6, "Sgr A* (4.3e6 Msun)")]
    phys = [{"system": label, "mass_solar": M,
             "echo_delay_s_planck": echo_delay_M(1e-40) * M * M_SEC} for M, label in systems]
    return {
        "version": VERSION,
        "method": ("echo delay = 2[r*(3M) - r*(2M(1+eps))] from the tortoise coordinate; reflective "
                   "surface at r=2M(1+eps); M=1 for the delay-in-M, then * (G M_sun/c^3) for seconds"),
        "log_scaling": scaling,
        "delay_is_log_sensitive": bool(log_sensitive),
        "physical_echo_delays_planck": phys,
        "finding": (
            "Black-hole echoes turn the ringdown into a probe of horizon-scale new physics. A "
            "reflective surface at r = 2M(1+epsilon) produces echoes delayed by Delta t ~ -4M "
            "ln(epsilon): the delay grows only LOGARITHMICALLY as the surface approaches the horizon, "
            "so a Planck-scale surface (epsilon ~ 1e-40) gives Delta t ~ 368 M -- "
            f"{phys[0]['echo_delay_s_planck']*1e3:.0f} ms for a 30 Msun black hole, "
            f"{phys[1]['echo_delay_s_planck']*1e3:.0f} ms for the GW150914 remnant, and ~"
            f"{phys[2]['echo_delay_s_planck']/3600:.1f} hours for Sgr A*. The 36-orders-of-magnitude "
            "range of epsilon (1e-4 to 1e-40) changes the delay only ~10x, so the delay is a clean, "
            "weakly-model-dependent observable: detecting (or bounding) post-ringdown echoes at this "
            "delay tests whether the remnant has a true horizon or a quantum-corrected surface -- the "
            "information-paradox question, made observational. This is exactly what the LIGO/Virgo "
            "echo searches target."
        ),
        "honest_scope": (
            "This is the geometric-optics ECHO DELAY (the leading round-trip light-crossing time), "
            "exact for the Schwarzschild tortoise coordinate. The full echo WAVEFORM -- amplitudes, "
            "the surface reflectivity, the progressive damping and frequency content of successive "
            "echoes, and the spinning (Kerr) case -- requires solving the wave equation with the "
            "modified inner boundary condition (not done here). The epsilon <-> Planck-scale relation "
            "is convention-dependent (coordinate vs proper distance differ by O(1) in ln), so the "
            "physical delays are order-of-magnitude. Echoes remain a debated/unconfirmed signal in "
            "the data. Reconstruction of a real QG-at-the-horizon observable, not a detection claim. "
            "Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Cardoso, Franzin, Pani, PRL 116 (2016) 171101 -- ringdown is not the horizon / echoes",
            "Cardoso & Pani, Living Rev. Rel. 22 (2019) 4 -- testing the nature of compact objects",
            "Abedi, Dykaar, Afshordi, PRD 96 (2017) 082004 -- LIGO echo search",
            "this repo: v2.210 (tortoise coordinate / QNM solver)",
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
    print(" epsilon    echo delay (M)   -4 ln(eps)")
    for s in res["log_scaling"]:
        print(f" {s['epsilon']:.0e}   {s['echo_delay_M']:8.2f}        {s['minus_4_ln_eps']:8.2f}")
    print(f"\n delay log-sensitive (1e36x eps -> <12x delay) = {res['delay_is_log_sensitive']}")
    print(" physical echo delay (Planck-scale eps=1e-40):")
    for ph in res["physical_echo_delays_planck"]:
        print(f"  {ph['system']:28s} {ph['echo_delay_s_planck']:.3e} s")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
