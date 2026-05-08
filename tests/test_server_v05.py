from fastapi.testclient import TestClient

from itb.api.server import app


client = TestClient(app)


_FULL_STACK = [
    "scalar_positivity_g4",
    "scalar_positivity_g6",
    "scalar_convexity_g6_vs_g4",
    "graviton_mixed_positivity",
    "bekenstein_tight",
    "eft_validity_box",
]


def test_constraints_listing_includes_v05_additions():
    r = client.get("/constraints")
    items = r.json()
    names = [it["name"] for it in items]
    assert "bekenstein_tight" in names
    assert "eft_validity_box" in names
    classes = {it["name"]: it["constraint_class"] for it in items}
    assert classes["bekenstein_tight"] == "information_theoretic"
    assert classes["eft_validity_box"] == "gravitational_universality"


def test_frameworks_listing_includes_string_eft():
    r = client.get("/frameworks")
    items = r.json()
    names = [it["name"] for it in items]
    assert "string_tree_eft" in names


def test_phases_endpoint_first_quadrant_one_component():
    r = client.post(
        "/phases",
        json={
            "x_param": "g_4",
            "x_range": [-1.0, 1.0],
            "x_steps": 21,
            "y_param": "g_6",
            "y_range": [-1.0, 1.0],
            "y_steps": 21,
            "constraints": [
                "scalar_positivity_g4",
                "scalar_positivity_g6",
                "scalar_convexity_g6_vs_g4",
            ],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["n_components"] == 1


def test_sweep_with_framework_overlay():
    r = client.post(
        "/sweep",
        json={
            "x_param": "g_4",
            "x_range": [0.0, 1.0],
            "x_steps": 11,
            "y_param": "g_6",
            "y_range": [0.0, 1.0],
            "y_steps": 11,
            "constraints": [
                "scalar_positivity_g4",
                "scalar_positivity_g6",
                "scalar_convexity_g6_vs_g4",
            ],
            "overlay_frameworks": ["pure_gr", "string_tree_eft"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "overlay_frameworks" in body
    names = [f["name"] for f in body["overlay_frameworks"]]
    assert "pure_gr" in names
    assert "string_tree_eft" in names


def test_string_eft_within_full_stack_via_check_endpoint():
    """The acid test: ask the engine, via the HTTP API, whether string-EFT
    is consistent with every constraint we have."""
    r = client.post(
        "/check",
        json={
            "coefficients": {"g_4": 0.5, "g_6": 0.4, "g_R2": 0.2},
            "constraints": _FULL_STACK,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["feasible"] is True


def test_completeness_now_bounded_with_validity_box():
    r = client.post(
        "/completeness",
        json={
            "constraints": _FULL_STACK,
            "params": ["g_4", "g_6"],
            "starting_box": 2.0,
            "max_box": 8.0,
            "steps_per_axis": 11,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["bounded"] is True
