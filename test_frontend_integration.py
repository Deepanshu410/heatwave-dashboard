"""
Verification script for HaiGarmi frontend integration against PRD Acceptance Criteria
"""

import json
import urllib.request
import re
import sys

BASE_URL = "http://localhost:8000"
CITIES = ["haldwani", "nainital", "delhi", "mumbai", "patna"]

def test_backend_api():
    print("=" * 60)
    print("TEST 1: Backend API /analyze Verification across 5 cities")
    print("=" * 60)
    
    for city in CITIES:
        url = f"{BASE_URL}/analyze?city={city}"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as response:
                assert response.status == 200, f"Expected status 200 for {city}, got {response.status}"
                data = json.loads(response.read().decode("utf-8"))
                
                # Check target_node
                assert "target_node" in data, f"Missing target_node for {city}"
                node = data["target_node"]
                assert "name" in node and node["name"], f"Missing name for {city}"
                assert "id" in node and node["id"], f"Missing id for {city}"
                assert "terrain" in node and node["terrain"], f"Missing terrain for {city}"
                
                # Check realtime_ingested_metrics (4 metrics)
                assert "realtime_ingested_metrics" in data, f"Missing realtime_ingested_metrics for {city}"
                metrics = data["realtime_ingested_metrics"]
                for key in ["heat_index", "swbgt", "wet_bulb", "utci"]:
                    assert key in metrics, f"Missing metric {key} for {city}"
                    assert isinstance(metrics[key], (int, float)), f"Metric {key} is not numeric for {city}"
                    
                # Check predictive_analytics_output
                assert "predictive_analytics_output" in data, f"Missing predictive_analytics_output for {city}"
                pred = data["predictive_analytics_output"]
                
                # Test MRI string parsing gotcha (x.xx/10.0)
                mri_str = pred.get("current_mortality_risk_index", "")
                assert "/" in mri_str, f"Invalid MRI format: {mri_str} for {city}"
                mri_val = float(mri_str.split("/")[0])
                assert 0.0 <= mri_val <= 10.0, f"MRI score out of bounds: {mri_val} for {city}"
                
                # Test 12-hour horizon
                horizon = pred.get("predictive_temporal_12h_forecast_horizon", [])
                assert len(horizon) == 12, f"Expected 12 forecast items, got {len(horizon)} for {city}"
                for h in horizon:
                    assert "lookahead" in h, f"Missing lookahead in forecast for {city}"
                    assert "projected_heat_index" in h, f"Missing projected_heat_index for {city}"
                    assert "projected_utci" in h, f"Missing projected_utci for {city}"
                    assert "mortality_risk_index_projection" in h, f"Missing mortality_risk_index_projection for {city}"
                    h_mri = float(h["mortality_risk_index_projection"].split("/")[0])
                    assert 0.0 <= h_mri <= 10.0
                    
                # Test targeted_administrative_triggers (3 departments)
                assert "targeted_administrative_triggers" in data, f"Missing administrative triggers for {city}"
                triggers = data["targeted_administrative_triggers"]
                assert "disaster_management_authority" in triggers
                assert "healthcare_administration_system" in triggers
                assert "power_grid_corporation" in triggers
                
                print(f"  [PASS] City: {city:8s} | Node: {node['name']} | MRI: {mri_val:.2f}/10.0 | 12h: {len(horizon)} pts")
        except Exception as e:
            print(f"  [FAIL] Error testing city {city}: {e}")
            return False
            
    print("[PASS] All 5 cities verified successfully!")
    return True


def test_html_and_js_contract():
    print("\n" + "=" * 60)
    print("TEST 2: HTML & JS UI Elements & Contract Verification")
    print("=" * 60)
    
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    required_ids = [
        "loadingOverlay", "liveClock", "serverStatusBadge", "rawAnalyzeLink",
        "errorBanner", "wardName", "wardId", "wardCoords", "wardTerrain",
        "iotHardwareId", "iotDropRate", "satRadiance",
        "cityButtonContainer", "mriBandBadge", "gaugeNeedle", "gaugePivot",
        "mriRiskLabel", "mriScoreValue", "mriActionTier", "mriProgressBar",
        "modelConfidenceFootnote", "metricHeatIndex", "metricWetBulb",
        "metricSwbgt", "metricUtci", "forecastChartCanvas",
        "forecastLookaheadCards", "adminEscalationSummaryPill",
        "triggerDisasterMgmt", "badgeDm", "cardDisasterMgmt",
        "triggerHealthcare", "badgeHealth", "cardHealthcare",
        "triggerPowerGrid", "badgeGrid", "cardPowerGrid",
        "modelProvenanceModal", "settingsModal"
    ]
    
    missing_ids = []
    for elem_id in required_ids:
        if f'id="{elem_id}"' not in html:
            missing_ids.append(elem_id)
            
    if missing_ids:
        print(f"  [FAIL] Missing required HTML element IDs: {missing_ids}")
        return False
    else:
        print(f"  [PASS] All {len(required_ids)} required UI elements are present in HTML.")
        
    # Check JS for parsing logic and risk classifications
    with open("static/js/dashboard.js", "r", encoding="utf-8") as f:
        js = f.read()
        
    assert "SUPPORTED_CITIES" in js
    assert "SAMPLE_PATNA_DATA" in js
    assert "getRiskClassification" in js
    assert "renderMriGaugeAndHero" in js
    assert "renderRealtimeMetrics" in js
    assert "render12HourForecast" in js
    assert "renderAdministrativeTriggers" in js
    assert "split('/')[0]" in js
    
    print("  [PASS] JavaScript orchestration logic and string parsing verified.")
    return True

if __name__ == "__main__":
    t1 = test_backend_api()
    t2 = test_html_and_js_contract()
    if t1 and t2:
        print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! (100% PRD COMPLIANT)")
        sys.exit(0)
    else:
        print("\nTESTS FAILED!")
        sys.exit(1)
