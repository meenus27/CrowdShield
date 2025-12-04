#!/usr/bin/env python3
"""
CrowdShield — Enhanced Live & Interactive Streamlit UI
Features: Real-time updates, interactive charts, live status indicators, animated elements
"""

import os
from pathlib import Path
import time
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

import streamlit as st
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px

from src import (
    data_loader,
    routing,
    fusion_engine,
    llm_insights,
    translate,
    alerting,
    authority,
    gps_mock,
    ux,
    risk_disaster,
    risk_crowd,
    tts,
    live_weather,
)


def build_gpx(route, name="Safe route"):
    """
    Build a minimal GPX representation of the given route so it can be
    imported into Garmin / GPS devices.
    """
    try:
        from xml.etree.ElementTree import Element, SubElement, tostring

        gpx = Element("gpx", version="1.1", creator="CrowdShield")
        trk = SubElement(gpx, "trk")
        name_el = SubElement(trk, "name")
        name_el.text = name
        seg = SubElement(trk, "trkseg")
        for lat, lon in route:
            SubElement(seg, "trkpt", lat=str(lat), lon=str(lon))
        return tostring(gpx, encoding="utf-8", xml_declaration=True)
    except Exception as e:
        print(f"GPX build error: {e}")
        return None

# Optional: load .env for keys
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Ensure data folders exist
Path("data/alerts").mkdir(parents=True, exist_ok=True)
Path("data/cache").mkdir(parents=True, exist_ok=True)

