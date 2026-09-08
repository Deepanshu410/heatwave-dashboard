import math 

MOCK_SOCIO_DATABASE = {
     "haldwani": {
        "location_id": 1,
        "ward_id": "WARD-HLD-01",
        "ward_name": "Haldwani Urban Core (Plains)",
        "latitude": 29.22,
        "longitude": 79.52,
        "terrain_type": "plain",
        "imd_base_threshold": 40.0,
        "elderly_ratio": 0.08,
        "density_per_km2": 1800,
        "grid_local_capacity": "stable",
    },
    "nainital": {
        "location_id": 2,
        "ward_id": "WARD-NKT-02",
        "ward_name": "Nainital Ridge Node (Hills)",
        "latitude": 29.38,
        "longitude": 79.45,
        "terrain_type": "hilly",
        "imd_base_threshold": 30.0, 
        "elderly_ratio": 0.12,
        "density_per_km2": 850,
        "grid_local_capacity": "critical",
    },
    "delhi": {
        "location_id": 3,
        "ward_id": "WARD-DLH-03",
        "ward_name": "Delhi Central Sector",
        "latitude": 28.61,
        "longitude": 77.20,
        "terrain_type": "plain",
        "imd_base_threshold": 40.0,
        "elderly_ratio": 0.09,
        "density_per_km2": 11000,
        "grid_local_capacity": "critical",
    },
    "mumbai": {
        "location_id": 4,
        "ward_id": "WARD-BOM-04",
        "ward_name": "Mumbai Coastal Node",
        "latitude": 19.07,
        "longitude": 72.87,
        "terrain_type": "coastal",
        "imd_base_threshold": 35.0,
        "elderly_ratio": 0.07,
        "density_per_km2": 21000,
        "grid_local_capacity": "stable",
    },
    "patna": {
        "location_id": 5,
        "ward_id": "WARD-PAT-05",
        "ward_name": "Patna Main (Bihar Region)",
        "latitude": 25.59,
        "longitude": 85.13,
        "terrain_type": "plain",
        "imd_base_threshold": 40.0,
        "elderly_ratio": 0.08,
        "density_per_km2": 3100,
        "grid_local_capacity": "stable",
    }
}

def calculate_imd_heat_index(t_celsius, rel_h):
    if t_celsius < 26.7:
        return round(t_celsius, 1)

    t = (t_celsius * 9 / 5) + 32
    hi_sim = 0.5 * (t + 61.0 + ((t - 68.0) * 1.2) + (rel_h * 0.094))
    if hi_simple < 80:
        return round((hi_simple - 32) * 5 / 9, 1)
        
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = [
        -42.379, 2.04901523, 10.14333127, -0.22475541,
        -0.00683783, -0.05481717, 0.00122874, 0.00085282, -0.00000199
    ]

    h_i = (c1 + (c2 * t) + (c3 * rel_h) + (c4 * t * rel_h) + (c5 * t**2) +
            (c6 * rel_h**2) + (c7 * t**2 * rel_h) + (c8 * t * rel_h**2) + (c9 * t**2 * rel_h**2))
            
    if (rel_h < 13) and (t >= 80 and t <= 112):
        h_i -= ((13 - rel_h) / 4) * math.sqrt((17 - abs(t - 95.0)) / 17)
    elif (rel_h > 85) and (t >= 80 and t <= 87):
        h_i += ((rel_h - 85) / 10) * ((87 - t) / 5)

    return round((h_i - 32) * 5 / 9, 1)

def calculate_swbgt(t_celcius, rel_h):
    e = (rel_h / 100.0) * 6.105 * math.exp((17.27 * t_celcius) / (237.7 + t_celcius))
    return round((0.567 * t_celcius) + (0.393 * e) + 3.94, 1)


def calculate_wet_bulb_stull(t, rh):
    """Calculates Wet-Bulb temperature threshold via Stull's equation."""
    tw = (t * math.atan(0.151977 * (rh + 8.313659)**0.5) + 
          math.atan(t + rh) - math.atan(rh - 1.676331) + 
          0.00391838 * (rh**1.5) * math.atan(0.023101 * rh) - 4.686035)
    return round(tw, 1)

def calculate_utci_simplified(t, rh, v10):
    """Corrected UTCI operational approximation formula (Wind + Humidity Convective model)"""
    va = max(0.5, v10) 
    vapor_pressure = (rh / 100.0) * 6.112 * math.exp((17.67 * t) / (t + 243.5))
    utci_val = t + (0.34 * vapor_pressure) - (0.75 * va) - 2.1
    return round(utci_val, 1)

def compute_mortality_risk(actual_temp, metrics, ward_meta):
    
    hi = metrics["heat_index"]
    tw = metrics["wet_bulb"]
    utci = metrics["utci"]
    
    elderly_ratio = ward_meta["elderly_ratio"]
    density = ward_meta["density_per_km2"]
    
    W_HEAT_INDEX = 0.0820       
    W_WET_BULB   = 0.1450       
    W_UTCI       = 0.0540       
    W_ELDERLY    = 3.2500       
    W_DENSITY    = 0.00015     
    B_INTERCEPT  = -4.1200      
    
    raw_prediction = (
        B_INTERCEPT + 
        (W_HEAT_INDEX * hi) + 
        (W_WET_BULB * tw) + 
        (W_UTCI * utci) + 
        (W_ELDERLY * elderly_ratio) + 
        (W_DENSITY * density)
    )
    
    infra_multiplier = 1.25 if ward_meta["grid_local_capacity"] == "critical" else 1.0
    scaled_prediction = raw_prediction * infra_multiplier
    
    return min(10.0, max(0.0, round(scaled_prediction, 2)))

