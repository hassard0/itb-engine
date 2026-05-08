from fastapi.testclient import TestClient

from itb.api.server import app

client = TestClient(app)

_FULL = [
    "scalar_positivity_g4", "scalar_positivity_g6",
    "scalar_convexity_g6_vs_g4", "graviton_mixed_positivity",
    "bekenstein_tight", "eft_validity_box",
]


def test_sensitivity_probability_endpoint():
    r = client.post("/sensitivity/probability", json={
        "coefficients": {"g_4": 0.5, "g_6": 0.4, "g_R2": 0.2},
        "constraints": _FULL,
        "sigma": 0.05, "n_samples": 100,
    })
    assert r.status_code == 200
    body = r.json()
    assert 0.0 <= body["p_feasible"] <= 1.0


def test_sensitivity_grid_endpoint():
    r = client.post("/sensitivity/grid", json={
        "x_param": "g_4", "x_range": [0.0, 1.0], "x_steps": 5,
        "y_param": "g_6", "y_range": [0.0, 1.0], "y_steps": 5,
        "constraints": _FULL,
        "sigma": 0.05, "n_samples": 30,
    })
    assert r.status_code == 200
    assert "p_grid" in r.json()


def test_duality_endpoint():
    r = client.post("/duality", json={
        "constraints": _FULL,
        "x_param": "g_4", "x_range": [0.0, 2.0], "x_steps": 11,
        "y_param": "g_6", "y_range": [0.0, 2.0], "y_steps": 11,
        "fixed_coefficients": {"g_R2": 0.5},
    })
    assert r.status_code == 200
    body = r.json()
    assert 0.0 <= body["iou"] <= 1.0


def test_voxel_endpoint_with_slice():
    r = client.post("/voxel", json={
        "x_param": "g_4", "x_range": [0.0, 1.0], "x_steps": 5,
        "y_param": "g_6", "y_range": [0.0, 1.0], "y_steps": 5,
        "z_param": "g_R2", "z_range": [0.0, 1.0], "z_steps": 5,
        "constraints": _FULL,
        "slice_axis": "g_R2",
        "slice_value": 0.0,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["shape"] == [5, 5, 5]
    assert "slice" in body


def test_fingerprint_endpoint():
    r = client.post("/fingerprint", json={
        "frameworks": ["pure_gr", "string_tree_eft"],
        "constraints": _FULL,
    })
    assert r.status_code == 200
    body = r.json()
    assert len(body["fingerprints"]) == 2
    assert len(body["distance_matrix"]) == 2
    # diagonal zeros
    assert body["distance_matrix"][0][0] == 0.0
    assert body["distance_matrix"][1][1] == 0.0
