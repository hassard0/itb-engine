"""v2.04 - The minimal falsifier: the single cheapest measurement that would confirm or
kill the data-driven EFT.

For the data-driven EFT (discovered_data_driven), each falsifiable observable has a
prediction, a NULL/alternative (parity-even beta=0, KSS eta/s, Lloyd-saturated dC/dt,
unscreened sub-mm, r=0), and a projected experimental precision + milestone year (the
v1.92 roadmap). The FALSIFICATION POWER = |prediction - null| / sigma_projected (how many
sigma the measurement would separate the EFT from the null). We rank by power and by year
to find the MINIMAL FALSIFIER: the earliest measurement reaching >=5 sigma.

HONEST: projected sigmas are roadmap estimates; the headline beta=0.32 vs 0 rests on the
birefringence map + a ~3.6 sigma hint. Robust content is the RANKING of which measurement
discriminates first/most -- and the finding that the EFT's falsifiability is concentrated
in ONE observable.

Run on Vulcan:  python experiments/minimal_falsifier.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")
from itb.predict import predict

KILL = 5.0   # sigma separation that decisively confirms-or-kills


def main():
    p = predict("discovered_data_driven")
    o = p["observables"]
    gpar = p["coefficients"]["g_R2_parity"]
    beta = 3.4 * gpar                     # cosmic birefringence prediction (deg)
    dCdt = o["holographic_complexity_rate_lloyd_units"]
    eta_s = o["holographic_eta_over_s_KSS_units"]
    ns_r = o.get("starobinsky_inflation_ns_r_N55") or [0.964, 0.004]

    # (observable, prediction, null/alternative, projected sigma, year, experiment, kind)
    obs = [
        {"obs": "CMB birefringence beta (deg)", "pred": beta, "null": 0.0,
         "sigma": 0.03, "year": 2030, "exp": "LiteBIRD / CMB-S4", "kind": "EXPERIMENT"},
        {"obs": "inflation tensor-to-scalar r", "pred": ns_r[1], "null": 0.0,
         "sigma": 0.001, "year": 2030, "exp": "CMB-S4 / Simons", "kind": "EXPERIMENT"},
        {"obs": "sub-mm screening (force @ ~115um)", "pred": 0.0, "null": 1.0,
         "sigma": 0.35, "year": 2028, "exp": "next-gen sub-mm", "kind": "EXPERIMENT"},
        {"obs": "PTA chiral SGWB Pi_V (%)", "pred": 2.0, "null": 0.0,
         "sigma": 1.2, "year": 2032, "exp": "SKA-PTA", "kind": "EXPERIMENT"},
        {"obs": "GW birefringence |g_R2_parity|", "pred": gpar, "null": 0.0,
         "sigma": 0.08, "year": 2035, "exp": "Einstein Telescope / CE", "kind": "EXPERIMENT"},
        # structural / no direct measurement (falsification power undefined experimentally)
        {"obs": "eta/s (KSS units)", "pred": eta_s, "null": 1.0, "sigma": None,
         "year": None, "exp": "holographic-dual statement", "kind": "STRUCTURAL"},
        {"obs": "holographic dC/dt (Lloyd units)", "pred": dCdt, "null": 1.0, "sigma": None,
         "year": None, "exp": "Complexity=Action statement", "kind": "STRUCTURAL"},
        {"obs": "BH extremal entropy Delta S_ext", "pred": o["bh_entropy_shift_delta_S_ext"],
         "null": 0.0, "sigma": None, "year": None, "exp": "WGC / BH thermodynamics",
         "kind": "STRUCTURAL"},
    ]
    for r in obs:
        if r["sigma"]:
            r["falsification_power_sigma"] = round(abs(r["pred"] - r["null"]) / r["sigma"], 2)
        else:
            r["falsification_power_sigma"] = None

    exp = [r for r in obs if r["kind"] == "EXPERIMENT"]
    exp_sorted = sorted(exp, key=lambda r: -r["falsification_power_sigma"])
    # minimal falsifier: earliest measurement reaching >= KILL sigma
    reaching = sorted([r for r in exp if r["falsification_power_sigma"] >= KILL],
                      key=lambda r: r["year"])
    minimal_falsifier = reaching[0] if reaching else None
    top_power = exp_sorted[0]

    # ---- figure: power vs year ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    for r in exp:
        col = "#d62728" if r["falsification_power_sigma"] >= KILL else "#1f77b4"
        ax1.scatter(r["year"], r["falsification_power_sigma"], s=120, color=col, zorder=5)
        ax1.annotate(f"{r['obs'].split('(')[0][:18]}\n({r['exp']})",
                     (r["year"], r["falsification_power_sigma"]), fontsize=6.5,
                     textcoords="offset points", xytext=(5, 3))
    ax1.axhline(KILL, color="black", ls="--", lw=1.5, label=f"{KILL} sigma kill line")
    if minimal_falsifier:
        ax1.scatter([minimal_falsifier["year"]], [minimal_falsifier["falsification_power_sigma"]],
                    s=320, facecolors="none", edgecolors="#d62728", linewidths=2.5, zorder=6)
    ax1.set_xlabel("milestone year"); ax1.set_ylabel("falsification power (sigma separation)")
    ax1.set_yscale("log"); ax1.legend(fontsize=8)
    ax1.set_title("falsification power vs availability (circled = minimal falsifier)", fontsize=9)
    ax2.barh([r["obs"][:24] for r in exp_sorted][::-1],
             [r["falsification_power_sigma"] for r in exp_sorted][::-1],
             color=["#d62728" if r["falsification_power_sigma"] >= KILL else "#1f77b4"
                    for r in exp_sorted][::-1])
    ax2.axvline(KILL, color="black", ls="--", lw=1.2)
    ax2.set_xlabel("falsification power (sigma)"); ax2.set_xscale("log")
    ax2.set_title("sigma-separation per observable (red >= 5 sigma)", fontsize=9)
    fig.suptitle("v2.04  The minimal falsifier of the data-driven EFT", fontsize=12)
    fig.tight_layout()
    png = "/tmp/minimal_falsifier.png"
    fig.savefig(png, dpi=140)

    summary = {
        "minimal_falsifier": (f"{minimal_falsifier['exp']} ({minimal_falsifier['obs']}) "
                              f"in {minimal_falsifier['year']} at "
                              f"{minimal_falsifier['falsification_power_sigma']} sigma"
                              if minimal_falsifier else "none reaches 5 sigma"),
        "highest_power_observable": f"{top_power['obs']} ({top_power['falsification_power_sigma']} sigma)",
        "most_dangerous_observation": "a tightened CMB birefringence consistent with beta=0 "
            "(LiteBIRD/CMB-S4, ~2030) would most strongly REFUTE the data-driven EFT -- its "
            "entire identity rests on beta=0.32 deg; a null there collapses it.",
        "concentration": "The EFT's experimental falsifiability is CONCENTRATED in cosmic "
            "birefringence (~10 sigma vs the next-best ~4 sigma): it is effectively a "
            "one-observable theory -- it lives or dies by the birefringence measurement.",
        "ranking": exp_sorted,
        "structural_only": [r["obs"] for r in obs if r["kind"] == "STRUCTURAL"],
        "honest": "projected sigmas are roadmap estimates; beta=0.32 vs 0 rests on the "
                  "birefringence map + a ~3.6 sigma HINT; robust content is the ranking + the "
                  "single-observable concentration.",
        "relates_to": ["v1.92 convergence forecast", "v2.01 Bayesian comparison",
                       "v1.78/79 birefringence + data-driven EFT"],
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
