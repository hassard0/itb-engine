from fastapi.testclient import TestClient

from itb.api.server import app


client = TestClient(app)


def test_constraints_listing_includes_convexity():
    r = client.get("/constraints")
    items = r.json()
    names = [it["name"] for it in items]
    assert "scalar_convexity_g6_vs_g4" in names


def test_per_constraint_color_mode():
    r = client.post(
        "/sweep",
        json={
            "x_param": "g_4",
            "x_range": [-1.0, 1.0],
            "x_steps": 7,
            "y_param": "g_6",
            "y_range": [-1.0, 1.0],
            "y_steps": 7,
            "constraints": [
                "scalar_positivity_g4",
                "scalar_positivity_g6",
                "scalar_convexity_g6_vs_g4",
            ],
            "color_by": "per_constraint",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "figure" in body


def test_fragility_endpoint():
    r = client.post(
        "/fragility",
        json={
            "x_param": "g_4",
            "x_range": [-1.0, 1.0],
            "x_steps": 7,
            "y_param": "g_6",
            "y_range": [-1.0, 1.0],
            "y_steps": 7,
            "constraints": [
                "scalar_positivity_g4",
                "scalar_positivity_g6",
                "scalar_convexity_g6_vs_g4",
            ],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "distance_grid" in body
    assert "most_fragile_grid" in body
    assert "figure" in body


def test_importance_endpoint():
    r = client.post(
        "/importance",
        json={
            "x_param": "g_4",
            "x_range": [-1.0, 1.0],
            "x_steps": 11,
            "y_param": "g_6",
            "y_range": [-1.0, 1.0],
            "y_steps": 11,
            "constraints": [
                "scalar_positivity_g4",
                "scalar_positivity_g6",
                "scalar_convexity_g6_vs_g4",
            ],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "scores" in body
    assert len(body["scores"]) == 3
    assert "baseline_allowed_count" in body
