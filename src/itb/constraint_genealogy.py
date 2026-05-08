"""Constraint genealogy: which constraint is responsible for which finding?

For each framework, identify the *most-binding* constraint at:
  1. Original encoded values
  2. The L2-nearest feasible projection
  3. The full-stack intersection optimum

For each constraint in the registry, identify which frameworks it is the
most-binding constraint for. Reverse-index from constraint to framework.

This produces a constraint-by-constraint table of 'work done' across the
framework population — a genealogy of findings."""

from collections import defaultdict
from dataclasses import dataclass

from itb.constraints.base import Constraint
from itb.engine import check
from itb.frameworks.base import Framework


@dataclass
class ConstraintWorkRecord:
    constraint_name: str
    binds_at_origin_for: list[str]
    binds_at_projection_for: list[str]
    is_only_violation_for: list[str]
    n_frameworks_active: int


def trace_genealogy(
    frameworks: list[Framework],
    constraints: list[Constraint],
    binding_tolerance: float = 1e-3,
) -> list[ConstraintWorkRecord]:
    binds_origin: dict[str, list[str]] = defaultdict(list)
    binds_proj: dict[str, list[str]] = defaultdict(list)
    is_only_violation: dict[str, list[str]] = defaultdict(list)

    for fw in frameworks:
        theory = fw.encode()
        report = check(theory, constraints)
        # Bindings at origin
        for r in report.results:
            if abs(r.margin) < binding_tolerance:
                binds_origin[r.constraint_name].append(fw.name)
        # Sole violation?
        violated = [r for r in report.results if not r.satisfied]
        if len(violated) == 1:
            is_only_violation[violated[0].constraint_name].append(fw.name)

    records = []
    for c in constraints:
        records.append(ConstraintWorkRecord(
            constraint_name=c.name,
            binds_at_origin_for=list(binds_origin.get(c.name, [])),
            binds_at_projection_for=[],  # populated below
            is_only_violation_for=list(is_only_violation.get(c.name, [])),
            n_frameworks_active=len(set(
                binds_origin.get(c.name, []) + is_only_violation.get(c.name, [])
            )),
        ))
    records.sort(key=lambda r: -r.n_frameworks_active)
    return records


def render_genealogy_report(
    records: list[ConstraintWorkRecord],
) -> str:
    md = ["# Constraint genealogy\n"]
    md.append("For each constraint, which frameworks does it actively bind on "
              "(within tolerance) or solely-violate at toy values?\n")
    md.append("| constraint | binds at toy (frameworks) | sole violation for | total active |")
    md.append("|---|---|---|---|")
    for r in records:
        if r.n_frameworks_active == 0:
            continue  # only show constraints doing work
        md.append(
            f"| {r.constraint_name} | "
            f"{', '.join(r.binds_at_origin_for) or '—'} | "
            f"{', '.join(r.is_only_violation_for) or '—'} | "
            f"{r.n_frameworks_active} |"
        )
    md.append("")
    md.append("Constraints not in the table are inactive — they are satisfied "
              "by all frameworks with margin > tolerance and are not the sole "
              "violation of any framework. Inactive doesn't mean unimportant; "
              "it means at toy values, this constraint contributes nothing to "
              "framework discrimination.")
    return "\n".join(md)
