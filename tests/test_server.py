from fastapi.testclient import TestClient

from itb.api.server import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_check_pure_gr():
    r = client.post(
        "/check",
        json={
            "coefficients": {"g_4": 0.0, "g_6": 0.0},
            "constraints": ["scalar_positivity_g4", "scalar_positivity_g6"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["feasible"] is True
    names = [r["constraint_name"] for r in body["results"]]
    assert "scalar_positivity_g4" in names
    assert "scalar_positivity_g6" in names


def test_check_violation():
    r = client.post(
        "/check",
        json={
            "coefficients": {"g_4": -1.0, "g_6": 0.5},
            "constraints": ["scalar_positivity_g4", "scalar_positivity_g6"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["feasible"] is False


def test_unknown_constraint_returns_400():
    r = client.post(
        "/check",
        json={
            "coefficients": {"g_4": 1.0},
            "constraints": ["does_not_exist"],
        },
    )
    assert r.status_code == 400


def test_sweep_returns_grid_and_figure():
    r = client.post(
        "/sweep",
        json={
            "x_param": "g_4",
            "x_range": [-1.0, 1.0],
            "x_steps": 5,
            "y_param": "g_6",
            "y_range": [-1.0, 1.0],
            "y_steps": 5,
            "constraints": ["scalar_positivity_g4", "scalar_positivity_g6"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "grid" in body
    assert len(body["grid"]) == 5
    assert len(body["grid"][0]) == 5
    assert "figure" in body


def test_constraints_listing():
    r = client.get("/constraints")
    assert r.status_code == 200
    items = r.json()
    names = [item["name"] for item in items]
    assert "scalar_positivity_g4" in names
    assert "scalar_positivity_g6" in names


def test_frameworks_listing():
    r = client.get("/frameworks")
    assert r.status_code == 200
    items = r.json()
    names = [item["name"] for item in items]
    assert "pure_gr" in names
