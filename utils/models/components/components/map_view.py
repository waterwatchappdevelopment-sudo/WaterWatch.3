import folium
from streamlit_folium import st_folium
from config import WESTMEATH_LAT, WESTMEATH_LON

def create_sensor_map(sensors: list):
    """Create interactive map with sensor markers"""
    m = folium.Map(
        location=[WESTMEATH_LAT, WESTMEATH_LON],
        zoom_start=10,
        tiles='cartodbpositron'
    )
    
    # Color mapping
    status_colors = {
        'normal': 'green',
        'warning': 'orange', 
        'critical': 'red'
    }
    
    # Icon mapping
    type_icons = {
        'water_level': 'tint',
        'rainfall': 'cloud',
        'soil_moisture': 'leaf'
    }
    
    for sensor in sensors:
        popup_html = f"""
        <div style="width: 200px">
            <h4>{sensor['name']}</h4>
            <p><b>Type:</b> {sensor['type'].replace('_', ' ').title()}</p>
            <p><b>Value:</b> {sensor['value']} {sensor['unit']}</p>
            <p><b>Status:</b> {sensor['status'].upper()}</p>
            <p><b>Trend:</b> {sensor['trend']}</p>
        </div>
        """
        
        folium.Marker(
            location=[sensor['lat'], sensor['lon']],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=sensor['name'],
            icon=folium.Icon(
                color=status_colors.get(sensor['status'], 'blue'),
                icon=type_icons.get(sensor['type'], 'info-sign'),
                prefix='glyphicon'
            )
        ).add_to(m)
    
    # Add Lough Ennell
    folium.Circle(
        location=[53.48, -7.39],
        radius=2000,
        color='#3b82f6',
        fill=True,
        fillOpacity=0.3,
        tooltip="Lough Ennell"
    ).add_to(m)
    
    # Add Lough Owel
    folium.Circle(
        location=[53.57, -7.38],
        radius=1500,
        color='#3b82f6',
        fill=True,
        fillOpacity=0.3,
        tooltip="Lough Owel"
    ).add_to(m)
    
    return m
