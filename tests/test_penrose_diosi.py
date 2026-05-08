from itb.frameworks.penrose_diosi import PenroseDiosi


def test_returns_theory():
    fw = PenroseDiosi()
    theory = fw.encode()
    assert theory.coefficients["g_4"] > 0
    assert theory.coefficients["g_4"] < 0.1


def test_parity_conserving():
    theory = PenroseDiosi().encode()
    assert theory.coefficients["g_R2_parity"] == 0.0
    assert theory.coefficients["g_R3_parity"] == 0.0


def test_small_coefficients():
    """Penrose-Diosi treats gravity as near-classical → small coefs."""
    theory = PenroseDiosi().encode()
    assert all(v < 0.1 for v in theory.coefficients.values())
