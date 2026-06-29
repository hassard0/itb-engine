"""v2.274 - QNM asymptotics, black-hole area quantization, and the Barbero-Immirzi tension.

A fresh QG thread tying the validated QNM ringdown (v2.210) to black-hole entropy (v2.257/v2.258) and
loop quantum gravity. The highly-damped (n -> infinity) Schwarzschild quasinormal modes have a real
part that approaches a universal value (Hod 1998; Motl 2003; Motl-Neitzke 2003):

    Re(omega_n) -> T_H ln 3 = ln 3 / (8 pi M)     (M=1: 0.04371...).

Bohr's correspondence principle reads this asymptotic frequency as the quantum of a black-hole
transition: emitting it changes the mass by dM = hbar Re(omega_inf), so the horizon AREA changes by

    dA = 32 pi M dM = 32 pi M * (ln 3 / 8 pi M) = 4 ln 3     (the M cancels -- a UNIVERSAL area quantum).

So the area spectrum is evenly spaced, A_N = 4 ln 3 * N, the entropy quantum is dS = dA/4 = ln 3, and
each area quantum carries exactly 3 microstates (Hod) -- a discrete statistical origin of S = A/4. If
this area quantum is matched to the loop-quantum-gravity area spectrum A = 8 pi gamma sum sqrt(j(j+1))
with the lowest spin j=1 (Dreyer 2003), it FIXES the Barbero-Immirzi parameter to
gamma = ln 3 / (2 pi sqrt2) ~ 0.124 -- which DISAGREES with the standard LQG entropy-counting value
gamma ~ 0.2375 (Meissner; Domagala-Lewandowski, j=1/2 dominance). That ~2x tension is a real, famous,
unresolved problem, reported here rather than papered over.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.274"
DEFAULT_OUT = Path("experiments/results/v2.274/qnm_area_quantization.json")

LN3 = math.log(3.0)
GAMMA_STANDARD_LQG = 0.2375   # Meissner / Domagala-Lewandowski entropy-counting value


def hawking_temperature(M: float = 1.0) -> float:
    """T_H = 1/(8 pi M)."""
    return 1.0 / (8.0 * math.pi * M)


def omega_asymptotic_real(M: float = 1.0) -> float:
    """Highly-damped QNM real part Re(omega_inf) = T_H ln 3 = ln 3 / (8 pi M) (Hod/Motl-Neitzke)."""
    return LN3 * hawking_temperature(M)


def area_quantum(M: float = 1.0) -> float:
    """Bohr-correspondence area change per emitted asymptotic quantum: dA = 32 pi M Re(omega_inf)."""
    return 32.0 * math.pi * M * omega_asymptotic_real(M)


def barbero_immirzi_dreyer() -> float:
    """Dreyer's gamma from matching dA = 4 ln 3 to the LQG j=1 minimal area 8 pi gamma sqrt(2)."""
    return LN3 / (2.0 * math.pi * math.sqrt(2.0))


