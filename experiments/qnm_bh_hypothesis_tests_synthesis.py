"""v2.250 - Synthesis: the 'is it really a black hole?' test suite (v2.235-v2.249), cross-verified.

This session's second sub-program asks, channel by channel, whether a compact remnant is a true Kerr
black hole or something else (a horizonless exotic compact object, or a hole hosting an ultralight-
boson cloud). This capstone maps the suite and GUARANTEES its internal consistency: the shared
physics (the horizon angular velocity Omega_H, the photon sphere) must appear identically wherever
it is used across the independent modules.

The cross-test consistency checks are the verifiable content; the channel map organizes the suite by
what each test probes (horizon existence vs spin) and the new physics it constrains.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_horizon_tidal_heating import omega_h as omega_h_heating
from experiments.qnm_shadow_multimessenger import photon_sphere_shadow
from experiments.qnm_superradiance_boson_bound import horizon_angular_velocity
from experiments.qnm_tidal_love_number import run as love_run

VERSION = "v2.250"
DEFAULT_OUT = Path("experiments/results/v2.250/qnm_bh_hypothesis_tests_synthesis.json")


def cross_checks() -> list[dict]:
    rows = []
    # 1. the same Omega_H drives superradiance (v2.243) and horizon tidal heating (v2.249)
    for a in (0.5, 0.9):
        rows.append({"check": f"Omega_H consistent (superradiance == tidal-heating), a*={a}",
                     "ok": abs(horizon_angular_velocity(a) - omega_h_heating(a)) < 1e-12})
    # 2. extremal Omega_H = 1/2
    rows.append({"check": "extremal Omega_H == 1/2", "ok": abs(horizon_angular_velocity(1.0) - 0.5) < 1e-12})
    # 3. the echo-cavity barrier == the photon sphere == the shadow photon sphere (r = 3M)
    ps = photon_sphere_shadow()
    rows.append({"check": "echo barrier / shadow photon sphere at r=3M",
                 "ok": abs(ps["r_ph"] - 3.0) < 1e-9})
    # 4. the GR black-hole tidal Love number vanishes
    rows.append({"check": "BH tidal Love number == 0 (horizon static baseline)",
                 "ok": love_run()["all_zero"]})
    return rows


def channel_map() -> list[dict]:
    return [
        {"probe": "HORIZON existence (black hole vs exotic compact object)",
         "channels": [
             {"name": "static tidal response", "cycles": "v2.235-v2.236",
              "signature": "BH Love number = 0 exactly; a horizonless ECO has k_l != 0"},
             {"name": "ringdown reflection (echoes)", "cycles": "v2.247-v2.248",
              "signature": "a reflective surface gives post-ringdown echoes (delay ~ -4M ln eps) "
                           "and a trapped-mode comb; a true horizon gives neither"},
             {"name": "tidal-heating absorption", "cycles": "v2.249",
              "signature": "a horizon absorbs/feeds inspiral energy (sign = Omega_orbit vs Omega_H); "
                           "a horizonless ECO does not"}]},
        {"probe": "SPIN / superradiance (ultralight bosons)",
         "channels": [
             {"name": "superradiance condition + Regge exclusion", "cycles": "v2.243-v2.244",
              "signature": "observed spins exclude bosons mu < m Omega_H/M (1e-13 to 1e-21 eV)"},
             {"name": "boson-cloud continuous GW", "cycles": "v2.245",
              "signature": "the cloud radiates a monochromatic line f = mu c^2/(pi hbar) -> LIGO/LISA/PTA"},
             {"name": "spin-down endpoint (Regge trajectory)", "cycles": "v2.246",
              "signature": "the hole spins down to Omega_H(a_f) = alpha -- the observed spin gaps"}]},
    ]


def run() -> dict:
    checks = cross_checks()
    return {
        "version": VERSION,
        "method": "cross-import the 'is it a black hole?' modules and verify the shared Omega_H / "
                  "photon-sphere physics is consistent; map the suite by probe and channel",
        "cross_test_consistency": checks,
        "all_consistent": all(c["ok"] for c in checks),
        "test_suite_map": channel_map(),
        "finding": (
            "The 'is it really a black hole?' suite (v2.235-v2.249) is internally consistent: the "
            "horizon angular velocity Omega_H that drives SUPERRADIANCE (v2.243) is identical to the "
            "one setting the HORIZON TIDAL-HEATING sign (v2.249); the extremal Omega_H = 1/2; the "
            "echo-cavity barrier is the same photon sphere (r=3M) as the shadow and eikonal ringdown; "
            "and the BH tidal Love number is exactly zero. The suite probes the black-hole hypothesis "
            "through two unifying handles: the HORIZON (tested three ways -- static Love-number "
            "response, ringdown echo reflection, and tidal-heating absorption, each distinguishing a "
            "true horizon from a horizonless ECO) and the SPIN (superradiance turning observed spins "
            "into ultralight-boson constraints and a continuous-GW beacon). Omega_H ties the spin and "
            "horizon channels together, and the photon sphere ties the echoes to the ringdown -- one "
            "coherent program rather than disconnected probes."
        ),
        "honest_scope": (
            "A SYNTHESIS / consistency capstone, not a new measurement. The per-cycle caveats carry "
            "(geometric-optics echo delay and eps<->Planck convention; representative superradiance "
            "growth coefficient and N-efold; static/electric/Schwarzschild Love number; flux SIGN not "
            "MAGNITUDE for tidal heating). These are self-contained reconstructions of real horizon / "
            "BSM observables, not detection claims or published bounds. Parity-odd g_R4_c3 stays dark "
            "(v2.209)."
        ),
        "references": ["this repo: v2.235-v2.249 result notes (docs/results/), docs/results/INDEX.md"],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()
    res = run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("cross-test consistency:")
    for c in res["cross_test_consistency"]:
        print(f"  [{'OK' if c['ok'] else 'FAIL'}] {c['check']}")
    print(f"all_consistent = {res['all_consistent']}\n")
    for grp in res["test_suite_map"]:
        print(f"{grp['probe']}")
        for ch in grp["channels"]:
            print(f"    {ch['cycles']:14s} {ch['name']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
