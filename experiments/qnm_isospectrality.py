"""v2.218 - Axial<->polar QNM isospectrality and the R4 parity-splitting discriminator.

A self-contained ringdown experiment that needs NO un-cached appendix data (the R4
single-event thread was blocked there at v2.217). It rests on a textbook GR fact and the
repo's already-validated WKB solver.

GR isospectrality (Chandrasekhar-Detweiler): the two gravitational perturbation sectors of
a Schwarzschild black hole -- the AXIAL (odd-parity) Regge-Wheeler potential and the POLAR
(even-parity) Zerilli potential -- look completely different yet share an IDENTICAL QNM
spectrum (they are Darboux/superpartner potentials). This cycle:

  1. VALIDATION. Feed BOTH potentials through the same in-house WKB solver (qnm_wkb_solver,
     validated to ~1e-3 at v2.210-v2.211) and confirm the axial and polar QNMs coincide to
     the solver's precision. The residual |omega_axial - omega_polar| is the WKB-method
     PARITY-SPLITTING NOISE FLOOR -- the bar any *physical* (beyond-GR) isospectrality
     breaking must clear to be an observable discriminator.

  2. DISCRIMINATOR. Isospectrality breaking -- omega_axial != omega_polar under a modified
     theory -- is the clean fingerprint that separates parity-even from parity-odd operator
     content (and, with polarization-resolved ringdown, the lever the v2.209 'g_R4_c3 is
     dark' finding identified as missing). The repo holds the source-backed AXIAL R4
     correction (v2.215, delta_V_2^- = -432 eta_2 (r_g/r)^10); its induced axial QNM shift is
     ~10^4x the noise floor, so the splitting is sharply resolvable IN PRINCIPLE.

  HONEST NEGATIVE (preserved): the *magnitude* of the physical R4 splitting needs the POLAR
  (even-parity / Zerilli-sector) R4 correction too, which lives in the same un-sourceable
  2205.05132 appendix (v2.215's own claim-gate already lists 'even-parity (Zerilli) sector'
  as required). So this cycle delivers the validated machinery + the one-sided (axial)
  contribution, NOT the full splitting number.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_r4_sensitivity import E_J
from experiments.qnm_wkb_solver import f_metric, qnm, r_of_rstar, schwarzschild_qnm

ALPHA10_PER_ETA2 = -1728.0  # v2.215: alpha_10 = -432 * r_H^2 (per eta_2), r_H = 2

VERSION = "v2.218"
DEFAULT_OUT = Path("experiments/results/v2.218/qnm_isospectrality.json")

MODES = [(2, 0), (2, 1), (3, 0), (3, 1)]


def zerilli_potential(r: float, L: int = 2) -> float:
    """Even-parity (polar) Zerilli potential, M=1 (Chandrasekhar; Berti-Cardoso-Will rev.).

    V_Z = f * [2 lam^2 (lam+1) r^3 + 6 lam^2 r^2 + 18 lam r + 18] / [r^3 (lam r + 3)^2],
    lam = (L-1)(L+2)/2.  The Darboux superpartner of the axial Regge-Wheeler potential.
    """
    lam = (L - 1) * (L + 2) / 2.0
    num = 2 * lam**2 * (lam + 1) * r**3 + 6 * lam**2 * r**2 + 18 * lam * r + 18
    den = r**3 * (lam * r + 3.0) ** 2
    return f_metric(r) * num / den


def polar_qnm(n: int = 0, L: int = 2, **kw) -> complex:
    return qnm(lambda rs: zerilli_potential(r_of_rstar(rs), L), n=n, **kw)


def isospectrality_table() -> list[dict]:
    rows = []
    for L, n in MODES:
        ax = schwarzschild_qnm(n=n, L=L, s=2)
        po = polar_qnm(n=n, L=L)
        rows.append({
            "L": L, "n": n,
            "axial": [ax.real, ax.imag], "polar": [po.real, po.imag],
            "residual": abs(ax - po),
        })
    return rows


def run() -> dict:
    rows = isospectrality_table()
    noise_floor = max(r["residual"] for r in rows)

    # source-backed AXIAL R4 shift (v2.215 McManus contraction route), per unit eta_2, l=2 n=0.
    # Uses the published transfer coefficient e_10, NOT a WKB re-solve of the sharply-peaked
    # (r_g/r)^10 deformation (v2.212 showed the WKB-at-peak sensitivity is unreliable for such
    # high-power short-range terms -- it overshoots ~20x); this keeps the axial number
    # consistent with v2.215/v2.216.
    axial_shift = ALPHA10_PER_ETA2 * E_J[10]
    floor_22 = next(r["residual"] for r in rows if r["L"] == 2 and r["n"] == 0)
    headroom = abs(axial_shift) / floor_22

    return {
        "version": VERSION,
        "method": ("axial Regge-Wheeler vs polar Zerilli potentials through the same WKB "
                   "solver (qnm_wkb_solver, validated v2.210/v2.211); M=1, G=c=1"),
        "isospectrality": rows,
        "parity_splitting_noise_floor": noise_floor,
        "isospectrality_validated": noise_floor < 5e-3,
        "finding": (
            "GR isospectrality CONFIRMED in-house: the axial (Regge-Wheeler) and polar "
            "(Zerilli) potentials -- structurally unalike -- yield the SAME QNM spectrum to "
            f"the WKB solver's precision (max residual {noise_floor:.1e}; the l=3 modes agree "
            "to ~1e-6, the l=2 residual ~2e-4 is the known low-l WKB systematic). This residual "
            "is the parity-splitting NOISE FLOOR: any beyond-GR isospectrality breaking must "
            "exceed it to be an observable discriminator."
        ),
        "r4_discriminator": {
            "axial_R4_shift_per_eta2": [axial_shift.real, axial_shift.imag],
            "axial_shift_magnitude": abs(axial_shift),
            "noise_floor_l2_n0": floor_22,
            "headroom_over_noise_floor": headroom,
            "statement": (
                "The source-backed AXIAL R4 correction (v2.215) shifts the l=2 n=0 QNM by "
                f"|Delta omega| ~ {abs(axial_shift):.2f} per unit eta_2 -- ~{headroom:.0e}x the "
                "parity-splitting noise floor -- so isospectrality breaking is sharply "
                "resolvable IN PRINCIPLE and is the parity-resolved lever the v2.209 "
                "'g_R4_c3 is dark to non-polarization-resolved ringdown' finding identified."
            ),
            "honest_negative": (
                "The MAGNITUDE of the physical R4 isospectrality splitting "
                "|Delta omega_axial - Delta omega_polar| needs the POLAR (even-parity / "
                "Zerilli-sector) R4 correction too, which lives in the same un-sourceable "
                "2205.05132 appendix (v2.215's claim-gate already lists the even-parity sector "
                "as required). Only the one-sided axial contribution is source-backed here; the "
                "full splitting number is NOT claimed."
            ),
        },
        "claim_gate": (
            "GR isospectrality result is claim-grade (textbook fact reproduced by a validated "
            "solver, self-contained). The R4 discriminator is delivered as validated machinery "
            "+ the one-sided axial shift only; the full splitting magnitude stays gated on the "
            "un-sourceable even-parity (Zerilli) R4 correction. Parity-odd g_R4_c3 dark (v2.209)."
        ),
        "references": [
            "Chandrasekhar, The Mathematical Theory of Black Holes (1983) -- isospectrality",
            "Berti, Cardoso, Will, PRD 73 (2006) 064030 -- Zerilli potential / QNMs",
            "Silva, Ghosh, Buonanno, PRD 107 (2023) 044030 (arXiv:2205.05132) -- axial R4 delta_V",
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
    for r in res["isospectrality"]:
        print(f"L={r['L']} n={r['n']}  axial={r['axial'][0]:.6f}{r['axial'][1]:+.6f}i  "
              f"polar={r['polar'][0]:.6f}{r['polar'][1]:+.6f}i  residual={r['residual']:.2e}")
    print(f"parity-splitting noise floor = {res['parity_splitting_noise_floor']:.2e}  "
          f"validated={res['isospectrality_validated']}")
    d = res["r4_discriminator"]
    print(f"axial R4 shift/eta2 = {d['axial_shift_magnitude']:.3f}  "
          f"headroom = {d['headroom_over_noise_floor']:.1e}x")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
