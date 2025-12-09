import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
from pathlib import Path

class FloodPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = Path("models/trained_model.pkl")
        
    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features from dataframe"""
        features = df[['rainfall_mm', 'water_level_m', 'soil_moisture_pct']].copy()
        
        # Add rolling features if enough data
        if len(df) > 3:
            features['rainfall_3d'] = df['rainfall_mm'].rolling(3, min_periods=1).sum()
            features['rainfall_7d'] = df['rainfall_mm'].rolling(7, min_periods=1).sum()
            features['water_level_trend'] = df['water_level_m'].diff().fillna(0)
        else:
            features['rainfall_3d'] = df['rainfall_mm']
            features['rainfall_7d'] = df['rainfall_mm']
            features['water_level_trend'] = 0
            
        return features.fillna(0).values
    
    def train(self, df: pd.DataFrame):
        """Train the model on historical data"""
        X = self.prepare_features(df)
        y = df['flood_event'].values
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Save model
        self.model_path.parent.mkdir(exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler
            }, f)
            
        return self.model.score(X_scaled, y)
    
    def load(self):
        """Load trained model"""
        if self.model_path.exists():
            with open(self.model_path, 'rb') as f:
                saved = pickle.load(f)
                self.model = saved['model']
                self.scaler = saved['scaler']
                self.is_trained = True
                return True
        return False
    
    def predict(self, sensors: list, weather: dict) -> dict:
        """Predict flood risk from current conditions"""
        if not self.is_trained:
            return self._rule_based_prediction(sensors, weather)
        
        # Extract current values
        water_levels = [s['value'] for s in sensors if s['type'] == 'water_level']
        rainfall = [s['value'] for s in sensors if s['type'] == 'rainfall']
        soil = [s['value'] for s in sensors if s['type'] == 'soil_moisture']
        
        current = {
            'rainfall_mm': np.mean(rainfall) if rainfall else 0,
            'water_level_m': np.mean(water_levels) if water_levels else 1.5,
            'soil_moisture_pct': np.mean(soil) if soil else 50
        }
        
        # Add forecast rainfall
        forecast_rain = sum(f['precipitation'] for f in weather.get('forecast', [])[:3])
        
        df = pd.DataFrame([{
            **current,
            'rainfall_3d': current['rainfall_mm'] * 24 + forecast_rain,
            'rainfall_7d': current['rainfall_mm'] * 24 * 3 + forecast_rain * 2,
            'water_level_trend': 0.1 if current['rainfall_mm'] > 5 else 0
        }])
        
        X = df.values
        X_scaled = self.scaler.transform(X)
        
        probability = self.model.predict_proba(X_scaled)[0][1]
        
        # Determine risk level
        if probability > 0.7:
            risk_level = "severe"
        elif probability > 0.5:
            risk_level = "high"
        elif probability > 0.3:
            risk_level = "moderate"
        else:
            risk_level = "low"
            
        # Feature importance for contributing factors
        factors = []
        importances = self.model.feature_importances_
        feature_names = ['Rainfall', 'Water Level', 'Soil Moisture', '3-Day Rain', '7-Day Rain', 'Level Trend']
        
        for name, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1])[:3]:
            if imp > 0.1:
                factors.append(name)
        
        return {
            "risk_level": risk_level,
            "probability": round(probability * 100, 1),
            "contributing_factors": factors,
            "confidence": round(np.mean(importances) * 100, 1),
            "model_type": "Random Forest ML"
        }
    
    def _rule_based_prediction(self, sensors: list, weather: dict) -> dict:
        """Fallback rule-based prediction"""
        water_levels = [s['value'] for s in sensors if s['type'] == 'water_level']
        rainfall = [s['value'] for s in sensors if s['type'] == 'rainfall']
        soil = [s['value'] for s in sensors if s['type'] == 'soil_moisture']
        
        avg_water = np.mean(water_levels) if water_levels else 1.5
        avg_rain = np.mean(rainfall) if rainfall else 0
        avg_soil = np.mean(soil) if soil else 50
        
        # Simple weighted score
        score = (
            (avg_water / 4.0) * 0.4 +
            (avg_rain / 20.0) * 0.35 +
            (avg_soil / 100.0) * 0.25
        )
        
        if score > 0.7:
            risk_level = "severe"
        elif score > 0.5:
            risk_level = "high"
        elif score > 0.3:
            risk_level = "moderate"
        else:
            risk_level = "low"
            
        return {
            "risk_level": risk_level,
            "probability": round(score * 100, 1),
            "contributing_factors": ["Water Level", "Rainfall"],
            "confidence": 65,
            "model_type": "Rule-based (no trained model)"
        }
