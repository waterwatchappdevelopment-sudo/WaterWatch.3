import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_water_level_chart(sensors: list):
    """Create water level bar chart"""
    water_sensors = [s for s in sensors if s['type'] == 'water_level']
    
    fig = go.Figure()
    
    colors = []
    for s in water_sensors:
        if s['status'] == 'critical':
            colors.append('#ef4444')
        elif s['status'] == 'warning':
            colors.append('#f59e0b')
        else:
            colors.append('#22c55e')
    
    fig.add_trace(go.Bar(
        x=[s['name'] for s in water_sensors],
        y=[s['value'] for s in water_sensors],
        marker_color=colors,
        text=[f"{s['value']}m" for s in water_sensors],
        textposition='outside'
    ))
    
    # Add warning and flood lines
    fig.add_hline(y=2.5, line_dash="dash", line_color="orange", 
                  annotation_text="Warning Level")
    fig.add_hline(y=3.5, line_dash="dash", line_color="red",
                  annotation_text="Flood Level")
    
    fig.update_layout(
        title="Water Levels by Station",
        yaxis_title="Level (m)",
        showlegend=False,
        height=400
    )
    
    return fig

def create_historical_chart(df: pd.DataFrame):
    """Create historical trends chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['rainfall_mm'],
        name='Rainfall (mm)', line=dict(color='#3b82f6')
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['water_level_m'] * 10,
        name='Water Level (×10 m)', line=dict(color='#22c55e')
    ))
    
    fig.update_layout(
        title="Historical Trends (Last 30 Days)",
        xaxis_title="Date",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    
    return fig

def create_risk_gauge(probability: float):
    """Create risk probability gauge"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Flood Risk Probability"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "#22c55e"},
                {'range': [30, 50], 'color': "#f59e0b"},
                {'range': [50, 70], 'color': "#f97316"},
                {'range': [70, 100], 'color': "#ef4444"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': probability
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig
