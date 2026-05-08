from fastapi.testclient import TestClient

from itb.api.server import app

client = TestClient(app)


def test_experiment_priority_endpoint():
    r = client.post("/experiment-priority", json={
        "base_constraints": [
            "scalar_positivity_g4", "scalar_positivity_g6",
            "scalar_convexity_g6_vs_g4", "bekenstein_tight",
        ],
        "experiments": [
            {"label": "tight", "coefficient_name": "g_R2",
             "central_value": 0.0, "sigma": 0.05},
            {"label": "loose", "coefficient_name": "g_R2",
             "central_value": 0.0, "sigma": 1.0},
        ],
        "x_param": "g_4", "x_range": [0.0, 2.0], "x_steps": 11,
        "y_param": "g_6", "y_range": [0.0, 2.0], "y_steps": 11,
        "fixed_coefficients": {"g_R2": 0.3},
    })
    assert r.status_code == 200
    body = r.json()
    assert "rankings" in body
    assert len(body["rankings"]) == 2
    # tighter should rank first
    assert body["rankings"][0]["label"] == "tight"
