"""Prefactor sensitivity analysis.

Many of the engine's constraints have O(1) numerical prefactors that are
publication-grade-flavored simplifications. The question this module
answers: how *robust* is a framework's feasibility status to those
prefactors?

For a constraint with a tunable prefactor (e.g., BNOSSW MMI's coefficient
on the harmonic mean), sweep the prefactor across a range and record:
for each framework, the threshold prefactor value at which the framework
transitions from feasible to infeasible (or vice versa).

The output: a sensitivity score per (framework, prefactor) pair. If the
threshold is far from the literature-suggested value, the framework's
status is *robust*. If the threshold is close, it's *prefactor-sensitive*
and may not survive proper publication-grade encoding."""

from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np

from itb.constraints.base import Constraint
from itb.engine import check
from itb.frameworks.base import Framework


@dataclass
class FrameworkSensitivity:
    framework_name: str
    prefactor_values: list[float]
    feasibility: list[bool]
    transition_prefactor: float | None    # value at which framework status flips


def sweep_prefactor(
    constraint_factory: Callable[[float], Constraint],
    prefactor_values: Iterable[float],
    other_constraints: list[Constraint],
    frameworks: list[Framework],
) -> list[FrameworkSensitivity]:
    """Sweep a constraint's prefactor and record framework feasibility per value.

    `constraint_factory(value) -> Constraint` builds the constraint with the
    given prefactor. We test each framework against `[constraint_factory(v)] +
    other_constraints` for each v.

    Returns: per-framework list of feasibility, plus the prefactor value at
    which the framework's status transitions (if any)."""
    values = list(prefactor_values)
    out: list[FrameworkSensitivity] = []
    for fw in frameworks:
        feasibility = []
        for v in values:
            constraints = [constraint_factory(v)] + other_constraints
            theory = fw.encode()
            feasibility.append(check(theory, constraints).feasible)
        # Transition: first value where state changes from earlier value
        transition = None
        for i in range(1, len(feasibility)):
            if feasibility[i] != feasibility[i - 1]:
                transition = values[i]
                break
        out.append(FrameworkSensitivity(
            framework_name=fw.name,
            prefactor_values=values,
            feasibility=feasibility,
            transition_prefactor=transition,
        ))
    return out


def render_sensitivity_report(
    constraint_label: str,
    results: list[FrameworkSensitivity],
) -> str:
    lines: list[str] = []
    lines.append(f"# Prefactor sensitivity: {constraint_label}")
    lines.append("")
    lines.append("| framework | feasibility @ values | transition prefactor |")
    lines.append("|---|---|---|")
    for r in results:
        states = "".join("✓" if f else "✗" for f in r.feasibility)
        trans = f"{r.transition_prefactor:.4f}" if r.transition_prefactor is not None else "(no flip)"
        lines.append(f"| {r.framework_name} | `{states}` | {trans} |")
    lines.append("")
    lines.append(f"**Prefactor values swept:** {results[0].prefactor_values if results else []}")
    return "\n".join(lines)
