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
