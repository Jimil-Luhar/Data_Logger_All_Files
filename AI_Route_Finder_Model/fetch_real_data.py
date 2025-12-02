import requests
import polyline
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import numpy as np

# --- CONFIGURATION ---
START_LOC = (22.30499013251421, 73.19084042580408) # Vadodara
END_LOC = (23.070228013469958, 72.51690870297924)  # Ahmedabad

# Reduced to 2 representative dates to speed up the MVP
DATES_TO_FETCH = ["2023-01-15", "2023-05-15"] 
HOURS_TO_SAMPLE = [8, 14, 18]
LOGGER_FILE_PATH = "logger_data.csv"

def get_multiple_routes(start, end):
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&alternatives=true"
    try:
        response = requests.get(url)
        data = response.json()
        routes_dict = {}
        print(f"   > OSRM found {len(data['routes'])} valid paths.")
        
        for idx, route in enumerate(data['routes']):
            geometry = route['geometry']
            coords = polyline.decode(geometry)
            # To make operations faster, Stride changed from 20 to 40 (fewer points)
            sampled_coords = coords[::40] 
            if coords[0] not in sampled_coords: sampled_coords.insert(0, coords[0])
            if coords[-1] not in sampled_coords: sampled_coords.append(coords[-1])
            routes_dict[idx] = sampled_coords
        return routes_dict
    except Exception as e:
        print(f"Error: {e}")
        return {}

def get_daily_weather(lat, lon, date):
    #Fetches ALL hours for a single day in one request.
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date,
        "end_date": date,
        "hourly": "temperature_2m",
        "timezone": "auto"
    }
    for _ in range(3):
        try:
            res = requests.get(url, params=params)
            if res.status_code == 200:
                return res.json()['hourly']['temperature_2m']
            time.sleep(1)
        except:
            time.sleep(1)
    return None

# --- MAIN EXECUTION ---
print("--- 1. CALCULATING ROUTES ---")
routes_data = get_multiple_routes(START_LOC, END_LOC)

all_data = []

print("\n--- 2. FETCHING WEATHER (Optimized) ---")

for route_id, waypoints in routes_data.items():
    print(f"\nProcessing ROUTE {route_id} ({len(waypoints)} segments)...")
    
    # Loop through POINTS first, then DATES
    # This keeps connections alive better and is logically faster
    for i, point in enumerate(waypoints):
        lat, lon = point
        
        # Visual progress dot every 5 segments
        if i % 5 == 0: print(f"      Processing segment {i}/{len(waypoints)}...", end='\r')
        
        for date in DATES_TO_FETCH:
            # 1. Fetch 24 hours of data for this point ONCE
            daily_temps = get_daily_weather(lat, lon, date)
            
            if daily_temps:
                # 2. Extract the specific hours we need
                for hour in HOURS_TO_SAMPLE:
                    # Simulate travel time offset
                    actual_hour = hour + int((i * 2) / 60)
                    if actual_hour > 23: actual_hour = 23
                    
                    temp = daily_temps[actual_hour]
                    
                    all_data.append({
                        "date": date,
                        "start_hour": hour,
                        "lat": lat,
                        "lon": lon,
                        "route_id": route_id,
                        "segment_id": i,
                        "temp_c": temp
                    })
        # Small sleep to be safe
        time.sleep(0.05) 

print("\n\n--- 3. SAVING DATASET ---")
df = pd.DataFrame(all_data)
df.to_csv("real_route_data.csv", index=False)
print(f"✅ SUCCESS! Saved {len(df)} data points.")