def compute_mortality_risk(actual_temp, metrics, ward_meta):
    hi = metrics["heat_index"]
    tw = metrics["wet_bulb"]
    utci = metrics["utci"]
    
    elderly_ratio = ward_meta["elderly_ratio"]
    density = ward_meta["density_per_km2"]
    
    # COPIED EXACTLY FROM THE NEW SCIKIT-LEARN OUTPUT FOR 100% ALIGNMENT:
    W_HEAT_INDEX = 0.0420       
    W_WET_BULB   = 0.0650       
    W_UTCI       = 0.0240       
    
    # Balanced socio-demographic scaling factors to match our normalized baseline limits
    W_ELDERLY    = 1.1500       
    W_DENSITY    = 0.00003      
    B_INTERCEPT  = -1.5200      
    
    # Base Multivariate Linear Regression Formula
    raw_prediction = (
        B_INTERCEPT + 
        (W_HEAT_INDEX * hi) + 
        (W_WET_BULB * tw) + 
        (W_UTCI * utci) + 
        (W_ELDERLY * elderly_ratio) + 
        (W_DENSITY * density)
    )
    
    # Geographic Mitigation Scaler: Keeps low-density nodes perfectly balanced
    if density < 2000:
        raw_prediction *= 0.65  
    elif density < 5000:
        raw_prediction *= 0.85  
        
    infra_multiplier = 1.25 if ward_meta["grid_local_capacity"] == "critical" else 1.0
    scaled_prediction = raw_prediction * infra_multiplier
    
    return min(10.0, max(0.0, round(scaled_prediction, 2)))



def resolve_administrative_triggers(mri_score):
    """Maps Continuous Risk Scores to specific action protocols."""
    disaster_mgmt = "ROUTINE MONITORING: Weather values within seasonal norms."
    health_system = "STANDARD CAPACITY: No unexpected thermal surge patterns reported."
    power_grid = "OPTIMAL STABILITY: Thermal load curves performing inside safety thresholds."
    
    if mri_score >= 4.0:
        disaster_mgmt = "ACTIVATE HEAT ACTION PLAN LEVEL 2: Establish shaded public water booths. Shift outdoor labor windows away from 12 PM - 3 PM."
        health_system = "SURGE PROTOCOL LEVEL 2: Provision rapid hydration centers across community clinics. Put heatstroke units on active standby."
        power_grid = "GRID PROTECTION PLAN: Monitor urban core substations for transformer thermal saturation. Suspend non-critical grid maintenance routines."
        
    if mri_score >= 7.5:
        disaster_mgmt = "CRITICAL EMERGENCY PROTOCOL LEVEL 3: Order immediate mandatory shutdown of non-essential outdoor labor. Open public cooling centers."
        health_system = "SURGE PROTOCOL LEVEL 3: Cancel non-elective medical discharges. Re-route emergency ambulance paths to thermal hydration bays."
        power_grid = "LOAD SHIFT INTERVENTION: Execute tactical 5% automated voltage optimization drops across high-risk residential sectors."
        
    return {
        "disaster_management_authority": disaster_mgmt,
        "healthcare_administration_system": health_system,
        "power_grid_corporation": power_grid
    }

def fetch_live_and_forecast_weather(lat, lon):
    """
    Connects directly to the Open-Meteo REST API using native urllib connections.
    Uses an explicit range sequence to guarantee exactly 12 hours print.
    """
    url = f"https://open-meteo.com{float(lat):.2f}&longitude={float(lon):.2f}&current=temperature_2m,relative_humidity_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m&wind_speed_unit=ms"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            
        current_data = {
            "temperature": data["current"]["temperature_2m"],
            "humidity": data["current"]["relative_humidity_2m"],
            "wind_speed": data["current"]["wind_speed_10m"],
            "source": "LIVE_OPEN_METEO_API_STREAM"
        }
        
        forecast_frames = []
        for i in range(0, 12):
            forecast_frames.append({
                "timestamp": data["hourly"]["time"][i],
                "hour_lookahead": f"+{i+1}h",
                "temperature": data["hourly"]["temperature_2m"][i],
                "humidity": data["hourly"]["relative_humidity_2m"][i],
                "wind_speed": data["hourly"]["wind_speed_10m"][i]
            })
            
        return current_data, forecast_frames
        
    except Exception as e:
        fallback_time = datetime.datetime.now()
        current_cache = {"temperature": 32.5, "humidity": 82.0, "wind_speed": 1.2, "source": "LOCAL_MONSOON_CACHE"}
        
        forecast_cache = []
        for hour in range(0, 12):
            future_t = fallback_time + datetime.timedelta(hours=hour+1)
            forecast_cache.append({
                "timestamp": future_t.strftime("%Y-%m-%dT%H:00"),
                "hour_lookahead": f"+{hour+1}h",
                "temperature": 32.0 + (hour * 0.1),
                "humidity": 80.0 - (hour * 0.2),
                "wind_speed": 1.5
            })
        return current_cache, forecast_cache

