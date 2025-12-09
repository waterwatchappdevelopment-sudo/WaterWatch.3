import numpy as np
from datetime import datetime, timedelta
from config import STATIONS

def generate_sensor_data():
    """Generate simulated sensor data based on seasonal patterns"""
    now = datetime.now()
    month = now.month
    hour = now.hour
    
    # Seasonal adjustments (winter = higher water, more rain)
    seasonal_factor = 1.0 + 0.3 * np.sin((month - 4) * np.pi / 6)
    
    sensors = []
    
    # Water level sensors
    for station in STATIONS["water_level"]:
        base_level = np.random.uniform(1.2, 2.0)
        level = base_level * seasonal_factor + np.random.uniform(-0.2, 0.3)
        
        if level > 3.0:
            status = "critical"
        elif level > 2.5:
            status = "warning"
        else:
            status = "normal"
            
        sensors.append({
            "id": station["id"],
            "name": station["name"],
            "type": "water_level",
            "value": round(level, 2),
            "unit": "m",
            "status": status,
            "lat": station["lat"],
            "lon": station["lon"],
            "river": station.get("river", ""),
            "trend": np.random.choice(["rising", "stable", "falling"])
        })
    
    # Rainfall sensors
    for station in STATIONS["rainfall"]:
        rainfall = np.random.uniform(0, 8) * seasonal_factor
        
        if rainfall > 15:
            status = "critical"
        elif rainfall > 8:
            status = "warning"
        else:
            status = "normal"
            
        sensors.append({
            "id": station["id"],
            "name": station["name"],
            "type": "rainfall",
            "value": round(rainfall, 1),
            "unit": "mm/hr",
            "status": status,
            "lat": station["lat"],
            "lon": station["lon"],
            "trend": np.random.choice(["rising", "stable", "falling"])
        })
    
    # Soil moisture sensors
    for station in STATIONS["soil_moisture"]:
        moisture = np.random.uniform(50, 85) * (0.8 + 0.2 * seasonal_factor)
        moisture = min(100, moisture)
        
        if moisture > 90:
            status = "critical"
        elif moisture > 75:
            status = "warning"
        else:
            status = "normal"
            
        sensors.append({
            "id": station["id"],
            "name": station["name"],
            "type": "soil_moisture",
            "value": round(moisture, 1),
            "unit": "%",
            "status": status,
            "lat": station["lat"],
            "lon": station["lon"],
            "trend": np.random.choice(["rising", "stable", "falling"])
        })
    
    return sensors

def generate_historical_data(days: int = 365):
    """Generate historical data for ML training"""
    import pandas as pd
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    data = []
    
    for date in dates:
        month = date.month
        seasonal = 1.0 + 0.3 * np.sin((month - 4) * np.pi / 6)
        
        rainfall = max(0, np.random.normal(5, 8) * seasonal)
        water_level = 1.5 + rainfall * 0.08 + np.random.normal(0, 0.3)
        soil_moisture = 50 + rainfall * 2 + np.random.normal(0, 10)
        soil_moisture = np.clip(soil_moisture, 20, 100)
        
        # Flood events (more likely with high rainfall)
        flood_prob = min(0.8, rainfall / 30)
        flood_event = 1 if np.random.random() < flood_prob and rainfall > 20 else 0
        
        data.append({
            "date": date,
            "rainfall_mm": round(rainfall, 1),
            "water_level_m": round(water_level, 2),
            "soil_moisture_pct": round(soil_moisture, 1),
            "flood_event": flood_event
        })
    
    return pd.DataFrame(data)
