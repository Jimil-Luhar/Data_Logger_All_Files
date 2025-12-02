import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

# 1. LOAD DATA
print("--- LOADING DATA ---")
try:
    df = pd.read_csv("real_route_data.csv")
    print(f"Loaded {len(df)} rows of data.")
except FileNotFoundError:
    print("❌ Error: 'real_route_data.csv' not found. Run fetch_real_data.py first!")
    exit()

# 2. FEATURE ENGINEERING
print("--- PREPARING FEATURES ---")
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.month
df['day_of_year'] = df['date'].dt.dayofyear

# --- Added 'route_id' ---
# AI should know that Segment 5 on Route 0 is different from Segment 5 on Route 1
features = ['route_id', 'segment_id', 'start_hour', 'month']

# Check if route_id exists
if 'route_id' not in df.columns:
    print("⚠️  Warning: 'route_id' not found in CSV. Assuming Route 0 for all.")
    df['route_id'] = 0

X = df[features]
y = df['temp_c']

# 3. SPLIT DATA
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. TRAIN MODEL
print("--- TRAINING MODEL (Random Forest) ---")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. EVALUATE
predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
print(f"✅ Model Trained!")
print(f"   Average Error: +/- {mae:.2f}°C")

# 6. SAVE THE MODEL
joblib.dump(model, "temperature_model.pkl")
print("--- SAVED TO 'temperature_model.pkl' ---")