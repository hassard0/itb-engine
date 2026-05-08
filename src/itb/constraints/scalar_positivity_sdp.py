"""SDP-mode positivity bound. Uses cvxpy to formulate g_4 >= 0 as an SDP
feasibility problem. Lazy import of cvxpy: it is only imported when the
constraint is actually evaluated, so importing this module costs nothing."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class ScalarPositivityG4SDP(Constraint):
    name = "scalar_positivity_g4_sdp"
    citation = "Adams et al 2006 (cvxpy SDP form)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory, tolerance: float = 1e-7) -> ConstraintResult:
        import cvxpy as cp_local

        g4_value = float(theory.coefficients.get("g_4", 0.0))
        x = cp_local.Variable()
        constraints = [x >= 0, x == g4_value]
        prob = cp_local.Problem(cp_local.Minimize(0), constraints)
        prob.solve(solver=cp_local.SCS, verbose=False)
        status = prob.status
        feasible = status in (cp_local.OPTIMAL, cp_local.OPTIMAL_INACCURATE) and g4_value >= -tolerance
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=feasible,
            margin=g4_value,
            signed_distance_margin=g4_value,
            details={"bound": "g_4 >= 0 (SDP)", "value": g4_value, "solver_status": status},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_4", 0.0)
        out["g_4"] = 1.0
        return out
