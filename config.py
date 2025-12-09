# Westmeath coordinates
WESTMEATH_LAT = 53.5259
WESTMEATH_LON = -7.3389

# Station locations
STATIONS = {
    "water_level": [
        {"id": "WL001", "name": "Athlone Bridge", "lat": 53.4239, "lon": -7.9407, "river": "Shannon"},
        {"id": "WL002", "name": "Mullingar Town", "lat": 53.5259, "lon": -7.3389, "river": "Brosna"},
        {"id": "WL003", "name": "Moate Station", "lat": 53.4567, "lon": -7.7182, "river": "Brosna"},
        {"id": "WL004", "name": "Kilbeggan Bridge", "lat": 53.3694, "lon": -7.5000, "river": "Brosna"},
    ],
    "rainfall": [
        {"id": "RF001", "name": "Mullingar Met", "lat": 53.5350, "lon": -7.3620},
        {"id": "RF002", "name": "Athlone AWS", "lat": 53.4300, "lon": -7.9200},
        {"id": "RF003", "name": "Lough Ennell", "lat": 53.4800, "lon": -7.3900},
    ],
    "soil_moisture": [
        {"id": "SM001", "name": "Belvedere Farm", "lat": 53.4850, "lon": -7.3750},
        {"id": "SM002", "name": "Tullynally Estate", "lat": 53.6100, "lon": -7.2400},
    ]
}

# Risk thresholds
WATER_LEVEL_WARNING = 2.5  # meters
WATER_LEVEL_FLOOD = 3.5    # meters
RAINFALL_HIGH = 15.0        # mm/day