st.set_page_config(
    layout="wide", 
    page_title="CrowdShield — AI Disaster Copilot",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# -------- Multilingual dictionary --------
I18N = {
    "en": {
        "title": "CrowdShield Demo", "state": "Select state", "map": "Safety Map",
        "drivers": "Drivers", "severity": "Severity Tier", "advisory": "LLM Advisory",
        "risk_crowd": "Crowd risk", "risk_disaster": "Disaster risk",
        "recommendations": "Recommendations", "nearest": "Nearest shelter",
        "eta": "ETA", "distance": "Distance", "instructions": "Route instructions",
        "safety_methods": "Safety methods", "live_status": "Live Status",
        "refresh_rate": "Auto-refresh (seconds)", "enable_auto_refresh": "Enable Auto-Refresh",
        "real_time_data": "Real-time Data", "history": "Risk History",
        "current_conditions": "Current Conditions", "alerts_active": "Active Alerts"
    },
    "hi": {
        "title": "क्राउडशील्ड डेमो", "state": "राज्य चुनें", "map": "सुरक्षा मानचित्र",
        "drivers": "ड्राइवर्स", "severity": "गंभीरता स्तर", "advisory": "एलएलएम सलाह",
        "risk_crowd": "भीड़ जोखिम", "risk_disaster": "आपदा जोखिम",
        "recommendations": "सिफारिशें", "nearest": "निकटतम शेल्टर",
        "eta": "अनुमानित समय", "distance": "दूरी", "instructions": "रूट निर्देश",
        "safety_methods": "सुरक्षा उपाय", "live_status": "लाइव स्थिति",
        "refresh_rate": "ऑटो-रिफ्रेश (सेकंड)", "enable_auto_refresh": "ऑटो-रिफ्रेश सक्षम करें",
        "real_time_data": "रीयल-टाइम डेटा", "history": "जोखिम इतिहास",
        "current_conditions": "वर्तमान स्थितियां", "alerts_active": "सक्रिय अलर्ट"
    },
    "ml": {
        "title": "ക്രൗഡ്‌ഷീൽഡ് ഡെമോ", "state": "സംസ്ഥാനം തിരഞ്ഞെടുക്കുക", "map": "സുരക്ഷാ മാപ്പ്",
        "drivers": "ഡ്രൈവർസ്", "severity": "ഗൗരവത്വം", "advisory": "എൽഎൽഎം ഉപദേശം",
        "risk_crowd": "ജനക്കൂട്ട അപകടം", "risk_disaster": "ദുരന്ത അപകടം",
        "recommendations": "ശുപാർശകൾ", "nearest": "അടുത്ത അഭയം",
        "eta": "എത്താൻ വേണ്ട സമയം", "distance": "ദൂരം", "instructions": "റൂട്ടു നിർദ്ദേശങ്ങൾ",
        "safety_methods": "സുരക്ഷാ രീതികൾ", "live_status": "ലൈവ് സ്ഥിതി",
        "refresh_rate": "ഓട്ടോ-റിഫ്രഷ് (സെക്കൻഡ്)", "enable_auto_refresh": "ഓട്ടോ-റിഫ്രഷ് പ്രവർത്തനക്ഷമമാക്കുക",
        "real_time_data": "റിയൽ-ടൈം ഡാറ്റ", "history": "റിസ്ക് ചരിത്രം",
        "current_conditions": "നിലവിലെ വ്യവസ്ഥകൾ", "alerts_active": "സജീവമായ അലേർട്ടുകൾ"
    },
    "ta": {
        "title": "கூட்டம் பாதுகாப்பு டெமோ", "state": "மாநிலத்தைத் தேர்ந்தெடுக்கவும்", "map": "பாதுகாப்பு வரைபடம்",
        "drivers": "டிரைவர்கள்", "severity": "தீவிர நிலை", "advisory": "LLM ஆலோசனை",
        "risk_crowd": "கூட்டம் அபாயம்", "risk_disaster": "பேரழிவு அபாயம்",
        "recommendations": "பரிந்துரைகள்", "nearest": "அருகிலுள்ள தங்குமிடம்",
        "eta": "வருகை நேரம்", "distance": "தூரம்", "instructions": "பாதை வழிமுறைகள்",
        "safety_methods": "பாதுகாப்பு முறைகள்", "live_status": "நேரடி நிலை",
        "refresh_rate": "ஆட்டோ-ரெஃப்ரெஷ் (விநாடிகள்)", "enable_auto_refresh": "ஆட்டோ-ரெஃப்ரெஷ் இயக்கு",
        "real_time_data": "நேரடி தரவு", "history": "ஆபத்து வரலாறு",
        "current_conditions": "தற்போதைய நிலைமைகள்", "alerts_active": "செயலில் உள்ள அலாரங்கள்"
    }
}

STATES = [
    "Kerala", "Tamil Nadu", "Karnataka", "Maharashtra",
    "Uttar Pradesh", "Delhi", "West Bengal", "Rajasthan"
]

# Approximate map centres for supported states so the map pans
# to the selected region instead of always showing Kochi.
STATE_CENTERS = {
    "Kerala": (10.1632, 76.6413),
    "Tamil Nadu": (11.1271, 78.6569),
    "Karnataka": (15.3173, 75.7139),
    "Maharashtra": (19.7515, 75.7139),
    "Uttar Pradesh": (26.8467, 80.9462),
    "Delhi": (28.6139, 77.2090),
    "West Bengal": (22.9868, 87.8550),
    "Rajasthan": (27.0238, 74.2179),
}

# -------- Session State Initialization --------
if "risk_history" not in st.session_state:
    st.session_state.risk_history = []
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now()
if "auto_refresh_enabled" not in st.session_state:
    st.session_state.auto_refresh_enabled = False
if "refresh_interval" not in st.session_state:
    st.session_state.refresh_interval = 5
if "reports" not in st.session_state:
    st.session_state.reports = []
if "rainfall_slider" not in st.session_state:
    st.session_state.rainfall_slider = 30
if "wind_slider" not in st.session_state:
    st.session_state.wind_slider = 25
if "crowd_density_slider" not in st.session_state:
    st.session_state.crowd_density_slider = 1.0
if "scenario_trigger_flood" not in st.session_state:
    st.session_state.scenario_trigger_flood = False
if "scenario_trigger_crowd" not in st.session_state:
    st.session_state.scenario_trigger_crowd = False

# -------- Sidebar controls --------
st.sidebar.title("🛡️ " + I18N[st.session_state.get("lang", "en")].get("title", "CrowdShield Demo"))
lang = st.sidebar.selectbox("Language / भाषा / ഭാഷ / மொழி", options=list(I18N.keys()), index=0, key="lang_selector")
i18n = I18N[lang]

state = st.sidebar.selectbox(i18n["state"], options=STATES, index=0, key="state_selector")
role = st.sidebar.radio("User role", ["Citizen", "Authority"], index=0, key="role_selector")

# Scenario presets: set scenario flags and slider defaults
st.sidebar.markdown("#### 🎭 Scenarios")
col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    if st.button("Stadium crowd"):
        st.session_state.rainfall_slider = 10
        st.session_state.wind_slider = 10
        st.session_state.crowd_density_slider = 8.0
        st.session_state.scenario_trigger_crowd = True
        st.rerun()
with col_s2:
    if st.button("Coastal flood"):
        st.session_state.rainfall_slider = 180
        st.session_state.wind_slider = 80
        st.session_state.scenario_trigger_flood = True
        st.session_state.crowd_density_slider = 2.0
        st.rerun()

st.sidebar.markdown("### 🎛️ Simulation Controls")
trigger_flood = st.sidebar.checkbox(
    "🌊 Trigger Flood",
    value=st.session_state.scenario_trigger_flood,
    key="trigger_flood",
)
trigger_crowd = st.sidebar.checkbox(
    "👥 Trigger Crowd Surge",
    value=st.session_state.scenario_trigger_crowd,
    key="trigger_crowd",
)
offline_mode = st.sidebar.checkbox(
    "📴 Offline Mode (local graph/satellite)", value=False, key="offline_mode"
)

st.sidebar.markdown("### 🌦️ Weather Controls")
rainfall_mm = st.sidebar.slider(
    "Rainfall (mm)", 0, 200, st.session_state.rainfall_slider, 5, key="rainfall_slider"
)
wind_kph = st.sidebar.slider(
    "Wind speed (kph)", 0, 150, st.session_state.wind_slider, 5, key="wind_slider"
)
crowd_density = st.sidebar.slider(
    "Crowd Density (people/m²)", 0.0, 10.0, st.session_state.crowd_density_slider, 0.1, key="crowd_density_slider"
)

st.sidebar.markdown("### 🗺️ Routing")
route_mode = st.sidebar.radio("Route Mode", ["Shortest", "Fastest", "Safest"], index=0, key="route_mode")
find_route = st.sidebar.button("🔍 Find Safe Route", width="stretch")

st.sidebar.markdown("### 🔄 Live Updates")
auto_refresh = st.sidebar.checkbox(i18n["enable_auto_refresh"], value=st.session_state.auto_refresh_enabled, key="auto_refresh_check")
if auto_refresh:
    st.session_state.auto_refresh_enabled = True
    refresh_seconds = st.sidebar.slider(i18n["refresh_rate"], 2, 30, st.session_state.refresh_interval, 1, key="refresh_rate_slider")
    st.session_state.refresh_interval = refresh_seconds
else:
    st.session_state.auto_refresh_enabled = False

if st.sidebar.button("🔄 Manual Refresh", width="stretch"):
    st.session_state.last_update = datetime.now()
    st.rerun()

st.sidebar.markdown("### 📢 Alerts")
if st.sidebar.button("📱 Send SMS Alert", width="stretch"):
    ok, msg = alerting.send_twilio_sms("CrowdShield advisory: check app for details")
    if ok:
        st.sidebar.success(f"✅ SMS sent: {msg}")
    else:
        st.sidebar.warning(f"⚠️ SMS status: {msg}")

play_alert = st.sidebar.checkbox("🔊 Play Audio Alert", value=False, key="play_alert")
show_charts = st.sidebar.checkbox("📊 Show Interactive Charts", value=True, key="show_charts")

st.sidebar.markdown("### 📝 Crowd Reports")
with st.sidebar.form("report_form"):
    report_type = st.selectbox("Incident type", ["Flooding", "Crowd crush", "Blocked road", "Other"])
    report_severity = st.select_slider("Severity", options=["low", "medium", "high", "critical"], value="medium")
    report_note = st.text_area("Details (optional)", height=60)
    submitted_report = st.form_submit_button("Submit report")

if submitted_report:
    # Attach report to current origin location (best proxy we have without geolocation)
    origin_lat, origin_lon = gps_mock.get_mock_location_for_state(st.session_state.get("state_selector", state))
    st.session_state.reports.append(
        {
            "lat": origin_lat,
            "lon": origin_lon,
            "type": report_type,
            "severity": report_severity,
            "note": report_note,
            "timestamp": datetime.now().isoformat(),
        }
    )
    st.sidebar.success("✅ Report submitted")

st.sidebar.markdown("---")
st.sidebar.caption("💡 Tip: Enable auto-refresh for live updates. Adjust sliders to simulate conditions.")

# Auto-refresh logic
if st.session_state.auto_refresh_enabled:
    time_since_update = (datetime.now() - st.session_state.last_update).total_seconds()
    if time_since_update >= st.session_state.refresh_interval:
        st.session_state.last_update = datetime.now()
        time.sleep(0.1)  # Small delay to prevent rapid reruns
        st.rerun()

# -------- Load data --------
haz_path = f"data/hazard_zones_{state.lower().replace(' ', '_')}.geojson"
shel_path = f"data/safe_zones_{state.lower().replace(' ', '_')}.csv"
crowd_path = f"data/crowd_sim_{state.lower().replace(' ', '_')}.csv"

try:
    hazards = data_loader.load_hazards(haz_path) if Path(haz_path).exists() else data_loader.load_hazards()
except Exception as e:
    st.warning(f"Could not load hazards: {e}")
    hazards = data_loader.load_hazards()

try:
    shelters = data_loader.load_shelters(shel_path) if Path(shel_path).exists() else data_loader.load_shelters()
except Exception as e:
    st.warning(f"Could not load shelters: {e}")
    shelters = data_loader.load_shelters()

try:
    crowd_sim = data_loader.load_crowd(crowd_path) if Path(crowd_path).exists() else data_loader.load_crowd()
    # Simulate crowd density if slider is used
    if not crowd_sim.empty and "people" in crowd_sim.columns:
        crowd_sim["people"] = crowd_sim["people"] * (crowd_density / max(1.0, crowd_sim["people"].mean() / 1000))
except Exception as e:
    st.warning(f"Could not load crowd data: {e}")
    crowd_sim = data_loader.load_crowd()

# Live weather (optional) + slider override for interactivity
live_wx = live_weather.fetch_weather_for_state(state)
if live_wx:
    base_rain = live_wx["rainfall_mm"]
    base_wind = live_wx["wind_kph"]
else:
    base_rain = rainfall_mm
    base_wind = wind_kph

weather = {
    "state": state,
    "rainfall_mm": base_rain,
    "wind_kph": base_wind,
    "timestamp": datetime.now().timestamp(),
}

# -------- Risk scoring --------
try:
    disaster_score, drivers = risk_disaster.score_disaster(weather, trigger_flood)
    crowd_score, crowd_drivers = risk_crowd.score_crowd(crowd_sim, trigger_crowd)
except Exception as e:
    st.error(f"Risk scoring error: {e}")
    disaster_score, drivers = 0.0, ["Error in disaster scoring"]
    crowd_score, crowd_drivers = 0.0, ["Error in crowd scoring"]

try:
    severity, recommendations = fusion_engine.fuse(disaster_score, crowd_score, i18n=i18n)
except Exception as e:
    st.error(f"Fusion error: {e}")
    severity, recommendations = "Medium", ["Error in fusion engine"]

# Update risk history for charts
current_time = datetime.now()
st.session_state.risk_history.append({
    "timestamp": current_time,
    "disaster_score": disaster_score,
    "crowd_score": crowd_score,
    "combined": max(disaster_score, crowd_score * 0.9),
    "severity": severity
})
# Keep only last 50 points
if len(st.session_state.risk_history) > 50:
    st.session_state.risk_history = st.session_state.risk_history[-50:]

# -------- Advisory --------
try:
    advisory_en = llm_insights.generate_advisory(severity, drivers + crowd_drivers, role="Authority")
    advisory_out = translate.translate(advisory_en, dest=lang) if lang != "en" else advisory_en
except Exception as e:
    st.warning(f"Advisory generation error: {e}")
    advisory_out = f"{severity} advisory: Follow local safety instructions."

# -------- Main Layout --------
# Header with live status
col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
with col_header1:
    st.title("🛡️ CrowdShield — AI Disaster Copilot")
with col_header2:
    status_color = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}.get(severity, "⚪")
    st.metric(i18n["live_status"], f"{status_color} {severity}")
