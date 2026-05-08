"""Adams-Arkani-Hamed-Dubovsky-Nicolis-Rattazzi (2006) positivity bounds for a
real-scalar EFT. The forward 2->2 elastic amplitude must satisfy g_{2n} >= 0
for n >= 2 from analyticity + unitarity + crossing.

Reference:
  Adams, Arkani-Hamed, Dubovsky, Nicolis, Rattazzi. "Causality, Analyticity
  and an IR Obstruction to UV Completion." JHEP 10 (2006) 014.
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class ScalarPositivityG4(Constraint):
    name = "scalar_positivity_g4"
    citation = "Adams, Arkani-Hamed, Dubovsky, Nicolis, Rattazzi 2006"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=g4 >= 0,
            margin=g4,
            details={"bound": "g_4 >= 0", "value": g4},
        )


class ScalarPositivityG6(Constraint):
    name = "scalar_positivity_g6"
    citation = "Adams, Arkani-Hamed, Dubovsky, Nicolis, Rattazzi 2006"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g6 = theory.coefficients.get("g_6", 0.0)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=g6 >= 0,
            margin=g6,
            details={"bound": "g_6 >= 0", "value": g6},
        )
