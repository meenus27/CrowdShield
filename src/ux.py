import folium
from streamlit.components.v1 import html

def create_base_map(center_point=(9.931233,76.267304), zoom_start=15):
    """
    Create a base folium map with multiple tile options.
    """
    try:
        m = folium.Map(
            location=center_point,
            zoom_start=zoom_start,
            tiles="OpenStreetMap",
            attr="© OpenStreetMap contributors",
        )
        # Add tile layer options with attribution. Use explicit URLs for
        # Stamen tiles to avoid streamlit_folium trying to resolve them
        # as local static files (which caused the 'Stamen Terrain' read error).
        folium.TileLayer(
            tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
            name="Stamen Terrain",
            attr="Map tiles by Stamen Design, © OpenStreetMap contributors",
        ).add_to(m)
        folium.TileLayer(
            "CartoDB positron",
            attr="© OpenStreetMap contributors, © CartoDB",
        ).add_to(m)
        folium.LayerControl().add_to(m)
        return m
    except Exception as e:
        print(f"Map creation error: {e}")
        return folium.Map(
            location=center_point,
            zoom_start=zoom_start,
            tiles="OpenStreetMap",
            attr="© OpenStreetMap contributors",
        )

def add_hazards_to_map(m, hazards_gdf, i18n=None):
    """
    Add hazard zones to map with error handling.
    """
    if hazards_gdf is None or hazards_gdf.empty:
        return
    try:
        for _, row in hazards_gdf.iterrows():
            label = row.get("name", i18n.get("hazard", "Hazard") if i18n else "Hazard")
            risk_level = row.get('risk', 'high')
            color_map = {"low": "yellow", "medium": "orange", "high": "red", "critical": "darkred"}
            color = color_map.get(risk_level.lower(), "red")
            
            folium.GeoJson(
                row["geometry"],
                name=label,
                style_function=lambda x, c=color: {
                    "fillColor": c,
                    "color": c,
                    "opacity": 0.6,
                    "weight": 2
                },
                tooltip=f"{label} ({risk_level})",
                popup=folium.Popup(f"<b>{label}</b><br>Risk: {risk_level}", max_width=200)
            ).add_to(m)
    except Exception as e:
        print(f"Error adding hazards to map: {e}")

def add_shelters_to_map(m, shelters_df, i18n=None):
    """
    Add shelters to map with error handling.
    """
    if m is None:
        return
    if shelters_df is None or shelters_df.empty:
        return
    try:
        for _, r in shelters_df.iterrows():
            try:
                name = str(r.get('name', 'Shelter'))
                capacity = str(r.get('capacity', 'Unknown'))
                lat = float(r.get('lat', 0))
                lon = float(r.get('lon', 0))
                
                if lat == 0 and lon == 0:
                    continue  # Skip invalid coordinates
                
                shelter_label = i18n.get('shelter', 'Shelter') if i18n and isinstance(i18n, dict) else 'Shelter'
                capacity_label = i18n.get('capacity', 'Capacity') if i18n and isinstance(i18n, dict) else 'Capacity'
                
                popup_text = f"<b>{shelter_label}</b>: {name}<br>{capacity_label}: {capacity}"
                
                folium.CircleMarker(
                    location=(lat, lon),
                    radius=8,
                    color="blue",
                    fill=True,
                    fillColor="blue",
                    popup=folium.Popup(popup_text, max_width=200),
                    tooltip=f"{name} ({capacity})"
                ).add_to(m)
            except Exception as e:
                print(f"Error adding shelter {r.get('name', 'unknown')}: {e}")
                continue
    except Exception as e:
        print(f"Error in add_shelters_to_map: {e}")

def add_origin_to_map(m, origin, i18n=None):
    """
    Add origin point to map with error handling.
    """
    if m is None or origin is None:
        return
    try:
        label = i18n.get("origin", "Origin") if i18n and isinstance(i18n, dict) else "Origin"
        folium.Marker(
            location=origin,
            icon=folium.Icon(color="green", icon="user", prefix="glyphicon"),
            popup=folium.Popup(f"<b>{label}</b>", max_width=150),
            tooltip=label
        ).add_to(m)
    except Exception as e:
        print(f"Error adding origin to map: {e}")
        # Try with simpler marker
        try:
            folium.Marker(location=origin, popup="Origin").add_to(m)
        except:
            pass

def add_route_to_map(m, route, i18n=None):
    """
    Add route to map with enhanced styling.
    """
    if not route or len(route) < 2:
        return
    try:
        label = i18n.get("route", "Route") if i18n else "Route"
        folium.PolyLine(
            locations=route,
            color="green",
            weight=5,
            opacity=0.8,
            tooltip=label,
            popup=folium.Popup(f"<b>{label}</b><br>Distance: {len(route)} points", max_width=200)
        ).add_to(m)
        
        # Add start and end markers
        if len(route) >= 2:
            folium.Marker(
                location=route[0],
                icon=folium.Icon(color="green", icon="play", prefix="fa"),
                popup="Start"
            ).add_to(m)
            folium.Marker(
                location=route[-1],
                icon=folium.Icon(color="red", icon="stop", prefix="fa"),
                popup="End"
            ).add_to(m)
    except Exception as e:
        print(f"Error adding route to map: {e}")


def add_reports_to_map(m, reports, i18n=None):
    """
    Add user-reported incidents to the map.

    Each report is expected to be a dict with keys:
      - lat, lon
      - type
      - severity
      - note
    """
    if not reports:
        return
    try:
        for r in reports:
            lat = r.get("lat")
            lon = r.get("lon")
            if lat is None or lon is None:
                continue
            r_type = r.get("type", "Incident")
            severity = r.get("severity", "medium")
            note = r.get("note", "")
            label = i18n.get("report", "Report") if i18n and isinstance(i18n, dict) else "Report"
            popup_html = f"<b>{label}</b>: {r_type}<br>Severity: {severity}<br>{note}"
            folium.CircleMarker(
                location=(lat, lon),
                radius=6,
                color="red",
                fill=True,
                fillColor="red",
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{r_type} ({severity})",
            ).add_to(m)
    except Exception as e:
        print(f"Error adding reports to map: {e}")

def render_map(m):
    html(m.get_root().render(), height=500)