with col_header3:
    update_time = st.session_state.last_update.strftime("%H:%M:%S")
    st.caption(f"Last update: {update_time}")
    if st.session_state.auto_refresh_enabled:
        st.caption(f"🔄 Auto-refresh: {st.session_state.refresh_interval}s")

st.markdown("---")

# Main content columns
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader(i18n["map"])
    # Center map on the selected state; fall back to Kochi demo center.
    center_point = STATE_CENTERS.get(state, (9.931233, 76.267304))
    
    # Debug info (can be toggled off later)
    with st.expander("🔍 Map Debug Info", expanded=False):
        st.write(f"**Center Point:** {center_point}")
        st.write(f"**State:** {state}")
        st.write(f"**Offline Mode:** {offline_mode}")
        st.write(f"**Hazards loaded:** {not (hazards is None or hazards.empty) if hasattr(hazards, 'empty') else 'N/A'}")
        st.write(f"**Shelters loaded:** {not (shelters is None or shelters.empty) if hasattr(shelters, 'empty') else 'N/A'}")
        
        # Test map button
        if st.button("🧪 Test Map Display"):
            try:
                import folium
                test_map = folium.Map(location=center_point, zoom_start=15)
                test_map.add_child(folium.Marker(location=center_point, popup="Test Marker"))
                st_folium(test_map, width=700, height=400, key="test_map")
                st.success("✅ Test map displayed successfully!")
            except Exception as e:
                st.error(f"❌ Test map failed: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    try:
        # Load and block graph
        G = routing.load_graph(online=not offline_mode, center_point=center_point)
        G_blocked = routing.block_edges_by_hazards(G, hazards)
    except Exception as e:
        st.warning(f"Graph loading error: {e}, using fallback")
        G_blocked = None
    
    # Define origin and target.
    # Use a state-specific mock origin so the route and markers
    # appear in the selected region instead of always Kerala.
    origin = gps_mock.get_mock_location_for_state(state)
    
    # Choose nearest shelter dynamically
    import math
    def haversine_km(p1, p2):
        lat1, lon1 = p1
        lat2, lon2 = p2
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    shelters_list = [(float(row.lat), float(row.lon), row.name) for _, row in shelters.iterrows()]
    if shelters_list:
        target = min(shelters_list, key=lambda s: haversine_km(origin, (s[0], s[1])))
        target_coord = (target[0], target[1])
        target_name = target[2]
        dist_km = haversine_km(origin, target_coord)
        eta_hours = dist_km / 4.5 if dist_km > 0 else 0.0
        eta_min = int(eta_hours * 60)
    else:
        target_coord = (9.93, 76.27)
        target_name = "Fallback Shelter"
        dist_km = 1.5
        eta_min = 20
    
    # Compute route if enabled
    route = None
    route_mode_used = route_mode
    if find_route:
        if G_blocked is not None:
            try:
                if route_mode == "Shortest":
                    route = routing.compute_shortest_path(G_blocked, origin, target_coord)
                elif route_mode == "Fastest":
                    route = routing.compute_fastest_path(G_blocked, origin, target_coord)
                elif route_mode == "Safest":
                    route = routing.compute_safest_path(G_blocked, origin, target_coord, hazards)
                else:
                    route = routing.compute_shortest_path(G_blocked, origin, target_coord)
                    route_mode_used = "Shortest (fallback)"
                
                # Check if route is valid
                if route and len(route) > 1:
                    st.success(f"✅ {route_mode_used} route computed successfully! ({len(route)} waypoints)")
                else:
                    # Fallback to simple route
                    route = routing.grid_route_fallback(origin, target_coord)
                    route_mode_used = "Grid fallback"
                    st.info("Route computation returned invalid result. Using straight-line fallback.")
            except Exception as e:
                st.error(f"Routing failed: {e}")
                route = routing.grid_route_fallback(origin, target_coord)
                route_mode_used = "Grid fallback"
                st.info("Using straight-line grid fallback due to error.")
        else:
            # Use fallback route when graph is not available
            route = routing.grid_route_fallback(origin, target_coord)
            route_mode_used = "Grid fallback (offline)"
            st.info("Graph not available. Using straight-line fallback route.")
    
    # Create base map with enhanced error handling
    try:
        # Always create a base map first
        m = ux.create_base_map(center_point=center_point, zoom_start=15)
        
        if m is None:
            st.error("Failed to create map. Please check your folium installation.")
        else:
            # Add hazards if available
            try:
                if hazards is not None and not hazards.empty:
                    ux.add_hazards_to_map(m, hazards)
            except Exception as e:
                st.warning(f"Could not add hazards to map: {e}")
            
            # Add shelters if available
            try:
                if shelters is not None and not shelters.empty:
                    ux.add_shelters_to_map(m, shelters)
            except Exception as e:
                st.warning(f"Could not add shelters to map: {e}")
            
            # Add origin point
            try:
                ux.add_origin_to_map(m, origin)
            except Exception as e:
                st.warning(f"Could not add origin to map: {e}")

            # Add user crowd reports
            try:
                ux.add_reports_to_map(m, st.session_state.get("reports", []))
            except Exception as e:
                st.warning(f"Could not add reports to map: {e}")
            
            # Highlight chosen target shelter
            try:
                import folium
                folium.CircleMarker(
                    location=target_coord, 
                    radius=10, 
                    color="purple",
                    fill=True, 
                    fillColor="purple",
                    popup=folium.Popup(f"<b>Target Shelter</b><br>{target_name}", max_width=200),
                    tooltip=f"Target: {target_name}"
                ).add_to(m)
            except Exception as e:
                st.warning(f"Could not add target marker: {e}")
            
            # Add route if available
            if route:
                try:
                    ux.add_route_to_map(m, route)
                except Exception as e:
                    st.warning(f"Could not add route to map: {e}")
            
            # Render map in Streamlit - simplified for reliability
            try:
                # Try simple st_folium first
                map_data = st_folium(m, width=700, height=600, key="main_map")
            except Exception as e:
                st.error(f"Map rendering error: {str(e)}")
                # Fallback: try to render with HTML directly
                try:
                    import folium
                    html_str = m._repr_html_()
                    st.components.v1.html(html_str, width=700, height=600)
                    st.info("Map rendered using HTML fallback method.")
                except Exception as e2:
                    st.error(f"Fallback map rendering failed: {str(e2)}")
                    # Last resort: create and show minimal map
                    try:
                        minimal = folium.Map(location=center_point, zoom_start=15)
                        st_folium(minimal, width=700, height=600, key="minimal_map")
                    except:
                        st.error("Could not display map. Please check your Streamlit and Folium installation.")
                    
    except Exception as e:
        st.error(f"Critical map creation error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        # Last resort: create a minimal map
        try:
            import folium
            minimal_map = folium.Map(location=center_point, zoom_start=15)
            st_folium(minimal_map, width=700, height=600, key="fallback_map")
            st.info("Displaying minimal map as fallback.")
        except Exception as e2:
            st.error(f"Could not create fallback map: {str(e2)}")

with right_col:
    # Severity section with animated color badge
    severity_colors = {
        "Low": "#2ECC71", 
        "Medium": "#F5B041", 
        "High": "#E67E22", 
        "Critical": "#C0392B"
    }
    st.subheader(i18n["severity"])
    color = severity_colors.get(severity, "#bdc3c7")
    st.markdown(
        f"<div style='padding:12px;border-radius:8px;background:{color};"
        f"color:white;font-weight:bold;text-align:center;font-size:18px;"
        f"box-shadow:0 4px 6px rgba(0,0,0,0.1)'>{severity}</div>",
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Drivers with icons
    st.markdown("**" + i18n["drivers"] + ":**")
    driver_icons = {
        "rainfall": "🌧️",
        "wind": "💨",
        "flood": "🌊",
        "crowd": "👥",
        "density": "📊"
    }
    for d in drivers + crowd_drivers:
        icon = "⚠️"
        for key, emoji in driver_icons.items():
            if key.lower() in d.lower():
                icon = emoji
                break
        st.write(f"{icon} {d}")
    
    st.markdown("---")
    
    # Advisory
    st.subheader(i18n["advisory"])
    st.info(advisory_out)
    
    # Play GPS-style TTS in selected language: brief situation + route summary
    if play_alert:
        try:
            # Build a concise "navigation" style sentence in English first
            nav_msg_en = (
                f"Current risk level is {severity}. "
                f"Nearest shelter {target_name} is {dist_km:.1f} kilometers away, "
                f"approximately {eta_min} minutes on foot. "
            )
            if route:
                nav_msg_en += (
                    f"Using {route_mode_used} route. Follow the marked path to the shelter "
                    f"and avoid hazard and flood zones."
                )
            else:
                nav_msg_en += (
                    "Routing is not available. Move carefully towards the shelter "
                    "and avoid hazard and flood zones."
                )

            # Append the LLM advisory for extra context
            full_msg_en = f"{nav_msg_en} Advisory: {advisory_en}"

            # Translate the full message into the selected UI language
            if lang != "en":
                try:
                    tts_text = translate.translate(full_msg_en, dest=lang)
                except Exception:
                    tts_text = advisory_out  # fall back to already translated advisory
            else:
                tts_text = full_msg_en

            tts_lang = lang if lang in ("en", "hi", "ml", "ta") else "en"
            path = tts.generate_tts(tts_text, lang=tts_lang)
            if path and path.endswith(".mp3"):
                st.audio(path, autoplay=True)
                st.success(f"🔊 Playing navigation advisory ({tts_lang})")
            else:
                st.warning("TTS unavailable. Using text advisory.")
        except Exception as e:
            st.warning(f"TTS error: {e}")
    
    st.markdown("---")
    
    # Recommendations
    st.subheader(i18n["recommendations"])
    for i, r in enumerate(recommendations, 1):
        st.write(f"{i}. {r}")
    
    st.markdown("---")
    
    # Nearest shelter card
    st.subheader(i18n["nearest"])
    st.markdown(f"**{target_name}**")
    col_dist, col_eta = st.columns(2)
    with col_dist:
        st.metric(i18n["distance"], f"{dist_km:.2f} km")
    with col_eta:
        st.metric(i18n["eta"], f"~{eta_min} min")
    
    # Turn-by-turn route instructions
    if route:
        st.markdown("---")
        st.subheader(i18n["instructions"])
        instruction_container = st.container()
        with instruction_container:
            for i, pt in enumerate(route[:10], 1):  # Limit to first 10 steps
                st.write(f"📍 Step {i}: ({pt[0]:.5f}, {pt[1]:.5f})")
            if len(route) > 10:
                st.caption(f"... and {len(route) - 10} more steps")
        st.caption(f"Mode: {route_mode_used}")

        # Offer GPX download so route can be loaded on Garmin / GPS devices
        gpx_bytes = build_gpx(route, name=f"Safe route to {target_name}")
        if gpx_bytes:
            st.download_button(
                "📥 Download GPX for Garmin / GPS",
                data=gpx_bytes,
                file_name="crowdshield_safe_route.gpx",
                mime="application/gpx+xml",
            )
    
    st.markdown("---")
    
    # Risk scores with animated progress bars
    st.subheader(i18n["risk_crowd"])
    st.progress(min(1.0, max(0.0, crowd_score)), text=f"{crowd_score*100:.1f}%")
    st.subheader(i18n["risk_disaster"])
    st.progress(min(1.0, max(0.0, disaster_score)), text=f"{disaster_score*100:.1f}%")

    # Authority-specific panel: recent reports & auto-alerts when risk is high
    if role == "Authority":
        st.markdown("---")
        st.subheader("Authority View")
        reports = st.session_state.get("reports", [])
        st.write(f"Total crowd reports: {len(reports)}")
        if reports:
            last_reports = reports[-5:]
            for r in reversed(last_reports):
                try:
                    st.write(
                        f"• [{r.get('severity','?')}] {r.get('type','Incident')} "
                        f"at ({float(r.get('lat')):.4f}, {float(r.get('lon')):.4f}) — {r.get('note','')}"
                    )
                except Exception:
                    st.write(
                        f"• [{r.get('severity','?')}] {r.get('type','Incident')} — {r.get('note','')}"
                    )

        auto_alerts_enabled = st.checkbox(
            "Enable automatic SMS alert when risk is High or Critical",
            value=False,
            key="auto_sms_enabled",
        )
        if auto_alerts_enabled and severity in ("High", "Critical"):
            if not st.session_state.get("auto_sms_sent", False):
                ok, msg = alerting.send_twilio_sms(
                    f"CrowdShield automatic alert: {severity} risk detected in {state}. "
                    f"Nearest shelter: {target_name} (~{dist_km:.1f} km)."
                )
                st.session_state.auto_sms_sent = ok
                if ok:
                    st.success("✅ Automatic SMS alert sent")
                else:
                    st.warning(f"⚠️ SMS status: {msg}")

# -------- Interactive Charts Section --------
if show_charts and st.session_state.risk_history:
    st.markdown("---")
    st.subheader(i18n.get("history", "Risk History"))
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Time series chart
        df_history = pd.DataFrame(st.session_state.risk_history)
        if not df_history.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_history["timestamp"],
                y=df_history["disaster_score"],
                mode='lines+markers',
                name='Disaster Risk',
                line=dict(color='#E67E22', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=df_history["timestamp"],
                y=df_history["crowd_score"],
                mode='lines+markers',
                name='Crowd Risk',
                line=dict(color='#3498DB', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=df_history["timestamp"],
                y=df_history["combined"],
                mode='lines+markers',
                name='Combined Risk',
                line=dict(color='#E74C3C', width=3)
            ))
            fig.update_layout(
                title="Risk Scores Over Time",
                xaxis_title="Time",
                yaxis_title="Risk Score (0-1)",
                hovermode='x unified',
                height=300
            )
            st.plotly_chart(fig, width="stretch")
    
    with chart_col2:
        # Current conditions gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=disaster_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Disaster Risk Level"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 25], 'color': "#2ECC71"},
                    {'range': [25, 50], 'color': "#F5B041"},
                    {'range': [50, 75], 'color': "#E67E22"},
                    {'range': [75, 100], 'color': "#C0392B"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, width="stretch")
    
    # Risk distribution pie chart
    st.markdown("### Current Risk Breakdown")
    risk_col1, risk_col2, risk_col3 = st.columns(3)
    with risk_col1:
        st.metric("Disaster Risk", f"{disaster_score*100:.1f}%", delta=f"{disaster_score*100:.1f}%")
    with risk_col2:
        st.metric("Crowd Risk", f"{crowd_score*100:.1f}%", delta=f"{crowd_score*100:.1f}%")
    with risk_col3:
        combined_risk = max(disaster_score, crowd_score * 0.9)
        st.metric("Combined Risk", f"{combined_risk*100:.1f}%", delta=f"{combined_risk*100:.1f}%")

    # High-level KPIs for demo / authority view
    st.markdown("### Summary KPIs")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.metric("Total Reports", len(st.session_state.get("reports", [])))
    with kpi_col2:
        st.metric("Last Severity", severity)
    with kpi_col3:
        if st.session_state.risk_history:
            last10 = pd.DataFrame(st.session_state.risk_history[-10:])
            avg_combined = last10["combined"].mean() * 100
            st.metric("Avg Combined Risk (last 10)", f"{avg_combined:.1f}%")
        else:
            st.metric("Avg Combined Risk (last 10)", "N/A")

# -------- Safety methods --------
st.markdown("---")
st.subheader(i18n.get("safety_methods", "Safety methods"))
safety_tips = [
    "🏔️ Move to higher ground and avoid flood-prone areas",
    "🚫 Do not walk or drive through floodwaters",
    "🚪 In crowds, stay near exits and avoid dense clusters",
    "🎒 Carry ID, medicines, and an emergency kit",
    "📱 Follow official instructions; prefer SMS/low-bandwidth channels in outages",
    "🔋 Keep devices charged and have backup power",
    "👥 Stay in groups and inform others of your location"
]
for tip in safety_tips:
    st.write(tip)

# Footer with mode info
st.markdown("---")
st.caption(
    f"🔄 Auto-refresh: {'ON' if st.session_state.auto_refresh_enabled else 'OFF'} | "
    f"📊 Charts: {'ON' if show_charts else 'OFF'} | "
    f"🌐 Mode: {'Offline' if offline_mode else 'Online'} | "
    f"📍 State: {state}"
)
st.caption(
    "Notes: LLM/Twilio fallbacks are enabled. Offline mode uses local graph and satellite console. "
    "Enable auto-refresh for live updates."
)
