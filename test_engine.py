"""
Unit Test Suite for Physics Formulations, Composite HTSI, Driving Factor Attribution,
Targeted Organization Alerts, and Empirical Model Metrics
"""

import os
import json
import sys
from config import CITIES_DB, DEFAULT_CITY_ID, ADMINISTRATIVE_ALERTS, RISK_TIERS
from engine.thermal_engine import (
    adapt_humidity,
    calculate_heat_index,
    calculate_vapor_pressure,
    calculate_swbgt,
    calculate_wet_bulb_stull,
    calculate_utci_simplified,
    calculate_thermal_mortality_risk_score,
    get_risk_tier,
    explain_driving_factors
)
from engine.alert_rules import evaluate_city_alerts


def test_monsoon_adaptive_filter():
    print("[TEST 1/8] Testing Monsoon Adaptive Humidity Filter...")
    # Qualifying conditions: 30 <= T <= 35, RH > 80%, wind > 2.0 m/s
    res_active = adapt_humidity(temp_c=33.0, rh_pct=88.0, wind_speed_ms=4.0)
    assert res_active['is_active'] is True, "Monsoon filter should be active"
    assert res_active['reduction_pct'] == 10.0, f"Expected 10.0 reduction, got {res_active['reduction_pct']}"
    assert res_active['effective_rh'] == 78.0, f"Expected 78.0 effective RH, got {res_active['effective_rh']}"

    # Capped reduction at 15.0%
    res_capped = adapt_humidity(temp_c=32.0, rh_pct=90.0, wind_speed_ms=10.0)
    assert res_capped['reduction_pct'] == 15.0, "Reduction should cap at 15.0%"
    assert res_capped['effective_rh'] == 75.0

    # Outside qualifying range: Temp = 38 C
    res_inactive = adapt_humidity(temp_c=38.0, rh_pct=85.0, wind_speed_ms=4.0)
    assert res_inactive['is_active'] is False
    assert res_inactive['effective_rh'] == 85.0
    print("  [PASS] Monsoon Adaptive Humidity Filter verified.")


def test_heat_index():
    print("[TEST 2/8] Testing NOAA Heat Index...")
    # Low temperature below 26.7 C: equals raw temperature
    hi_low = calculate_heat_index(temp_c=22.0, rh_pct=60.0)
    assert hi_low['heat_index_c'] == 22.0, f"Expected 22.0, got {hi_low['heat_index_c']}"
    assert 'Raw Temperature' in hi_low['method']

    # Extreme hot condition (42 C, 40% RH)
    hi_hot = calculate_heat_index(temp_c=42.0, rh_pct=40.0)
    assert hi_hot['heat_index_c'] > 50.0, "Heat index should be elevated above 50C"
    assert hi_hot['category'] in ['Danger', 'Extreme Danger']
    print(f"  [PASS] Heat Index: 42C @ 40% RH -> {hi_hot['heat_index_c']}C ({hi_hot['category']})")


def test_swbgt_and_vapor_pressure():
    print("[TEST 3/8] Testing Simplified WBGT & Vapor Pressure...")
    e = calculate_vapor_pressure(temp_c=35.0, rh_pct=60.0)
    assert 30.0 <= e <= 40.0, f"Expected vapor pressure between 30 and 40 hPa, got {e}"

    swbgt = calculate_swbgt(temp_c=35.0, unadjusted_rh_pct=60.0)
    expected = round(0.567 * 35.0 + 0.393 * e + 3.94, 2)
    assert abs(swbgt - expected) < 0.05, f"Expected {expected}, got {swbgt}"
    print(f"  [PASS] Simplified WBGT: Vapor Pressure={e} hPa, SWBGT={swbgt}C")


def test_stull_wet_bulb():
    print("[TEST 4/8] Testing Stull Empirical Wet-Bulb...")
    tw = calculate_wet_bulb_stull(temp_c=30.0, rh_pct=50.0)
    assert 20.0 <= tw <= 24.0, f"Expected Tw around 22C, got {tw}"
    print(f"  [PASS] Stull Wet-Bulb: Temp=30C, RH=50% -> Tw={tw}C")


def test_utci_simplified():
    print("[TEST 5/8] Testing Simplified UTCI...")
    utci_calm = calculate_utci_simplified(temp_c=36.0, rh_pct=50.0, wind_speed_ms=0.2)
    utci_windy = calculate_utci_simplified(temp_c=36.0, rh_pct=50.0, wind_speed_ms=4.0)
    assert utci_windy < utci_calm, "Wind cooling must reduce UTCI"
    print(f"  [PASS] Simplified UTCI: Calm={utci_calm}C, Windy={utci_windy}C")


