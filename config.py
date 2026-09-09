"""
Configuration and Socio-Demographic Database for Extreme Heatwave Early Warning Platform
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODELS_DIR, 'heatwave_model.joblib')
DEFAULT_CITY_ID = 'haldwani'

# Canonical Mock Socio-Demographic Database as specified by the system architecture
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
        "state": "Uttarakhand",
        "name": "Haldwani"
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
        "state": "Uttarakhand",
        "name": "Nainital"
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
        "state": "Delhi NCR",
        "name": "New Delhi"
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
        "state": "Maharashtra",
        "name": "Mumbai"
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
        "state": "Bihar",
        "name": "Patna"
    }
}

# Compatibility alias
CITIES_DB = {}
for k, v in MOCK_SOCIO_DATABASE.items():
    CITIES_DB[k] = {
        'id': k,
        'name': v['ward_name'],
        'state': v.get('state', ''),
        'lat': v['latitude'],
        'lon': v['longitude'],
        'terrain': v['terrain_type'],
        'base_threshold': v['imd_base_threshold'],
        'normal_max_temp': v['imd_base_threshold'],
        'elderly_ratio': v['elderly_ratio'],
        'population_density': v['density_per_km2'],
        'grid_status': v['grid_local_capacity'],
        'population': v['density_per_km2'] * 200,
        'ward_id': v['ward_id'],
        'location_id': v['location_id']
    }

# Plain-Language Risk Tiers
RISK_TIERS = {
    'SAFE': {
        'min': 0.0,
        'max': 3.5,
        'label': 'Safe',
        'color': '#10b981',
        'alert_tier': 'Routine',
        'badge': 'safe',
        'description': 'Minimal thermal risk. Conditions within comfortable seasonal range.'
    },
    'CAUTION': {
        'min': 3.5,
        'max': 6.0,
        'label': 'Caution',
        'color': '#f59e0b',
        'alert_tier': 'Elevated',
        'badge': 'caution',
        'description': 'Elevated thermal stress. Fatigue possible with prolonged outdoor exposure.'
    },
    'DANGER': {
        'min': 6.0,
        'max': 8.0,
        'label': 'Danger',
        'color': '#f97316',
        'alert_tier': 'High',
        'badge': 'danger',
        'description': 'Dangerous thermal conditions. Heat cramps, exhaustion likely.'
    },
    'EXTREME_DANGER': {
        'min': 8.0,
        'max': 10.0,
        'label': 'Extreme Danger',
        'color': '#ef4444',
        'alert_tier': 'Critical',
        'badge': 'extreme',
        'description': 'Life-threatening thermal stress. Immediate health emergency.'
    }
}

IMD_THRESHOLDS = {
    'plain': {'normal_threshold': 40.0, 'heatwave_departure': 4.5, 'severe_departure': 6.4, 'absolute_heatwave': 45.0, 'absolute_severe': 47.0},
    'coastal': {'normal_threshold': 37.0, 'heatwave_departure': 4.5, 'severe_departure': 6.4, 'absolute_heatwave': 40.0, 'absolute_severe': 42.0},
    'hilly': {'normal_threshold': 30.0, 'heatwave_departure': 4.5, 'severe_departure': 6.4, 'absolute_heatwave': 35.0, 'absolute_severe': 38.0}
}

ADMINISTRATIVE_ALERTS = {
    'routine': {
        'tier': 'Routine',
        'score_range': '< 4.0',
        'color': '#10b981',
        'disaster_management': 'ROUTINE MONITORING: Weather values within seasonal norms.',
        'healthcare': 'STANDARD CAPACITY: No unexpected thermal surge patterns reported.',
        'power_grid': 'OPTIMAL STABILITY: Thermal load curves performing inside safety thresholds.'
    },
    'elevated': {
        'tier': 'Level 2 Elevated',
        'score_range': '4.0 – 7.4',
        'color': '#f59e0b',
        'disaster_management': 'ACTIVATE HEAT ACTION PLAN LEVEL 2: Establish shaded public water booths. Shift outdoor labor windows away from 12 PM - 3 PM.',
        'healthcare': 'SURGE PROTOCOL LEVEL 2: Provision rapid hydration centers across community clinics. Put heatstroke units on active standby.',
        'power_grid': 'GRID PROTECTION PLAN: Monitor urban core substations for transformer thermal saturation. Suspend non-critical grid maintenance routines.'
    },
    'critical': {
        'tier': 'Level 3 Critical',
        'score_range': '≥ 7.5',
        'color': '#ef4444',
        'disaster_management': 'CRITICAL EMERGENCY PROTOCOL LEVEL 3: Order immediate mandatory shutdown of non-essential outdoor labor. Open public cooling centers.',
        'healthcare': 'SURGE PROTOCOL LEVEL 3: Cancel non-elective medical discharges. Re-route emergency ambulance paths to thermal hydration bays.',
        'power_grid': 'LOAD SHIFT INTERVENTION: Execute tactical 5% automated voltage optimization drops across high-risk residential sectors.'
    }
}

