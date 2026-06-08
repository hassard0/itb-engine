"""Can a non-minimal axion potential reach DESI's steep wa? (v1.50)

v1.49 found the minimal cosine axion sits on the thawing track (wa ~ -0.28),
shallower than DESI's central wa ~ -0.7. This re-solves the SAME quintessence EOM
for a family of potential shapes and asks which (if any) reach DESI's
(w0 ~ -0.83, wa ~ -0.7) while keeping Omega_phi = 0.69.

EOM (units 8 pi G = 1, H0 = 1), integrated in N = ln a, shooting the initial
field value so Omega_phi(a=1) = 0.69:
    phi'' + (3 + Hdot/H^2) phi' + V'/H^2 = 0.

Potentials (V0 and scale f set by the shoot / fixed):
  cosine     V0 [1 - cos(x)]            x = phi/f      (minimal, v1.49)
  hilltop4   V0 [1 - (x/pi)^4]          quartic hilltop (faster thaw)
  exp        V0 exp(-lam x)             exponential (scaling/thawing)
  inverse    V0 / (1 + x)^2             inverse-power (tracker-like)
"""

import json
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, ".")

RHO_M0 = 0.93
RHO_PHI_TARGET = 2.07
F = 1.58
A_I = 0.02


def make_potential(kind, m=1.3, lam=1.0):
    if kind == "cosine":
        V = lambda x: m*m*F*F*(1 - np.cos(x))
        dV = lambda x: m*m*F*np.sin(x)            # dV/dphi
        x_max = np.pi - 0.02
    elif kind == "hilltop4":
        # V0[1-(x/pi)^4]; V0 ~ m^2 f^2 scale
        V0 = m*m*F*F
        V = lambda x: V0*(1 - (x/np.pi)**4)
        dV = lambda x: V0*(-4*(x**3)/np.pi**4)/F  # d/dphi = (1/f) d/dx
        x_max = np.pi - 0.05
    elif kind == "exp":
        V0 = m*m*F*F
        V = lambda x: V0*np.exp(-lam*x)
        dV = lambda x: V0*(-lam)*np.exp(-lam*x)/F
        x_max = 3.0
    elif kind == "inverse":
        V0 = m*m*F*F
        V = lambda x: V0/(1+x)**2
        dV = lambda x: V0*(-2)/(1+x)**3/F
        x_max = 3.0
    return V, dV, x_max


def integrate(V, dV, x_i):
    phi_i = x_i * F

    def rhs(N, y):
        phi, pi = y
        a = np.exp(N)
        Vv = V(phi/F) if False else V(phi/F)   # V takes x=phi/F
        x = phi / F
        Vv = V(x)
        denom = 1.0 - pi*pi/6.0
        H2 = (RHO_M0/a**3 + Vv) / (3.0*denom)
        H2 = max(H2, 1e-30)
        rho_phi = 0.5*H2*pi*pi + Vv
        p_phi = 0.5*H2*pi*pi - Vv
        rho_tot = RHO_M0/a**3 + rho_phi
        HdotoverH2 = -1.5*(1 + p_phi/rho_tot)
        dpi = -(3.0+HdotoverH2)*pi - dV(x)/H2
        return [pi, dpi]

    Ns = np.linspace(np.log(A_I), 0.0, 400)
    sol = solve_ivp(rhs, [Ns[0], Ns[-1]], [phi_i, 0.0], t_eval=Ns,
                    rtol=1e-8, atol=1e-10)
    phi, pi = sol.y; a = np.exp(sol.t)
    x = phi/F; Vv = V(x)
    denom = 1.0 - pi*pi/6.0
    H2 = (RHO_M0/a**3 + Vv)/(3.0*denom)
    rho_phi = 0.5*H2*pi*pi + Vv
    w = (0.5*H2*pi*pi - Vv)/rho_phi
    return a, w, rho_phi


def shoot_and_fit(kind, m=1.3, lam=1.0):
    V, dV, x_max = make_potential(kind, m, lam)
    lo, hi = 0.02, x_max
    for _ in range(60):
        mid = 0.5*(lo+hi)
        a, w, rho_phi = integrate(V, dV, mid)
        # larger initial x -> more potential energy (for cosine/hilltop); handle exp/inverse (decreasing V)
        more = rho_phi[-1] < RHO_PHI_TARGET
        if kind in ("exp", "inverse"):
            # V decreases with x, so smaller x = more energy
            if more: hi = mid
            else: lo = mid
        else:
            if more: lo = mid
            else: hi = mid
    a, w, rho_phi = integrate(V, dV, mid)
    w0 = float(w[-1])
    mask = a >= 0.5
    A = np.vstack([np.ones(mask.sum()), (1-a[mask])]).T
    coef, *_ = np.linalg.lstsq(A, w[mask], rcond=None)
    wa = float(coef[1])
    return {"kind": kind, "x_i": float(mid), "w0": w0, "wa": wa,
            "Omega_phi": float(rho_phi[-1]/3.0)}


def main():
    DESI = {"w0": -0.83, "w0_err": 0.06, "wa": -0.7, "wa_err": 0.3}
    print("=== Non-minimal quintessence potentials vs DESI (w0=-0.83, wa=-0.7) ===\n")
    print(f"  {'potential':<12}{'w0':>8}{'wa':>8}{'Omega_phi':>11}  reaches DESI wa?")
    rows = []
    configs = [("cosine", 1.3, 1.0), ("hilltop4", 1.3, 1.0),
               ("exp", 1.3, 1.5), ("exp", 1.3, 3.0), ("inverse", 1.3, 1.0)]
    for kind, m, lam in configs:
        r = shoot_and_fit(kind, m, lam)
        label = kind + (f"(lam={lam})" if kind == "exp" else "")
        steep = abs(r["wa"] - DESI["wa"]) < 2*DESI["wa_err"]
        w0ok = abs(r["w0"] - DESI["w0"]) < 2*DESI["w0_err"]
        tag = "BOTH w0&wa" if (steep and w0ok) else ("wa ok" if steep else ("w0 ok" if w0ok else ""))
        rows.append({**r, "label": label, "desi_wa": steep, "desi_w0": w0ok})
        print(f"  {label:<12}{r['w0']:>8.3f}{r['wa']:>8.3f}{r['Omega_phi']:>11.3f}  {tag}")

    hits = [r for r in rows if r["desi_wa"] and r["desi_w0"]]
    print()
    if hits:
        print(f"  => {len(hits)} potential(s) reach DESI's (w0,wa) simultaneously: "
              f"{[h['label'] for h in hits]}")
        print(f"     Non-minimal axion dynamics CAN steepen wa to DESI while keeping w0 ~ -0.83.")
    else:
        print(f"  => none of the simple shapes hit DESI's steep wa=-0.7 at w0=-0.83 within 2sigma.")
        best = min(rows, key=lambda r: abs(r["wa"]-DESI["wa"]))
        print(f"     closest in wa: {best['label']} (wa={best['wa']:.3f}). DESI's steep wa")
        print(f"     remains hard for minimal single-field quintessence — a real tension that")
        print(f"     points to either non-trivial dynamics (coupled/multi-field) or evolving")
        print(f"     systematics in the DESI w0wa fit. The engine's GW-birefringence")
        print(f"     prediction is independent of this cosmological model-building.")

    with open("experiments/out_quintessence_potentials.json", "w") as f:
        json.dump({"DESI": DESI, "rows": rows}, f, indent=2)
    print("\nwrote experiments/out_quintessence_potentials.json")


if __name__ == "__main__":
    main()
