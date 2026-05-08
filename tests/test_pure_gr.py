from itb.frameworks.pure_gr import PureGR
from itb.theory import Theory


def test_pure_gr_returns_theory():
    fw = PureGR()
    theory = fw.encode()
    assert isinstance(theory, Theory)


def test_pure_gr_higher_order_coefficients_zero():
    theory = PureGR().encode()
    assert theory.coefficients.get("g_4", 0.0) == 0.0
    assert theory.coefficients.get("g_6", 0.0) == 0.0


def test_pure_gr_metadata():
    theory = PureGR().encode()
    assert theory.name == "pure_gr"
    assert "Einstein" in theory.source
