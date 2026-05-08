from itb.constraints.base import Constraint, ConstraintResult, ConstraintClass
from itb.theory import Theory


class _DummyConstraint(Constraint):
    name = "dummy"
    citation = "test"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        margin = theory.coefficients.get("x", 0.0)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            details={"checked": "x >= 0"},
        )


def test_constraint_result_satisfied():
    c = _DummyConstraint()
    result = c.evaluate(Theory(coefficients={"x": 1.0}))
    assert result.satisfied is True
    assert result.margin == 1.0
    assert result.constraint_name == "dummy"


def test_constraint_result_violated():
    c = _DummyConstraint()
    result = c.evaluate(Theory(coefficients={"x": -2.0}))
    assert result.satisfied is False
    assert result.margin == -2.0


def test_constraint_metadata_present():
    c = _DummyConstraint()
    assert c.name == "dummy"
    assert c.citation == "test"
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE
