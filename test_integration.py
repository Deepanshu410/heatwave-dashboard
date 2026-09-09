"""
Integration Test Suite for Full REST API Server & PRD Acceptance Criteria
Extreme Heatwave Early Warning & Human Thermal Stress Index Platform
"""

import json
from fastapi.testclient import TestClient
from main import app
from config import CITIES_DB, DEFAULT_CITY_ID


def run_integration_tests():
    print("==================================================================")
    print("   THERMALSENSE - FULL-STACK INTEGRATION TEST SUITE               ")
    print("==================================================================")
    client = TestClient(app)

    # 1. Test Index Web Page
    print("[TEST 1/6] Testing Web UI Route (GET /)...")
    res = client.get('/')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "ThermalSense" in res.text or "Human Thermal Stress Index" in res.text
    print("  [PASS] Dashboard HTML served successfully.")

    # 2. Test Cities API
    print("[TEST 2/6] Testing Supported Cities (GET /api/cities)...")
    res = client.get('/api/cities')
    assert res.status_code == 200
    cities = res.json()
    assert len(cities) >= 5
    print(f"  [PASS] Retrieved {len(cities)} socio-demographic wards.")

    # 3. Test City Current Conditions
    print("[TEST 3/6] Testing Current Conditions (GET /api/city/delhi/current)...")
    res = client.get('/api/city/delhi/current')
    assert res.status_code == 200
    curr = res.json()
    assert 'htsi_score' in curr
    assert 'risk_level' in curr
    assert 'driving_factor' in curr
    assert curr['risk_level'] in ['Safe', 'Caution', 'Danger', 'Extreme Danger']
    print(f"  [PASS] Current conditions: City={curr['city']}, HTSI={curr['htsi_score']}, Level={curr['risk_level']}")

    # 4. Test Hourly Forecast
    print("[TEST 4/6] Testing Hourly Forecast (GET /api/city/delhi/forecast)...")
    res = client.get('/api/city/delhi/forecast?hours=18')
    assert res.status_code == 200
    timeline = res.json()
    assert len(timeline) >= 12
    print(f"  [PASS] Hourly timeline returned {len(timeline)} points.")

    # 5. Test Historical Trend Data
    print("[TEST 5/6] Testing Historical Dataset (GET /api/city/delhi/history)...")
    res = client.get('/api/city/delhi/history?sample_rate=4')
    assert res.status_code == 200
    history = res.json()
    assert len(history) > 50
    print(f"  [PASS] Historical dataset returned {len(history)} trend records.")

    # 6. Test Targeted Organization Alerts
    print("[TEST 6/6] Testing Targeted Org Alerts (GET /api/alerts)...")
    for org in ['hospital', 'disaster_mgmt', 'outdoor_employer', 'citizen']:
        res = client.get(f'/api/alerts?org_type={org}')
        assert res.status_code == 200
        alerts = res.json()
        assert isinstance(alerts, list)
    print("  [PASS] Targeted alerts verified across all 4 organizational tiers.")

    print("==================================================================")
    print("   ALL INTEGRATION ACCEPTANCE TESTS PASSED (6/6)                  ")
    print("==================================================================")


if __name__ == '__main__':
    run_integration_tests()
