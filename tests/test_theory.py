from itb.theory import Theory


def test_theory_holds_coefficients():
    t = Theory(coefficients={"g_4": 1.0, "g_6": 0.5})
    assert t.coefficients["g_4"] == 1.0
    assert t.coefficients["g_6"] == 0.5


def test_theory_get_with_default():
    t = Theory(coefficients={"g_4": 1.0})
    assert t.get("g_4") == 1.0
    assert t.get("g_6", default=0.0) == 0.0


def test_theory_with_metadata():
    t = Theory(coefficients={"g_4": 1.0}, name="test", source="unit-test")
    assert t.name == "test"
    assert t.source == "unit-test"


def test_theory_immutable_coefficients():
    t = Theory(coefficients={"g_4": 1.0})
    t2 = t.with_coefficient("g_6", 0.5)
    assert t2.coefficients["g_4"] == 1.0
    assert t2.coefficients["g_6"] == 0.5
    assert "g_6" not in t.coefficients
