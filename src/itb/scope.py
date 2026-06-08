"""Engine validity scope (v1.59).

Operationalizes the v1.58 finding: the engine's amplitude-positivity bounds are
derived assuming a LOCAL, LORENTZ-INVARIANT, unitary S-matrix, and the swampland
program assumes locality. A framework that breaks one of these assumptions is
OUTSIDE the engine's validity scope — its feasibility verdict is not meaningful
(the constraints may simply not apply). This module lets the engine declare its
own scope instead of silently returning a verdict it can't justify.
"""

from dataclasses import dataclass


@dataclass
class ScopeVerdict:
    framework: str
    in_scope: bool
    violations: list  # which assumptions are broken
    note: str


def engine_validity(framework) -> ScopeVerdict:
    """Is `framework` within the scope where the engine's constraints validly
    apply? Reads the framework's `local` / `lorentz_invariant` flags."""
    viol = []
    if not getattr(framework, "lorentz_invariant", True):
        viol.append("Lorentz invariance (assumed by amplitude-positivity bounds)")
    if not getattr(framework, "local", True):
        viol.append("locality (assumed by the swampland/positivity program)")
    if not getattr(framework, "fundamental", True):
        viol.append("a fundamental UV graviton field (the bounds expand the graviton "
                    "amplitude; emergent gravity has no such UV expansion)")
    if viol:
        note = ("OUT OF SCOPE: the engine's feasibility verdict is NOT meaningful for "
                "this framework — it breaks " + " and ".join(viol) + ", which are "
                "assumptions used to derive the constraints. Treat any verdict as an "
                "artifact of applying inapplicable bounds.")
        return ScopeVerdict(framework.name, False, viol, note)
    return ScopeVerdict(framework.name, True, [],
                        "in scope: local, Lorentz-invariant — engine verdict is meaningful.")
