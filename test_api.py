"""
Integration Test Suite for FastAPI REST API Endpoints & /analyze Canonical Contract
"""

import sys
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_analyze_canonical_endpoint():
    print("[1/8] Testing GET /analyze?city=patna...")
    resp = client.get("/analyze?city=patna")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()

    # Verify top-level structure exactly as specified by user
    required_sections = [
        "target_node",
        "realtime_ingested_metrics",
        "iot_sensor_validation_gate",
        "satellite_environmental_overrides",
        "predictive_analytics_output",
        "targeted_administrative_triggers"
    ]
    for section in required_sections:
        assert section in data, f"Missing section '{section}' in /analyze payload"

    # Target Node verification
    node = data["target_node"]
    assert node["location_id"] == 5
    assert node["id"] == "WARD-PAT-05"
    assert "Patna" in node["name"]
    assert node["terrain"] == "plain"

    # Realtime Ingested Metrics verification
    metrics = data["realtime_ingested_metrics"]
    for m in ["heat_index", "swbgt", "wet_bulb", "utci"]:
        assert m in metrics, f"Missing metric '{m}'"

    # Predictive Output verification
    pred = data["predictive_analytics_output"]
    assert "current_mortality_risk_index" in pred
    assert "/10.0" in pred["current_mortality_risk_index"]
    assert len(pred["predictive_temporal_12h_forecast_horizon"]) == 12

    # Targeted Administrative Triggers verification
    triggers = data["targeted_administrative_triggers"]
    assert "disaster_management_authority" in triggers
    assert "healthcare_administration_system" in triggers
    assert "power_grid_corporation" in triggers

    print(f"  [PASS] /analyze endpoint returned canonical envelope for Patna.")
    print(f"         MRI Score: {pred['current_mortality_risk_index']}")
    print(f"         12h Horizon Frames: {len(pred['predictive_temporal_12h_forecast_horizon'])}")


def test_analyze_default_fallback():
    print("[2/8] Testing GET /analyze with default fallback (Haldwani)...")
    resp = client.get("/analyze")
    assert resp.status_code == 200
    data = resp.json()
    assert data["target_node"]["id"] == "WARD-HLD-01"
    print("  [PASS] Default fallback successfully resolved to Haldwani [WARD-HLD-01].")


def test_api_cities():
    print("[3/8] Testing GET /api/cities...")
    resp = client.get("/api/cities")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert isinstance(data, list), "Expected list of cities"
    assert len(data) >= 5, f"Expected at least 5 cities, got {len(data)}"
    ward_ids = [c['ward_id'] for c in data]
    assert 'WARD-HLD-01' in ward_ids
    assert 'WARD-PAT-05' in ward_ids
    print(f"  [PASS] Successfully retrieved {len(data)} socio-demographic wards.")


def test_api_current_conditions():
    print("[4/8] Testing GET /api/city/delhi/current...")
    resp = client.get("/api/city/delhi/current")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert 'city' in data
    assert 'htsi_score' in data
    assert 'risk_level' in data
    print(f"  [PASS] Delhi Current: City={data['city']}, MRI/HTSI={data['htsi_score']}, Tier={data['risk_level']}")


def test_api_forecast():
    print("[5/8] Testing GET /api/city/mumbai/forecast...")
    resp = client.get("/api/city/mumbai/forecast")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert len(data) == 12, f"Expected exactly 12 forecast points, got {len(data)}"
    print(f"  [PASS] Mumbai 12-hour forecast horizon returned {len(data)} hourly frames.")


def test_api_targeted_alerts():
    print("[6/8] Testing GET /api/alerts...")
    resp_all = client.get("/api/alerts")
    assert resp_all.status_code == 200, f"Expected 200, got {resp_all.status_code}"
    data_all = resp_all.json()
    assert isinstance(data_all, list)

    for org in ['hospital', 'disaster_mgmt', 'outdoor_employer']:
        resp = client.get(f"/api/alerts?org_type={org}")
        assert resp.status_code == 200
        org_alerts = resp.json()
        assert isinstance(org_alerts, list)
        for a in org_alerts:
            assert a['org_type'] == org
    print("  [PASS] Targeted alerts verified across organizations.")


def test_api_model_info():
    print("[7/8] Testing GET /api/model/info...")
    resp = client.get("/api/model/info")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data['model_name'] == 'biometeorological_strain_v2'
    assert data['multivariate_linear_regression']['w_heat_index'] == 0.0420
    assert data['multivariate_linear_regression']['w_wet_bulb'] == 0.0650
    assert data['multivariate_linear_regression']['w_utci'] == 0.0240
    print(f"  [PASS] Model info matches biometeorological_strain_v2 parameters.")


def test_dashboard_route():
    print("[8/8] Testing GET / (HTML Dashboard)...")
    resp = client.get("/")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    html = resp.text
    assert "ThermalSense" in html or "Mortality Risk" in html
    print("  [PASS] Dashboard HTML loaded cleanly.")


if __name__ == "__main__":
    print("================================================================")
    print("   EXTREME HEATWAVE PLATFORM - FASTAPI & /analyze TEST SUITE    ")
    print("================================================================")
    test_analyze_canonical_endpoint()
    test_analyze_default_fallback()
    test_api_cities()
    test_api_current_conditions()
    test_api_forecast()
    test_api_targeted_alerts()
    test_api_model_info()
    test_dashboard_route()
    print("================================================================")
    print("   ALL INTEGRATION & CANONICAL TESTS PASSED (8/8)               ")
    print("================================================================")
