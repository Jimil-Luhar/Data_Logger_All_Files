import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
import polyline
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="TempTraverse", layout="wide")

# --- 1. LOAD THE MODEL ---
@st.cache_resource
def load_model():
    try:
        return joblib.load("temperature_model.pkl")
    except:
        return None

model = load_model()

# --- 2. HELPER FUNCTIONS ---

def geocode_location(location_name):
    # Converts a place name (e.g., 'Vadodara') into Lat/Lon coordinates
    # using the free OpenStreetMap Nominatim API.
    
    url = "https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'TempTraverseApp/1.0'} # Required by their terms
    params = {
        'q': location_name,
        'format': 'json',
        'limit': 1
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200 and len(response.json()) > 0:
            data = response.json()[0]
            return float(data['lat']), float(data['lon'])
        else:
            return None
    except:
        return None

def get_routes(start_coords, end_coords):
    # Fetch paths from OSRM using dynamic coordinates
    url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&alternatives=true"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    data = response.json()
    return data.get('routes', [])

# --- 3. THE UI ---
st.title("Best Route Finder Based on Data.")
st.markdown("Predicting the most comfortable driving path using **Random Forest AI Algorithm**.")

# Sidebar Controls
st.sidebar.header("Trip Settings")

# NEW: Dynamic User Inputs
default_start = "Vadodara, Gujarat"
default_end = "Ahmedabad, Gujarat"
start_location = st.sidebar.text_input("Start Location", default_start)
end_location = st.sidebar.text_input("End Location", default_end)

travel_date = st.sidebar.date_input("Date of Travel", datetime.now())
travel_time = st.sidebar.slider("Departure Time", 0, 23, 14) # Default 2 PM

# Warning for demo purposes
st.sidebar.info("ℹ️ **Note:** AI model is trained on specific route data from Vadodara to Ahmedabad. Predictions for completely new regions may be illustrative only.")

if st.sidebar.button("Find Best Path"):
    if model is None:
        st.error("❌ Model not found! Please run 'train_model.py' first.")
    else:
        with st.spinner(f"Locating '{start_location}' and '{end_location}'..."):
            # 1. Geocode the text inputs
            start_coords = geocode_location(start_location)
            end_coords = geocode_location(end_location)

            if not start_coords:
                st.error(f"❌ Could not find location: {start_location}")
            elif not end_coords:
                st.error(f"❌ Could not find location: {end_location}")
            else:
                # 2. Get Routes
                routes = get_routes(start_coords, end_coords)
                
                if not routes:
                    st.error("❌ No driving routes found between these locations.")
                else:
                    results = []
                    
                    # Analyze each route found by OSRM
                    for i, route in enumerate(routes):
                        # Decode the path geometry
                        coords = polyline.decode(route['geometry'])
                        
                        # We need to predict temp for segments along this path
                        # We sample 20 points along the path to get an average
                        indices = np.linspace(0, len(coords)-1, 20).astype(int)
                        sampled_coords = [coords[j] for j in indices]
                        
                        route_temps = []
                        
                        for seg_idx, (lat, lon) in enumerate(sampled_coords):
                            # Prepare input for the AI
                            features = pd.DataFrame({
                                'route_id': [i], # ID of this route
                                'segment_id': [seg_idx * 4], # Approx segment mapping
                                'start_hour': [travel_time],
                                'month': [travel_date.month]
                            })
                            
                            # ASK THE AI
                            pred_temp = model.predict(features)[0]
                            route_temps.append(pred_temp)
                        
                        avg_temp = np.mean(route_temps)
                        max_temp = np.max(route_temps)
                        
                        results.append({
                            "Route ID": f"Route {i+1}",
                            "Avg Temp": round(avg_temp, 1),
                            "Max Temp": round(max_temp, 1),
                            "Distance (km)": round(route['distance']/1000, 1),
                            "coords": coords,
                            "color": avg_temp # For map coloring
                        })

                    # --- DISPLAY RESULTS ---
                    st.success(f"Analyzed {len(results)} possible paths from {start_location} to {end_location}.")
                    
                    # 1. Comparison Table
                    df_res = pd.DataFrame(results).drop(columns=["coords", "color"])
                    st.dataframe(df_res.style.highlight_min(subset=["Avg Temp"], color="lightgreen"))
                    
                    # 2. Map Visualization
                    # We combine all routes into one dataframe for Plotly
                    map_data = []
                    for res in results:
                        path_df = pd.DataFrame(res['coords'], columns=['lat', 'lon'])
                        path_df['Route Name'] = f"{res['Route ID']} ({res['Avg Temp']}°C)"
                        map_data.append(path_df)
                    
                    final_map_df = pd.concat(map_data)
                    
                    # Center map dynamically
                    center_lat = (start_coords[0] + end_coords[0]) / 2
                    center_lon = (start_coords[1] + end_coords[1]) / 2

                    fig = px.line_map(
                        final_map_df, 
                        lat="lat", 
                        lon="lon", 
                        color="Route Name",
                        zoom=8, 
                        center={"lat": center_lat, "lon": center_lon},
                        height=500
                    )
                    fig.update_layout(mapbox_style="open-street-map")
                    st.plotly_chart(fig, width='stretch')
                    
                    # 3. Priority Logic to suggest the most comfortable path.
                    # Sorts by: 1. Avg Temp (asc), 2. Max Temp (asc), 3. Distance (asc)
                    best_route = min(results, key=lambda x: (x['Avg Temp'], x['Max Temp'], x['Distance (km)']))
                    
                    st.info(
                        f"💡 Recommendation: Take **{best_route['Route ID']}**.\n\n"
                        f"- Average Temp: **{best_route['Avg Temp']}°C**\n"
                        f"- Maximum Temp: **{best_route['Max Temp']}°C**\n"
                        f"- Total Distance: **{best_route['Distance (km)']} km**"
                    )


