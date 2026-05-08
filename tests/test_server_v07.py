from fastapi.testclient import TestClient

from itb.api.server import app

client = TestClient(app)


def test_constraints_listing_includes_v07():
    items = client.get("/constraints").json()
    names = {it["name"] for it in items}
    assert "spin_zero_positivity" in names
    assert "spin_two_positivity" in names


def test_frameworks_listing_includes_v07():
    items = client.get("/frameworks").json()
    names = {it["name"] for it in items}
    assert "asymptotic_safety" in names
    assert "lqg_induced" in names


def test_measurement_endpoint():
    r = client.post("/measurement", json={
        "coefficient_name": "g_R2",
        "central_value": 0.2,
        "sigma": 0.05,
        "experiment_label": "synth_2026",
        "coefficients": {"g_4": 0.5, "g_6": 0.4, "g_R2": 0.2},
    })
    assert r.status_code == 200
    assert r.json()["satisfied"] is True


def test_framework_report_endpoint():
    r = client.post("/framework-report", json={
        "frameworks": ["pure_gr", "string_tree_eft", "asymptotic_safety", "lqg_induced"],
        "constraints": [
            "scalar_positivity_g4", "scalar_positivity_g6",
            "scalar_convexity_g6_vs_g4", "graviton_mixed_positivity",
            "bekenstein_tight", "eft_validity_box",
        ],
    })
    assert r.status_code == 200
    body = r.json()
    assert "markdown" in body
    assert body["framework_count"] == 4
    assert "string_tree_eft" in body["markdown"]
    assert "asymptotic_safety" in body["markdown"]
