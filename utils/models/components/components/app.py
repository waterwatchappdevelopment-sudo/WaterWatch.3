import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Import utilities
from utils.met_eireann import fetch_weather_data, get_weather_description, get_weather_icon
from utils.sensor_data import generate_sensor_data, generate_historical_data
from models.flood_predictor import FloodPredictor
from components.charts import create_water_level_chart, create_historical_chart, create_risk_gauge
from components.map_view import create_sensor_map
from streamlit_folium import st_folium

# Page config
st.set_page_config(
    page_title="WaterWatch - Westmeath Flood Warning",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .risk-low { background: linear-gradient(135deg, #22c55e, #16a34a); padding: 20px; border-radius: 10px; color: white; }
    .risk-moderate { background: linear-gradient(135deg, #f59e0b, #d97706); padding: 20px; border-radius: 10px; color: white; }
    .risk-high { background: linear-gradient(135deg, #f97316, #ea580c); padding: 20px; border-radius: 10px; color: white; }
    .risk-severe { background: linear-gradient(135deg, #ef4444, #dc2626); padding: 20px; border-radius: 10px; color: white; }
    .metric-card { background: #1e293b; padding: 15px; border-radius: 8px; margin: 5px 0; }
    .stMetric { background: #1e293b; padding: 10px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'predictor' not in st.session_state:
    st.session_state.predictor = FloodPredictor()
    st.session_state.historical_data = generate_historical_data(365)
    
    # Try to load or train model
    if not st.session_state.predictor.load():
        accuracy = st.session_state.predictor.train(st.session_state.historical_data)
        st.session_state.model_accuracy = accuracy

if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/water.png", width=80)
    st.title("🌊 WaterWatch")
    st.caption("AI-Powered Flood Warning System")
    st.divider()
    
    st.subheader("📍 Location")
    st.write("County Westmeath, Ireland")
    
    st.subheader("🔄 Auto Refresh")
    auto_refresh = st.toggle("Enable auto-refresh", value=True)
    refresh_interval = st.slider("Interval (seconds)", 30, 300, 60)
    
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    st.divider()
    st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}")
    
    # Model info
    st.divider()
    st.subheader("🤖 ML Model")
    if st.session_state.predictor.is_trained:
        st.success("Model trained ✓")
        if hasattr(st.session_state, 'model_accuracy'):
            st.metric("Training Accuracy", f"{st.session_state.model_accuracy:.1%}")
    else:
        st.warning("Using rule-based fallback")

# Main content
st.title("🌊 WaterWatch Dashboard")
st.caption("Real-time flood monitoring for County Westmeath")

# Fetch data
weather = fetch_weather_data()
sensors = generate_sensor_data()
prediction = st.session_state.predictor.predict(sensors, weather or {})

# Top row - Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    risk_class = f"risk-{prediction['risk_level']}"
    st.markdown(f"""
    <div class="{risk_class}">
        <h3>🎯 Flood Risk</h3>
        <h1>{prediction['risk_level'].upper()}</h1>
        <p>{prediction['probability']}% probability</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if weather:
        icon = get_weather_icon(weather['current']['weather_code'])
        st.metric(
            f"{icon} Temperature",
            f"{weather['current']['temperature']}°C",
            f"Humidity: {weather['current']['humidity']}%"
        )
    else:
        st.metric("🌡️ Temperature", "N/A")

with col3:
    if weather:
        st.metric(
            "🌧️ Current Rainfall",
            f"{weather['current']['precipitation']} mm",
            f"Wind: {weather['current']['wind_speed']} km/h"
        )

with col4:
    critical_count = len([s for s in sensors if s['status'] == 'critical'])
    warning_count = len([s for s in sensors if s['status'] == 'warning'])
    st.metric(
        "⚠️ Alerts",
        f"{critical_count} Critical",
        f"{warning_count} Warnings"
    )

st.divider()

# Main dashboard
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🗺️ Map", "📈 Historical", "🔬 ML Analysis"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Water Levels")
        fig = create_water_level_chart(sensors)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Risk Gauge")
        gauge = create_risk_gauge(prediction['probability'])
        st.plotly_chart(gauge, use_container_width=True)
        
        st.subheader("Contributing Factors")
        for factor in prediction['contributing_factors']:
            st.write(f"• {factor}")
    
    # Sensor grid
    st.subheader("Sensor Status")
    sensor_cols = st.columns(4)
    
    for i, sensor in enumerate(sensors):
        with sensor_cols[i % 4]:
            status_emoji = {"normal": "🟢", "warning": "🟡", "critical": "🔴"}
            trend_emoji = {"rising": "↗️", "stable": "→", "falling": "↘️"}
            
            st.markdown(f"""
            **{sensor['name']}**  
            {status_emoji.get(sensor['status'], '⚪')} {sensor['value']} {sensor['unit']}  
            {trend_emoji.get(sensor['trend'], '')} {sensor['trend']}
            """)

with tab2:
    st.subheader("Sensor Locations")
    sensor_map = create_sensor_map(sensors)
    st_folium(sensor_map, width=None, height=500)
    
    # Legend
    col1, col2, col3 = st.columns(3)
    col1.markdown("🟢 **Normal** - Within safe limits")
    col2.markdown("🟡 **Warning** - Elevated levels")
    col3.markdown("🔴 **Critical** - Immediate attention")

with tab3:
    st.subheader("Historical Analysis")
    
    days = st.selectbox("Time Range", [7, 30, 90, 365], index=1)
    hist_data = st.session_state.historical_data.tail(days)
    
    fig = create_historical_chart(hist_data)
    st.plotly_chart(fig, use_container_width=True)
    
    # Stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Rainfall", f"{hist_data['rainfall_mm'].mean():.1f} mm")
    col2.metric("Max Water Level", f"{hist_data['water_level_m'].max():.2f} m")
    col3.metric("Flood Events", hist_data['flood_event'].sum())

with tab4:
    st.subheader("ML Model Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Model Type:** Random Forest Classifier")
        st.write("**Features:**")
        st.write("- Current rainfall (mm)")
        st.write("- Water level (m)")
        st.write("- Soil moisture (%)")
        st.write("- 3-day rainfall accumulation")
        st.write("- 7-day rainfall accumulation")
        st.write("- Water level trend")
        
    with col2:
        st.write("**Current Prediction:**")
        st.json(prediction)
        
    # Feature importance (if model is trained)
    if st.session_state.predictor.is_trained:
        st.subheader("Feature Importance")
        importances = st.session_state.predictor.model.feature_importances_
        features = ['Rainfall', 'Water Level', 'Soil Moisture', '3-Day Rain', '7-Day Rain', 'Level Trend']
        
        import plotly.express as px
        fig = px.bar(x=features, y=importances, title="Feature Importance")
        st.plotly_chart(fig, use_container_width=True)

# 5-Day Forecast
if weather:
    st.divider()
    st.subheader("🌤️ 5-Day Weather Forecast")
    
    forecast_cols = st.columns(5)
    for i, day in enumerate(weather['forecast'][:5]):
        with forecast_cols[i]:
            icon = get_weather_icon(day['weather_code'])
            date = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%a %d')
            st.markdown(f"""
            **{date}**  
            {icon} {get_weather_description(day['weather_code'])}  
            🌡️ {day['temp_max']}° / {day['temp_min']}°  
            🌧️ {day['precipitation']} mm
            """)

# Auto refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
