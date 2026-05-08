"""Experimental constraints: encode a measured Wilson coefficient with a
Gaussian uncertainty as a soft constraint.

A measurement gives `coefficient_name = mu ± sigma`. Theories near `mu` are
preferred; theories far from `mu` are penalized in proportion to the
distance / sigma. We expose this as a constraint with margin proportional to
`(2*sigma_threshold - |coefficient - mu| / sigma)`, so the constraint binds
once we exceed `sigma_threshold`σ from the central value.

This is the "experiments-as-constraints" idea (#10 from the theorize doc):
data becomes another physical principle the engine has to reconcile."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class MeasuredWilsonCoefficient(Constraint):
    constraint_class = ConstraintClass.B_INFORMATION  # data is information

    def __init__(
        self,
        coefficient_name: str,
        central_value: float,
        sigma: float,
        sigma_threshold: float = 2.0,
        experiment_label: str = "synthetic",
    ):
        self.coefficient_name = coefficient_name
        self.central_value = float(central_value)
        self.sigma = float(sigma)
        self.sigma_threshold = float(sigma_threshold)
        self.experiment_label = experiment_label
        self.name = f"measurement_{experiment_label}_{coefficient_name}"
        self.citation = (
            f"experimental constraint ({experiment_label}): {coefficient_name} = "
            f"{central_value} ± {sigma} (≤{sigma_threshold}σ allowed)"
        )

    def evaluate(self, theory: Theory) -> ConstraintResult:
        v = theory.coefficients.get(self.coefficient_name, 0.0)
        deviation = abs(v - self.central_value) / self.sigma if self.sigma > 0 else 0.0
        margin = self.sigma_threshold - deviation
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "coefficient": self.coefficient_name,
                "central_value": self.central_value,
                "sigma": self.sigma,
                "deviation_in_sigmas": deviation,
                "experiment_label": self.experiment_label,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        v = theory.coefficients.get(self.coefficient_name, 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault(self.coefficient_name, 0.0)
        if self.sigma > 0:
            sign = 1.0 if v >= self.central_value else -1.0
            out[self.coefficient_name] = -sign / self.sigma
        return out
