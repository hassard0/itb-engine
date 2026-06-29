"""v2.241 - The eikonal Kerr ringdown damping from the photon-orbit Lyapunov exponent.

Completes the Kerr eikonal QNM begun in v2.240 (frequency). The imaginary part (damping) of an
eikonal Kerr mode is set by the Lyapunov instability rate lambda of the same equatorial photon
orbit: omega_lmn ~ (l+1/2) Omega_ph(a) - i (n+1/2) lambda(a). The damping comes from how fast nearby
null rays peel away from the unstable circular orbit.

Equatorial Kerr null geodesics (Boyer-Lindquist, M=1, E=1): rdot^2 = 1 - V(r),
    V(r) = (b^2 - a^2)/r^2 - 2(b - a)^2/r^3 ,
with b = L/E the impact parameter. The circular photon orbit sits at the maximum of V (V'=0, V=1);
solving V'=0 gives the closed form b_c = a(r_ph + 3)/(3 - r_ph) (-> +/- 3 sqrt3 as a -> 0). A radial
perturbation grows as exp(omega_lambda * affine), omega_lambda = sqrt(-V''(r_ph)/2); converting to
coordinate time with tdot gives

    lambda = sqrt(-V''(r_ph)/2) / tdot ,   tdot = [ -a(a-b) + (r^2+a^2)(r^2+a^2-ab)/Delta ] / r^2 .

Validated against Schwarzschild (a=0 -> lambda = Omega_c = 1/(3 sqrt3), the v2.229 result). The
physics: the PROGRADE damping FALLS toward extremal (lambda -> 0, the "zero-damping" near-extremal
modes), so the ringdown QUALITY FACTOR Q ~ omega_R/(2 omega_I) RISES sharply -- near-extremal black
holes ring for many more cycles, the basis for near-extremal ringdown spectroscopy.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_kerr_eikonal_ringdown import omega_ph
from experiments.qnm_kerr_strong_field import photon_radius

VERSION = "v2.241"
DEFAULT_OUT = Path("experiments/results/v2.241/qnm_kerr_eikonal_damping.json")
SPINS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.998]


def b_critical(a: float, prograde: bool) -> tuple[float, float]:
    r = photon_radius(a, prograde)
    if a == 0.0:
        return r, (1.0 if prograde else -1.0) * 3 * math.sqrt(3)
    return r, a * (r + 3) / (3 - r)


def _Vpp(r: float, b: float, a: float) -> float:
    return 6 * (b**2 - a**2) / r**4 - 24 * (b - a)**2 / r**5


def _tdot(r: float, b: float, a: float) -> float:
    D = r**2 - 2 * r + a**2
    return (-a * (a - b) + (r**2 + a**2) * (r**2 + a**2 - a * b) / D) / r**2


def lyapunov(a: float, prograde: bool = True) -> float:
    r, b = b_critical(a, prograde)
    return math.sqrt(-_Vpp(r, b, a) / 2) / _tdot(r, b, a)


def run() -> dict:
    rows = []
    for a in SPINS:
        lp, lr = lyapunov(a, True), lyapunov(a, False)
        op = omega_ph(a, True)
        rows.append({"a": a, "lambda_prograde": lp, "lambda_retrograde": lr,
                     "Omega_ph_prograde": op, "quality_factor_prograde": op / (2 * lp)})
    a0 = rows[0]
    gate_ok = abs(a0["lambda_prograde"] - 1 / (3 * math.sqrt(3))) < 1e-9
    lp = [r["lambda_prograde"] for r in rows]
    Qp = [r["quality_factor_prograde"] for r in rows]
    lambda_falls = all(lp[i + 1] < lp[i] for i in range(len(lp) - 1))
    Q_rises = all(Qp[i + 1] > Qp[i] for i in range(len(Qp) - 1))
    return {
        "version": VERSION,
        "method": ("eikonal Kerr QNM damping from the equatorial photon-orbit Lyapunov exponent "
                   "lambda = sqrt(-V''(r_ph)/2)/tdot; b_c = a(r_ph+3)/(3-r_ph); M=1, E=1; "
                   "validated vs Schwarzschild (v2.229)"),
        "schwarzschild_gate_ok": bool(gate_ok),
        "spin_sequence": rows,
        "prograde_damping_falls_with_spin": bool(lambda_falls),
        "quality_factor_rises_with_spin": bool(Q_rises),
        "finding": (
            "The eikonal Kerr ringdown damping is the photon-orbit Lyapunov rate, reproducing "
            f"Schwarzschild at a=0 (lambda = {a0['lambda_prograde']:.5f} = Omega_c = 1/(3 sqrt3), the "
            "v2.229 identity). With spin the PROGRADE damping FALLS monotonically -- from 0.192 to "
            f"{rows[-1]['lambda_prograde']:.4f} at a=0.998 (heading to the extremal zero-damping "
            "limit lambda -> 0) -- while the retrograde damping stays ~0.186. So the prograde "
            "ringdown QUALITY FACTOR Q ~ omega_R/(2 omega_I) RISES sharply, from "
            f"{a0['quality_factor_prograde']:.2f} (Schwarzschild) to {rows[-1]['quality_factor_prograde']:.1f} "
            "at a=0.998: near-extremal black holes ring for many more cycles, the long-lived "
            "'zero-damping modes' that make near-extremal remnants the prime targets for ringdown "
            "spectroscopy. Combined with v2.240 (frequency) this gives the full eikonal Kerr QNM "
            "omega_lmn(a) = (l+1/2) Omega_ph - i(n+1/2) lambda from the photon orbit alone."
        ),
        "honest_scope": (
            "Eikonal (large-l), equatorial co-rotating (l=m) modes, exact Kerr photon orbits, "
            "validated against the Schwarzschild Lyapunov identity. Like v2.240 the eikonal is the "
            "large-l LIMIT and SPIN TREND, not a precise omega_220(a) (the precise low-l Kerr QNM, "
            "including the actual near-extremal zero-damping modes, needs the Teukolsky/Leaver "
            "solver -- the deferred effort; the eikonal captures the lambda -> 0 trend correctly). "
            "The a=1 extremal point has the photon orbit coincide with the horizon (coordinate "
            "degeneracy); astrophysical spins cap near Thorne a=0.998 (included). Parity-odd "
            "g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Yang, Zimmerman, Zhang, Berti, Chen, PRD 86 (2012) 104006 -- eikonal Kerr QNM / Lyapunov",
            "Cardoso et al., PRD 79 (2009) 064016 -- photon-orbit Lyapunov exponent",
            "this repo: v2.240 (eikonal Kerr frequency), v2.229 (Schwarzschild Lyapunov = Omega_c)",
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
    print(" a       lambda(pro/retro)     Q_prograde")
    for r in res["spin_sequence"]:
        print(f" {r['a']:.3f}   {r['lambda_prograde']:.5f}/{r['lambda_retrograde']:.5f}     "
              f"{r['quality_factor_prograde']:.3f}")
    print(f"gate OK={res['schwarzschild_gate_ok']}; prograde damping falls={res['prograde_damping_falls_with_spin']}; "
          f"Q rises={res['quality_factor_rises_with_spin']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
