import requests
import polyline
import pandas as pd

print("--- SYSTEM CHECK ---")

# 1. Test Internet & API Access
try:
    response = requests.get("https://archive-api.open-meteo.com/v1/archive?latitude=52.52&longitude=13.41&start_date=2023-01-01&end_date=2023-01-02&hourly=temperature_2m")
    if response.status_code == 200:
        print("API Connection: SUCCESS (Connected to Open-Meteo)")
    else:
        print("API Connection: FAILED")
except Exception as e:
    print(f"API Connection: FAILED ({e})")

# 2. Test Libraries
try:
    df = pd.DataFrame({"test": [1, 2, 3]})
    print("Data Science Libs: SUCCESS (Pandas is working)")
except ImportError:
    print("Data Science Libs: FAILED")

print("--- END CHECK ---")