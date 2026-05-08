from fastapi.testclient import TestClient

from itb.api.server import app


client = TestClient(app)


def test_sweep_returns_binding_class_figure_when_requested():
    r = client.post(
        "/sweep",
        json={
            "x_param": "g_4",
            "x_range": [-1.0, 1.0],
            "x_steps": 7,
            "y_param": "g_6",
            "y_range": [-1.0, 1.0],
            "y_steps": 7,
            "constraints": ["scalar_positivity_g4", "scalar_positivity_g6"],
            "color_by": "binding_class",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "figure" in body
    assert "binding_grid" in body


def test_perturbation_endpoint():
    r = client.post(
        "/perturbation",
        json={
            "coefficients": {"g_4": 0.5, "g_6": 0.5},
            "constraints": ["scalar_positivity_g4", "scalar_positivity_g6"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "distance" in body
    assert "binding_constraint" in body
    assert body["distance"] > 0


def test_fisher_endpoint():
    r = client.post(
        "/fisher",
        json={
            "coefficients": {"g_4": 0.5, "g_6": 0.5},
            "params": ["g_4", "g_6"],
            "s_values": [0.5, 1.0],
            "sigma": 0.1,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "metric" in body
    assert len(body["metric"]) == 2
    assert len(body["metric"][0]) == 2
