from fastapi.testclient import TestClient

from itb.api.server import app


client = TestClient(app)


_THREE = [
    "scalar_positivity_g4",
    "scalar_positivity_g6",
    "scalar_convexity_g6_vs_g4",
]


def test_adversarial_endpoint():
    r = client.post(
        "/adversarial",
        json={
            "initial_guess": {"g_4": 0.5, "g_6": 0.5},
            "constraints": _THREE,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "coefficients" in body
    assert "n_binding" in body
    assert body["n_binding"] >= 2


def test_path_endpoint_connected():
    r = client.post(
        "/path",
        json={
            "start": {"g_4": 0.2, "g_6": 0.5},
            "end": {"g_4": 0.4, "g_6": 0.6},
            "x_param": "g_4", "x_range": [0.0, 1.0], "x_steps": 11,
            "y_param": "g_6", "y_range": [0.0, 1.0], "y_steps": 11,
            "constraints": _THREE,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["connected"] is True
    assert body["distance"] >= 0


def test_path_endpoint_disconnected():
    r = client.post(
        "/path",
        json={
            "start": {"g_4": 0.5, "g_6": 0.5},
            "end": {"g_4": -0.5, "g_6": -0.5},
            "x_param": "g_4", "x_range": [-1.0, 1.0], "x_steps": 21,
            "y_param": "g_6", "y_range": [-1.0, 1.0], "y_steps": 21,
            "constraints": _THREE,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["connected"] is False
    assert body["distance"] is None


def test_completeness_endpoint():
    r = client.post(
        "/completeness",
        json={
            "constraints": _THREE,
            "params": ["g_4", "g_6"],
            "starting_box": 2.0,
            "max_box": 4.0,
            "steps_per_axis": 7,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "bounded" in body
    assert body["bounded"] is False  # the wedge is unbounded


def test_graviton_constraint_in_listing():
    r = client.get("/constraints")
    items = r.json()
    names = [it["name"] for it in items]
    assert "graviton_mixed_positivity" in names


def test_check_with_g_R2_coefficient():
    r = client.post(
        "/check",
        json={
            "coefficients": {"g_4": 1.0, "g_6": 1.0, "g_R2": 0.5},
            "constraints": _THREE + ["graviton_mixed_positivity"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["feasible"] is True
