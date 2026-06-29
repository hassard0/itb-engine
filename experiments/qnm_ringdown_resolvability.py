"""v2.219 - First-principles ringdown resolvability: turning a QNM deviation into a detector SNR.

v2.218 quantified the parity-splitting noise floor and showed the source-backed axial R4 QNM
shift sits far above it. The natural next question is OBSERVABILITY: at what gravitational-wave
ringdown signal-to-noise ratio (SNR) does a fractional QNM deviation become measurable? This
cycle answers it from first principles, fully self-contained -- no un-cached appendix, no
external Fisher coefficients to manufacture.

A single ringdown mode is a damped sinusoid h(t) = A e^{-t/tau} cos(omega t + phi), t >= 0,
with omega = omega_R, tau = 1/|omega_I|, quality factor Q = omega_R tau / 2 = omega_R/(2|omega_I|).
The Fisher matrix over {ln A, phi, omega, tau} (marginalizing amplitude and phase as nuisance
parameters) is computed by direct integration of the analytic waveform partials under a white-
noise inner product (a|b) = integral_0^inf a b dt. Two exact, derivable properties:

  1. sigma_theta ~ 1/rho  (the standard Fisher 1/SNR scaling -- exact here by construction).
  2. The dimensionless products R_f = rho sigma_f/f and R_tau = rho sigma_tau/tau are
     SCALE-INVARIANT, hence pure functions of Q alone (rescaling time t->t/a maps
     (omega, 1/tau) -> (a omega, a/tau) with Q fixed). Validated numerically below.

So R_f(Q), R_tau(Q) are universal ringdown-resolvability coefficients, and the critical SNR to
resolve a fractional QNM deviation delta at N sigma is rho_crit = N * R_f / delta.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from experiments.qnm_r4_sensitivity import E_J

VERSION = "v2.219"
DEFAULT_OUT = Path("experiments/results/v2.219/qnm_ringdown_resolvability.json")

# l=2 n=0 Schwarzschild gravitational QNM (M=1; Berti-Cardoso-Will)
OMEGA_R, OMEGA_I = 0.373672, 0.088962
ALPHA10_PER_ETA2 = -1728.0  # v2.215 axial R4: d(omega)/d(eta_2) = -1728 e_10


def ringdown_fisher(wR: float, wI: float, t_factor: float = 40.0,
                    npts: int = 400001) -> dict:
    """Fisher-matrix resolvability of a single damped-sinusoid ringdown mode (white noise)."""
    tau = 1.0 / wI
    Q = wR * tau / 2.0
    t = np.linspace(0.0, t_factor * tau, npts)
    e = np.exp(-t / tau)
    c, s = np.cos(wR * t), np.sin(wR * t)        # phi = 0 WLOG
    h = e * c
    partials = [h,                                # d/d ln A
                -e * s,                           # d/d phi
                -t * e * s,                       # d/d omega
                (t / tau**2) * e * c]             # d/d tau
    G = np.array([[np.trapezoid(pi * pj, t) for pj in partials] for pi in partials])
    rho1 = float(np.sqrt(np.trapezoid(h * h, t)))
    C = np.linalg.inv(G)
    R_f = rho1 * float(np.sqrt(C[2, 2])) / wR
    R_tau = rho1 * float(np.sqrt(C[3, 3])) / tau
    return {"Q": Q, "R_f": R_f, "R_tau": R_tau}


def critical_snr(delta: float, R_f: float, n_sigma: float = 5.0) -> float:
    """SNR needed to resolve a fractional frequency deviation delta at n_sigma."""
    return n_sigma * R_f / delta


def run() -> dict:
    base = ringdown_fisher(OMEGA_R, OMEGA_I)
    # internal validation: R_f, R_tau depend ONLY on Q (scale-invariance) -> rescale by 2x
    scaled = ringdown_fisher(2 * OMEGA_R, 2 * OMEGA_I)
    q_invariant = (abs(scaled["R_f"] - base["R_f"]) < 1e-3
                   and abs(scaled["R_tau"] - base["R_tau"]) < 1e-3)

    R_f = base["R_f"]
    rho_crit = {f"{d}": critical_snr(d, R_f, 5.0) for d in (0.01, 0.05, 0.10)}

    # application: source-backed axial R4 fractional frequency shift per eta_2 (v2.215)
    axial_shift = ALPHA10_PER_ETA2 * E_J[10]               # = -3.184 - 5.637 i
    delta_f_per_eta2 = abs(axial_shift.real) / OMEGA_R     # |Delta omega_R| / omega_R per eta_2
    # eta_2 reach at a given ringdown SNR: resolvable (5 sigma) when 5 R_f/(delta_f_per_eta2 eta_2) < rho
    eta2_reach = {f"rho={rho}": 5.0 * R_f / (delta_f_per_eta2 * rho) for rho in (8, 30, 100)}

    return {
        "version": VERSION,
        "method": ("analytic damped-sinusoid Fisher matrix over {lnA, phi, omega, tau}, white-"
                   "noise inner product int_0^inf a b dt, ringdown starts at t=0; M=1 units"),
        "mode": "l=2 n=0 Schwarzschild gravitational",
        "resolvability_coefficients": {
            "Q": base["Q"],
            "R_f_rho_sigma_f_over_f": R_f,
            "R_tau_rho_sigma_tau_over_tau": base["R_tau"],
        },
        "Q_scale_invariance_validated": bool(q_invariant),
        "critical_snr_5sigma": rho_crit,
        "finding": (
            f"For the l=2 n=0 ringdown (Q = {base['Q']:.2f}) the universal resolvability "
            f"coefficients are rho*sigma_f/f = {R_f:.3f} and rho*sigma_tau/tau = "
            f"{base['R_tau']:.2f} (both O(1), consistent with the published Berti-Cardoso-Will "
            "ringdown Fisher analysis). A fractional QNM frequency deviation delta is resolvable "
            f"at 5 sigma when rho > {5*R_f:.2f}/delta -- e.g. delta = 1% needs rho ~ "
            f"{rho_crit['0.01']:.0f}, delta = 10% needs rho ~ {rho_crit['0.1']:.0f}."
        ),
        "r4_isospectrality_application": {
            "axial_R4_delta_f_per_eta2": delta_f_per_eta2,
            "eta2_reach_5sigma": eta2_reach,
            "statement": (
                "The source-backed axial R4 shift (v2.215) gives a fractional frequency deviation "
                f"|Delta omega_R|/omega_R = {delta_f_per_eta2:.2f} per unit eta_2. A ringdown of "
                f"SNR rho thus resolves the R4-induced shift (5 sigma) for eta_2 > {5*R_f/delta_f_per_eta2:.3f}/rho: "
                f"a current single-event SNR ~8 reaches eta_2 ~ {eta2_reach['rho=8']:.3f} (at the "
                "edge of the linear/perturbative regime), while a high-SNR ~100 event (3G/LISA-era) "
                f"reaches eta_2 ~ {eta2_reach['rho=100']:.4f}, comfortably perturbative -- so "
                "isospectrality-resolved R4 ringdown bounds sharpen by ~an order of magnitude with "
                "next-generation SNR."
            ),
        },
        "honest_scope": (
            "Idealized estimate: SINGLE mode, WHITE noise, ringdown-starts-at-t=0 step (some "
            "spectral leakage), no detector PSD coloring, no overtone/mode mixing. R_f(Q) is "
            "therefore an O(1) order-of-magnitude resolvability coefficient (consistent with the "
            "published BCW analysis), NOT a detector-specific forecast. The eta_2 reach also "
            "carries the v2.215 eta_2 normalization caveat (the (r_g/r)^10 prefactor convention) "
            "and the axial-only limitation (the full isospectrality splitting needs the un-"
            "sourceable polar correction, v2.218). Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Berti, Cardoso, Will, PRD 73 (2006) 064030 -- ringdown Fisher analysis / sigma_f, sigma_Q",
            "Echeverria, PRD 40 (1989) 3194 -- ringdown frequency resolvability",
            "Silva, Ghosh, Buonanno, PRD 107 (2023) 044030 -- axial R4 delta_V (v2.215)",
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
    rc = res["resolvability_coefficients"]
    print(f"Q={rc['Q']:.3f}  rho*sigma_f/f={rc['R_f_rho_sigma_f_over_f']:.4f}  "
          f"rho*sigma_tau/tau={rc['R_tau_rho_sigma_tau_over_tau']:.4f}")
    print(f"Q-scale-invariance validated = {res['Q_scale_invariance_validated']}")
    print(f"critical SNR (5 sigma): {res['critical_snr_5sigma']}")
    a = res["r4_isospectrality_application"]
    print(f"axial R4 df/f per eta2 = {a['axial_R4_delta_f_per_eta2']:.3f}  "
          f"eta2 reach = {a['eta2_reach_5sigma']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
