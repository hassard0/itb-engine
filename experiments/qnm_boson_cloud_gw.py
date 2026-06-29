"""v2.245 - The boson cloud as a continuous-GW source: the direct-detection side of superradiance.

v2.243/v2.244 used superradiance as an INDIRECT probe (a spun-down hole excludes a boson). But the
superradiant cloud is also a DIRECT gravitational-wave source: the bosons annihilate in pairs to
gravitons, radiating a nearly MONOCHROMATIC, long-lived ("continuous-wave") signal at

    f_GW = mu c^2 / (pi hbar)        (two bosons of rest energy ~mu -> one graviton of energy ~2 mu),

with only a tiny secular drift as the cloud depletes. So the superradiance boson-mass windows map
DIRECTLY onto gravitational-wave detector bands: a measured high black-hole spin says "a boson cloud
should be there", and a continuous-wave search at the predicted frequency can confirm or refute it.

This cycle maps the v2.244 Regge-exclusion windows to their GW frequencies and detector bands,
completing the superradiance story (indirect spin bound + direct CW detection).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_superradiance_regge_exclusion import run as regge_run

VERSION = "v2.245"
DEFAULT_OUT = Path("experiments/results/v2.245/qnm_boson_cloud_gw.json")
HBAR_eV_s = 6.582119e-16


def f_gw_hz(mu_eV: float) -> float:
    """Boson-annihilation GW frequency f = mu c^2/(pi hbar)."""
    import math
    return mu_eV / (math.pi * HBAR_eV_s)


def detector_band(f_hz: float) -> str:
    if f_hz >= 10:
        return "LIGO/Virgo/KAGRA (10-2000 Hz)"
    if f_hz >= 1e-1:
        return "deci-Hz (Einstein Telescope / DECIGO)"
    if f_hz >= 1e-4:
        return "LISA (0.1-100 mHz)"
    return "PTA / nHz"


def run() -> dict:
    regge = regge_run()["regge_exclusion"]
    rows = []
    for r in regge:
        if not r["excluded_alpha"]:
            continue
        lo, hi = r["excluded_mu_eV"]
        flo, fhi = f_gw_hz(lo), f_gw_hz(hi)
        rows.append({"system": r["label"], "mu_window_eV": [lo, hi],
                     "f_gw_hz": [flo, fhi], "band": detector_band((flo * fhi) ** 0.5)})
    return {
        "version": VERSION,
        "method": ("boson-annihilation GW frequency f = mu c^2/(pi hbar) applied to the v2.244 "
                   "superradiance-excluded boson-mass windows; assign detector bands"),
        "cloud_gw_bands": rows,
        "finding": (
            "The superradiant boson cloud is a continuous-wave GW source whose frequency "
            "(f = mu c^2/(pi hbar)) maps the superradiance boson-mass windows DIRECTLY onto detector "
            "bands: stellar-mass black-hole clouds radiate at "
            f"~{rows[0]['f_gw_hz'][0]:.0f}-{rows[0]['f_gw_hz'][1]:.0f} Hz (LIGO/Virgo/KAGRA), a "
            "supermassive (1e6 Msun) cloud at mHz (LISA), and an M87*-scale cloud at micro-Hz "
            "(PTA/nHz). So superradiance is a TWO-SIDED probe: a measured high spin excludes a boson "
            "(indirect, v2.243/v2.244) AND predicts a nearly-monochromatic GW line at a definite "
            "frequency that a continuous-wave search can directly target. The same physics that makes "
            "black-hole spin an ultralight-boson detector also makes the boson cloud a gravitational-"
            "wave beacon, with the detector band set simply by the black-hole mass."
        ),
        "honest_scope": (
            "The annihilation FREQUENCY f = mu c^2/(pi hbar) is exact at leading order (small "
            "alpha^2 binding corrections and a tiny secular spin-up as the cloud depletes are "
            "neglected -- the signal is monochromatic to high precision, the basis of continuous-wave "
            "searches). The detector-band mapping is robust; the STRAIN amplitude / detectability "
            "(which sets whether each source is actually seen) depends on the cloud mass (~a few % of "
            "M), distance, and search coherence -- not computed here. The boson-mass windows are the "
            "v2.244 representative ones (their caveats carry). This is the frequency/band reconstruct"
            "ion of the direct-detection channel, not a detectability forecast. Parity-odd g_R4_c3 "
            "stays dark (v2.209)."
        ),
        "references": [
            "Arvanitaki & Dubovsky, PRD 83 (2011) 044026 -- boson annihilation GW signal",
            "Brito, Cardoso, Pani, Lect. Notes Phys. 906 (2015); Brito et al., PRD 96 (2017) 064050",
            "this repo: v2.243/v2.244 (superradiance condition / Regge exclusion)",
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
    print("system                                    f_GW (Hz)            band")
    for r in res["cloud_gw_bands"]:
        print(f"  {r['system'][:38]:38s} [{r['f_gw_hz'][0]:.2e},{r['f_gw_hz'][1]:.2e}]  {r['band']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
