from fastapi.testclient import TestClient

from itb.api.server import app


client = TestClient(app, raise_server_exceptions=False)


def test_server_registry_exposes_current_research_surface():
    constraints = {item["name"] for item in client.get("/constraints").json()}
    frameworks = {item["name"] for item in client.get("/frameworks").json()}

    assert "species_scale_bound" in constraints
    assert "submm_gravity_yukawa_bound" in constraints
    assert "cosmic_birefringence_data" in constraints
    assert "discovered_data_driven" in frameworks
    assert "group_field_theory" in frameworks


def test_sweep_rejects_invalid_step_counts():
    response = client.post(
        "/sweep",
        json={
            "x_param": "g_4",
            "x_range": [0.0, 1.0],
            "x_steps": 0,
            "y_param": "g_6",
            "y_range": [0.0, 1.0],
            "y_steps": 2,
            "constraints": ["scalar_positivity_g4"],
        },
    )
    assert response.status_code == 422


def test_sensitivity_rejects_zero_samples():
    response = client.post(
        "/sensitivity/probability",
        json={
            "coefficients": {"g_4": 1.0},
            "constraints": ["scalar_positivity_g4"],
            "n_samples": 0,
        },
    )
    assert response.status_code == 422


def test_fisher_rejects_zero_sigma():
    response = client.post(
        "/fisher",
        json={
            "coefficients": {"g_4": 1.0},
            "params": ["g_4"],
            "s_values": [1.0],
            "sigma": 0.0,
        },
    )
    assert response.status_code == 422
