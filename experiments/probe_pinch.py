"""Probe: is the theory+both-data region empty or a microscopic sliver?
Test hand-constructed candidates in the pinch window and print every failing
constraint's margin, to find what (if anything) is incompatible."""
import sys
sys.path.insert(0, "src"); sys.path.insert(0, "experiments")
from stack import build_stack
from itb.theory import Theory

STK = build_stack(bnossw_mean="geometric", rfc_form="convex_hull",
                  include_data=True, include_birefringence=True)

cands = [
    # (label, coeffs)
    ("v1.77-matter + parity 0.050", dict(g_4=0.2465, g_6=0.0831, g_8=0.2804,
        g_R2=0.055, g_R3=0.0166, g_C=0.0798, g_R2_parity=0.050, g_R3_parity=0.0)),
    ("larger g_R2=0.062", dict(g_4=0.2465, g_6=0.0831, g_8=0.2804,
        g_R2=0.062, g_R3=0.0166, g_C=0.0798, g_R2_parity=0.050, g_R3_parity=0.0)),
    ("bigger matter", dict(g_4=0.40, g_6=0.20, g_8=0.35,
        g_R2=0.060, g_R3=0.030, g_C=0.10, g_R2_parity=0.050, g_R3_parity=0.0)),
    ("parity at band edge 0.047", dict(g_4=0.30, g_6=0.12, g_8=0.30,
        g_R2=0.062, g_R3=0.020, g_C=0.09, g_R2_parity=0.047, g_R3_parity=0.0)),
]

for label, c in cands:
    th = Theory(coefficients=c)
    fails = [(cc.name, round(cc.evaluate(th).margin, 4)) for cc in STK
             if not cc.evaluate(th).satisfied]
    print(f"\n=== {label} ===")
    print(f"  feasible: {len(fails) == 0}")
    if fails:
        for n, m in sorted(fails, key=lambda kv: kv[1]):
            print(f"    FAIL {n}: margin={m}")