def test_thermal_mortality_risk_score():
    print("[TEST 6/8] Testing 0-10 Thermal / Mortality Risk Score (HTSI)...")
    delhi_meta = CITIES_DB['delhi']

    # Extreme summer heat conditions in Delhi
    score_delhi = calculate_thermal_mortality_risk_score(
        temp_c=44.0,
        effective_rh=45.0,
        unadjusted_rh=45.0,
        wind_speed_ms=1.5,
        location_meta=delhi_meta
    )
    assert 5.5 <= score_delhi['risk_score'] <= 10.0, f"Expected high risk in Delhi summer, got {score_delhi['risk_score']}"
    assert score_delhi['risk_tier'] in ['Danger', 'Extreme Danger']

    # Comfortable cool day
    score_mild = calculate_thermal_mortality_risk_score(
        temp_c=22.0,
        effective_rh=50.0,
        unadjusted_rh=50.0,
        wind_speed_ms=3.0,
        location_meta=delhi_meta
    )
    assert score_mild['risk_score'] < 3.5, f"Expected safe score on cool day, got {score_mild['risk_score']}"
    assert score_mild['risk_tier'] == 'Safe'
    print(f"  [PASS] HTSI Score: Delhi Hot={score_delhi['risk_score']} ({score_delhi['risk_tier']}), Mild={score_mild['risk_score']} ({score_mild['risk_tier']})")


def test_driving_factor_attribution():
    print("[TEST 7/8] Testing 'Why' Driving Factor Explanation...")
    # Extreme temperature case
    why_temp = explain_driving_factors(
        temp_c=43.0,
        rh_pct=25.0,
        wind_speed_ms=2.0,
        hi_c=48.0,
        tw_c=24.0,
        utci_c=44.0,
        risk_score=7.8
    )
    assert "Temperature" in why_temp['primary_driving_factor']
    assert len(why_temp['plain_language_explanation']) > 20

    # High humidity case
    why_humid = explain_driving_factors(
        temp_c=34.0,
        rh_pct=75.0,
        wind_speed_ms=2.0,
        hi_c=47.0,
        tw_c=29.0,
        utci_c=43.0,
        risk_score=6.8
    )
    assert "Humidity" in why_humid['primary_driving_factor']
    assert "sweat" in why_humid['plain_language_explanation'].lower()

    print(f"  [PASS] Factor Attribution: Dry Heat Driver='{why_temp['primary_driving_factor']}'")
    print(f"         Humid Heat Driver='{why_humid['primary_driving_factor']}'")


def test_targeted_organization_alerts_and_model():
    print("[TEST 8/8] Testing Targeted Organization Alerts & Real Model Parameters...")
    alerts = evaluate_city_alerts(
        city_id='delhi',
        current_temp=42.0,
        htsi_score=7.8,
        risk_tier='Danger',
        driving_factor='Extreme Air Temperature'
    )
    assert len(alerts) == 4, f"Expected 4 org alerts, got {len(alerts)}"
    org_types = [a['org_type'] for a in alerts]
    assert 'hospital' in org_types
    assert 'disaster_mgmt' in org_types
    assert 'outdoor_employer' in org_types
    assert 'citizen' in org_types

    # Check model JSON metadata
    json_path = os.path.join(os.path.dirname(__file__), 'delhi_climate_model.json')
    assert os.path.exists(json_path), "delhi_climate_model.json must exist"
    with open(json_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    assert meta['records_count'] == 1576, f"Expected 1576 records, got {meta.get('records_count')}"
    assert meta['r2_score'] >= 0.99, f"Expected R2 >= 0.99, got {meta.get('r2_score')}"
    print(f"  [PASS] Model Verification: 1,576 rows, Real R²={meta['r2_score']}, Real MSE={meta['mse']}")
    print("  [PASS] Targeted Organization Alerts generated successfully.")


if __name__ == '__main__':
    print("================================================================")
    print("   EXTREME HEATWAVE PLATFORM - CORE ENGINE & PHYSICS TESTS     ")
    print("================================================================")
    test_monsoon_adaptive_filter()
    test_heat_index()
    test_swbgt_and_vapor_pressure()
    test_stull_wet_bulb()
    test_utci_simplified()
    test_thermal_mortality_risk_score()
    test_driving_factor_attribution()
    test_targeted_organization_alerts_and_model()
    print("================================================================")
    print("   ALL ENGINE & FORMULA TESTS PASSED (8/8)                      ")
    print("================================================================")
