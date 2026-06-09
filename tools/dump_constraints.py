"""List the full constraint stack (theoretical + data) by class, for docs."""
import sys
sys.path.insert(0, "src"); sys.path.insert(0, "experiments")
from stack import build_stack
from itb.constraints.base import ConstraintClass

theo = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
data = build_stack(bnossw_mean="geometric", rfc_form="convex_hull",
                   include_data=True, include_birefringence=True,
                   include_gw_speed=True, include_gw_dispersion=True)
data_only = [c for c in data if c.name not in {t.name for t in theo}]

labels = {ConstraintClass.A_AMPLITUDE: "A - Amplitude bootstrap",
          ConstraintClass.B_INFORMATION: "B - Information-theoretic",
          ConstraintClass.C_UNIVERSALITY: "C - Gravitational universality"}
for cc in (ConstraintClass.A_AMPLITUDE, ConstraintClass.B_INFORMATION,
           ConstraintClass.C_UNIVERSALITY):
    rows = [c for c in theo if c.constraint_class == cc]
    print(f"\n## Class {labels[cc]} ({len(rows)})\n")
    for c in rows:
        cit = (c.citation or "").strip()
        print(f"- `{c.name}`" + (f" — {cit}" if cit else ""))
print(f"\n## DATA constraints (opt-in, {len(data_only)})\n")
for c in data_only:
    print(f"- `{c.name}` — {(c.citation or '').strip()}")
print(f"\nTOTAL theoretical: {len(theo)}  |  data: {len(data_only)}")
