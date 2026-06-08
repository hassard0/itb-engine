"""Capstone figure: the multi-probe parity web (v1.57).

The engine's signature parity coupling g_R2_parity ~ 0.09 is probed by a web of
experiments spanning ~12 orders of magnitude in frequency (plus non-GW channels).
This consolidates them into one figure: GW-band probes vs frequency with their
sensitivity to g_R2_parity, the predicted value, and the non-frequency channels
annotated.
"""

import json
import sys

import numpy as np

sys.path.insert(0, ".")

G_PV = 0.092   # discovered parity-violating branch

# GW-band probes: (label, frequency Hz, sensitivity to g_R2_parity, status)
PROBES = [
    ("PTA chiral HD\n(SKA)", 1e-8, 0.05, "future"),
    ("LISA GW\nbirefringence", 1e-3, 0.03, "future"),
    ("LIGO O5 GW\nbirefringence", 1e2, 0.01, "near"),
    ("BH ringdown\n(NULL @ DE scale)", 2e2, 1.0, "null"),
]
# non-GW-frequency channels (annotated separately)
OTHER = [
    ("CMB EB birefringence (LiteBIRD/CMB-S4) - EM sibling axion", 0.011),
    ("anomaly-inflow ceiling (sets max parity ~0.14)", 0.14),
]


def main():
    print("=== The multi-probe parity web (capstone) ===\n")
    print(f"  predicted g_R2_parity ~ {G_PV}\n")
    print(f"  {'probe':<28}{'freq (Hz)':>12}{'sensitivity':>13}  status")
    for lab, f, s, st in PROBES:
        reach = "REACHES 0.09" if (s < G_PV and st != "null") else (
            "null (>>0.09)" if st == "null" else "marginal")
        print(f"  {lab.replace(chr(10),' '):<28}{f:>12.0e}{s:>13.3f}  {st} [{reach}]")
    print(f"\n  non-GW-frequency channels:")
    for lab, s in OTHER:
        print(f"    {lab}: ~{s}")

    out = {"g_R2_parity": G_PV, "probes": [
        {"label": l.replace("\n", " "), "freq_Hz": f, "sensitivity": s, "status": st}
        for l, f, s, st in PROBES], "other_channels": OTHER}
    with open("experiments/results/out_parity_web.json", "w") as f_:
        json.dump(out, f_, indent=2)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(9, 5))
        colors = {"future": "C0", "near": "C2", "null": "C3"}
        for lab, f, s, st in PROBES:
            ax.scatter([f], [s], s=140, color=colors[st], zorder=3,
                       edgecolor="k", linewidth=0.5)
            ax.annotate(lab, (f, s), textcoords="offset points",
                        xytext=(0, 12 if st != "null" else -28), ha="center", fontsize=8)
        ax.axhline(G_PV, color="C1", lw=2, ls="--",
                   label=f"predicted g_R2_parity = {G_PV}")
        ax.fill_between([1e-10, 1e5], 0, G_PV, color="C1", alpha=0.06)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(1e-10, 1e5); ax.set_ylim(2e-3, 3)
        ax.set_xlabel("gravitational-wave frequency [Hz]")
        ax.set_ylabel("sensitivity to g_R2_parity")
        ax.set_title("The multi-probe parity web: one coupling, ~10 decades in frequency\n"
                     "(points BELOW the dashed line can detect the predicted parity)")
        ax.legend(loc="upper center")
        ax.grid(alpha=0.3, which="both")
        ax.text(1e-9, 0.0035, "CMB EB (EM sibling) + sub-mm Yukawa (g_R2) probe the\n"
                "same dark-energy axion in non-GW channels", fontsize=7, color="gray")
        plt.tight_layout()
        plt.savefig("experiments/results/parity_web.png", dpi=120)
        print("\n  wrote experiments/results/parity_web.png")
    except Exception as e:
        print(f"  (plot skipped: {e})")
    print("\nwrote experiments/results/out_parity_web.json")


if __name__ == "__main__":
    main()
