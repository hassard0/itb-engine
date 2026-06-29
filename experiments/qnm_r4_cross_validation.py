"""v2.216 - Cross-validate the engine's R4 odd-parity ringdown sensitivity (v2.215, McManus
route) against the repo's independently-extracted qEFT deformation coefficients (the qEFT /
ParSpec route from the SAME source, Silva-Ghosh-Buonanno arXiv:2205.05132).

Two routes to the SAME physical quantity -- the complex QNM shift of the l=2 n=0 fundamental
from the R4 (quartic) operator:

  McManus route (v2.215): delta_V_2^- = -432 eta_2 (r_g/r)^10  ->  alpha_10 = -1728 eta_2  ->
      d(omega)/d(eta_2) = -1728 * e_10 = -3.184 - 5.637 i   (M=1, absolute complex shift).

  qEFT/ParSpec route (repo extraction of 2205.05132): the fractional shifts of the real
      frequency and the damping time, omega_R = omega_R^0 (1 + gamma * dwq), tau = tau^0 (1 +
      gamma * dtq), with dwq = -0.2114, dtq = -0.6070 (n=0). With tau ~ -1/omega_I:
          d(omega_R)/d(gamma) = omega_R^0 * dwq
          d(omega_I)/d(gamma) = -omega_I^0 * dtq   (since Delta_tau/tau = -Delta_omega_I/omega_I)

Both gamma and eta_2 are REAL positive couplings, so the COMPLEX DIRECTION (the ratio
Im/Re of the shift, equivalently the damping-to-frequency shift ratio) is
CONVENTION-INDEPENDENT (the eta_2<->gamma and r_g normalizations only rescale the
magnitude). If the routes describe the same physics, the directions must coincide.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_r4_sensitivity import E_J  # McManus e_10 (M=1)

VERSION = "v2.216"
DEFAULT_OUT = Path("experiments/results/v2.216/qnm_r4_cross_validation.json")

OMEGA0 = complex(0.373672, -0.088962)        # l=2 n=0 GR (M=1)
# repo's qEFT/ParSpec deformation coefficients (2205.05132 extraction), n=0 fundamental
DWQ_0 = -0.2114                               # fractional REAL-frequency shift / gamma
DTQ_0 = -0.6070                               # fractional damping-TIME shift / gamma
ALPHA10_PER_ETA2 = -1728.0                    # v2.215


def mcmanus_shift_per_eta2() -> complex:
    return ALPHA10_PER_ETA2 * E_J[10]


def qeft_shift_per_gamma() -> complex:
    # ParSpec: omega = omega_R(1+gamma dwq) + i omega_I, tau ~ -1/omega_I, dtau = -d omega_I/omega_I
    d_omega_R = OMEGA0.real * DWQ_0
    d_omega_I = -OMEGA0.imag * DTQ_0
    return complex(d_omega_R, d_omega_I)


def run() -> dict:
    mc = mcmanus_shift_per_eta2()
    qe = qeft_shift_per_gamma()
    # convention-independent comparison: damping/frequency shift ratio = Im/Re
    ratio_mc = mc.imag / mc.real
    ratio_qe = qe.imag / qe.real
    import cmath
    phase_mc = cmath.phase(mc)
    phase_qe = cmath.phase(qe)
    phase_diff_deg = abs(phase_mc - phase_qe) * 180.0 / cmath.pi
    signs_agree = (mc.real < 0) == (qe.real < 0) and (mc.imag < 0) == (qe.imag < 0)
    ratio_rel_diff = abs(ratio_mc - ratio_qe) / abs(ratio_qe)
    return {
        "version": VERSION,
        "mcmanus_route_shift_per_eta2": [mc.real, mc.imag],
        "qeft_route_shift_per_gamma": [qe.real, qe.imag],
        "convention_independent_comparison": {
            "damping_over_frequency_ratio_mcmanus": ratio_mc,
            "damping_over_frequency_ratio_qeft": ratio_qe,
            "ratio_relative_difference": ratio_rel_diff,
            "complex_phase_difference_deg": phase_diff_deg,
        },
        "signs_agree": bool(signs_agree),
        "directions_agree_5pct": bool(ratio_rel_diff < 0.05),
        "finding": (
            "QUALITATIVE AGREEMENT, QUANTITATIVE DISAGREEMENT. Both source-backed routes agree "
            "on the SIGNS: the R4 quartic operator LOWERS the ringdown frequency (Delta omega_R "
            "< 0) AND increases the damping (Delta omega_I < 0). But the convention-INDEPENDENT "
            f"damping-to-frequency shift ratio differs by {100*ratio_rel_diff:.0f}% "
            f"(McManus {ratio_mc:.2f} vs qEFT {ratio_qe:.2f}; complex phase off by "
            f"{phase_diff_deg:.0f} deg). Since eta_2<->gamma and r_g only rescale the magnitude, "
            "this ratio mismatch is REAL and is NOT fixable by the v2.215 normalization caveats."
        ),
        "diagnosis": (
            "The single odd-parity (r_g/r)^10 term is most likely an INCOMPLETE representation "
            "of the qEFT modified potential: the full theory's QNM shift (the qEFT coefficients) "
            "carries contributions beyond the one leading axial power (additional radial terms, "
            "or the qEFT 'theory' combines more operator content than the single eta_2 monomial), "
            "so the McManus single-term contraction captures the right qualitative behavior but "
            "not the full complex shift. A ParSpec damping-time vs omega_I convention subtlety "
            "(not pinnable from the un-rendered 2205.05132 appendix) cannot be fully excluded. "
            "Per discipline: preserve the negative, do NOT tune to force agreement."
        ),
        "claim_gate": (
            "closed: the v2.215 single-term R4 sensitivity is QUALITATIVELY validated (correct "
            "signs, two independent routes) but NOT quantitatively (ratio off ~2.6x). The full "
            "claim needs the complete source-backed delta_V (all radial terms) from the "
            "2205.05132 appendix, the even-parity (Zerilli) sector, and the eta_2<->gamma map."
        ),
        "references": [
            "Silva, Ghosh, Buonanno, PRD 107 (2023) 044030 (arXiv:2205.05132)",
            "McManus et al., PRD 99 (2019) 104077",
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
    c = res["convention_independent_comparison"]
    print(f"McManus shift/eta2 = {res['mcmanus_route_shift_per_eta2']}")
    print(f"qEFT shift/gamma   = {res['qeft_route_shift_per_gamma']}")
    print(f"damping/freq ratio: McManus {c['damping_over_frequency_ratio_mcmanus']:.3f}  "
          f"qEFT {c['damping_over_frequency_ratio_qeft']:.3f}  "
          f"(rel.diff {c['ratio_relative_difference']:.2f}, phase {c['complex_phase_difference_deg']:.1f} deg)")
    print(f"signs_agree={res['signs_agree']}  directions_agree_5pct={res['directions_agree_5pct']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