def run() -> dict:
    # 1. the asymptotic QNM real part reproduces the famous 0.0437 numerical value
    w_inf = omega_asymptotic_real(1.0)

    # 2. the area quantum is universal (M-independent) and equals 4 ln 3
    dA = [{"M": M, "area_quantum": area_quantum(M)} for M in (0.5, 1.0, 2.0, 10.0)]
    area_universal = max(abs(d["area_quantum"] - 4.0 * LN3) for d in dA) < 1e-9

    # 3. entropy quantum dS = dA/4 = ln 3 -> exactly 3 microstates per area quantum
    dS = 4.0 * LN3 / 4.0
    microstates = math.exp(dS)

    # 4. the evenly-spaced area spectrum reproduces S = A/4 at every level
    levels = [{"N": N, "area": 4 * LN3 * N, "entropy": LN3 * N,
               "S_equals_A_over_4": abs(LN3 * N - (4 * LN3 * N) / 4.0) < 1e-12}
              for N in (1, 2, 5, 100)]
    bekenstein_ok = all(l["S_equals_A_over_4"] for l in levels)

    # 5. Barbero-Immirzi: Dreyer's ln3/(2 pi sqrt2) vs the standard entropy-counting value
    gamma_dreyer = barbero_immirzi_dreyer()
    tension_ratio = GAMMA_STANDARD_LQG / gamma_dreyer

    checks = {
        "asymptotic_qnm_real_is_ln3_over_8pi": abs(w_inf - 0.04371) < 1e-4,
        "area_quantum_universal_4ln3": area_universal,
        "entropy_quantum_is_ln3": abs(dS - LN3) < 1e-12,
        "exactly_three_microstates": abs(microstates - 3.0) < 1e-9,
        "discrete_spectrum_reproduces_S_equals_A_over_4": bekenstein_ok,
        "barbero_immirzi_tension_present": tension_ratio > 1.5,
    }

    return {
        "version": VERSION,
        "method": ("Hod/Motl-Neitzke asymptotic QNM Re(omega)=ln3/(8 pi M); Bohr correspondence -> "
                   "area quantum dA=32 pi M dM=4 ln3; entropy quantum dS=ln3 -> 3 states; Dreyer "
                   "Barbero-Immirzi gamma=ln3/(2 pi sqrt2) vs standard ~0.2375"),
        "asymptotic_qnm_real_M1": w_inf,
        "famous_numerical_value": 0.04371,
        "area_quantum_scan": dA,
        "area_quantum_value": 4.0 * LN3,
        "entropy_quantum": dS,
        "microstates_per_quantum": microstates,
        "area_spectrum_levels": levels,
        "barbero_immirzi_dreyer": gamma_dreyer,
        "barbero_immirzi_standard_lqg": GAMMA_STANDARD_LQG,
        "tension_ratio": tension_ratio,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The highly-damped ringdown frequency ties black-hole spectroscopy to quantum geometry. "
            f"The asymptotic QNM real part Re(omega_inf) = ln3/(8 pi M) = {w_inf:.5f} (M=1) reproduces "
            "the famous 0.0437 numerical value (Hod/Motl-Neitzke). Read via Bohr's correspondence as a "
            "mass-transition quantum, it makes the horizon area change by dA = 32 pi M dM = 4 ln 3 -- "
            "and the mass M CANCELS (verified across M=0.5..10), so the area quantum is UNIVERSAL. The "
            "evenly-spaced area spectrum A_N = 4 ln3 N gives an entropy quantum dS = ln3, exactly 3 "
            "microstates per quantum (verified e^{dS}=3), and reproduces Bekenstein-Hawking S = A/4 at "
            "every level -- a discrete statistical-mechanical origin for the entropy the v2.257/v2.258 "
            "thread treated as continuous. Matched to the loop-quantum-gravity area spectrum with the "
            f"lowest spin j=1 (Dreyer), it fixes the Barbero-Immirzi parameter gamma = {gamma_dreyer:.4f} "
            f"-- but the standard LQG entropy-counting value is gamma ~ {GAMMA_STANDARD_LQG} (j=1/2 "
            f"dominance), a factor {tension_ratio:.2f} larger. That disagreement is a real, famous, "
            "unresolved tension between the QNM/Bohr area-quantization picture and microscopic LQG "
            "state counting -- the kind of honest gap that marks where quantum gravity is genuinely "
            "open, not a solved consistency check."
        ),
        "honest_scope": (
            "The asymptotic value Re(omega_inf) = ln3/(8 pi M) is the SOURCE-BACKED Hod/Motl-Neitzke "
            "result, used here as input: the repo's WKB QNM solver (v2.210) is a LOW-overtone "
            "approximation and cannot reach the n -> infinity regime, so this cycle does NOT re-derive "
            "ln3 numerically -- it derives the area/entropy/Barbero-Immirzi CONSEQUENCES of that "
            "established input, which are exact arithmetic. The Bohr-correspondence area-quantization "
            "interpretation (Hod) is a CONJECTURE, not a theorem; whether the relevant frequency is the "
            "real part (Hod) or |omega| (others) and whether the j=1 (Dreyer) or j=1/2 (standard) LQG "
            "assignment is correct are exactly the debated points -- the ~2x Barbero-Immirzi tension is "
            "reported, not resolved. A QG-structure result connecting validated repo threads (QNM, "
            "entropy) to LQG, not an engine constraint refit."
        ),
        "references": [
            "Hod, 'Bohr's correspondence principle and the area spectrum of quantum black holes', PRL 81 (1998) 4293",
            "Motl, 'An analytical computation of asymptotic Schwarzschild QNM frequencies', Adv. Theor. Math. Phys. 6 (2003) 1135",
            "Dreyer, 'Quasinormal modes, the area spectrum, and black hole entropy', PRL 90 (2003) 081301",
            "Meissner, 'Black hole entropy in loop quantum gravity', Class. Quantum Grav. 21 (2004) 5245",
            "this repo: v2.210 (WKB QNM solver), v2.257/v2.258 (BH entropy / holographic bound)",
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
    print("QNM asymptotics -> area quantization -> Barbero-Immirzi")
    print(f"  Re(omega_inf) (M=1) = {res['asymptotic_qnm_real_M1']:.5f}  (famous value {res['famous_numerical_value']})")
    print(f"  area quantum = 4 ln3 = {res['area_quantum_value']:.5f} (M-independent across M=0.5..10)")
    print(f"  entropy quantum = ln3 = {res['entropy_quantum']:.5f} -> {res['microstates_per_quantum']:.4f} microstates")
    print(f"  Barbero-Immirzi: Dreyer gamma = {res['barbero_immirzi_dreyer']:.4f}  vs  standard {res['barbero_immirzi_standard_lqg']} "
          f"(tension x{res['tension_ratio']:.2f})")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
