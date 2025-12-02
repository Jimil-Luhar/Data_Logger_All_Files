# AI Route Finder Model
>This is an advanced AI software designed to process and utilize environmental data gathered from low-power hardware loggers.

![Dashboard Screenshot](Assets/Dashboard.png)

![Suggested Route Screenshot](Assets/Suggested_Route.png)

This software was developed as part of an official academic project of Low-Power Data Logging. While the hardware component handles the efficient logging of GPS, Temperature, and Humidity data, this repository demonstrates how to use that "ground truth" data using Machine Learning.

This model not only enhances the understanding of local environmental conditions but also improves navigation by prioritizing comfort over mere speed.

## Project Context & Value Proposition

>This project serves as a proof-of-concept for Data Utilization.

**The Data ("_The Gold_")**: Raw sensors logs contain the specific GPS coordinates and temperature values, which can be used later to train the model. Then the model will suggest a suitable path based on that data.

**The AI**: Based on Random Forest regression

### Random Forest Regressor
Random Forest is an "_ensemble_" machine learning technique, which simply means it combines many small models to create one strong predictor. Instead of relying on a single complex "Decision Tree" (which acts like a giant flowchart of rules), this algorithm builds hundreds of separate trees.

The "__Random__" part is the key to its success. During training, each tree is only allowed to study a random sample of your total data (a technique technically called Bagging). Because each tree sees a slightly different piece of the puzzle, they learn different patterns. To make a final temperature prediction, the algorithm takes the average answer from all the trees. This "wisdom of the crowd" approach cancels out individual errors and prevents the model from simply memorizing the training data (overfitting), resulting in much more reliable predictions on new routes.

## Technical Architecture

The system follows a modular ETL (Extract, Transform, Load) pipeline:

1.Ingestion Layer (Hybrid Source):
  
  + **Hardware Input**: Ingests CSV logs (timestamp, lat, lon, temp) from the physical data logger.
  
  + **API Input**: Fetches historical reanalysis data from Open-Meteo to fill gaps where hardware data is missing.
  
  + **Geometry**: Queries OSRM to snap noisy raw GPS logs to valid road graph edges.

2.Processing Layer:

  + **Spatio-Temporal Features**: Cyclical encoding of time (Month/Hour) and geospatial segment mapping.

  + **Model**: Ensemble Learning (Random Forest Regressor, n=100) trained to minimize Mean Absolute Error (MAE) between predicted and observed temperatures.

3.Application Layer:

  + **Geocoding**: Nominatim API for dynamic start/end point resolution.

  + **Visualization**: Streamlit Dashboard with Plotly Mapbox for route-specific heatmaps.

## Tech Stack

+ **Language:** Python 3.11

+ **Machine Learning:** Scikit-Learn (Random Forest)

+ **Data Processing:** Pandas, NumPy

+ **Geospatial:** Polyline, OSRM API, Nominatim API

+ **Visualization:** Plotly Express, Streamlit

## Installation & Usage

+ Clone the Repository

+ Install Dependencies

      pip install -r dependencies.txt


+ Data Pipeline (ETL)
  
    This script merges your local hardware logs with API data. Place your logger file as logger_data.csv in the root directory before running.

      python fetch_real_data.py


+ Model Training
    Train the AI on the combined dataset.

      python train_model.py


    Output: temperature_model.pkl

+ Run the Dashboard

      streamlit run app.py


##  Performance Metrics

+ _Target Corridor_: Vadodara to Ahmedabad (~100km).

+ _Model Accuracy_: Achieved a Mean Absolute Error (MAE) of +/- 0.13°C on the validation set.

+ _Inference Speed_: < 50ms per route segment.

##  License & Usage

This project is part of an academic submission. It is NOT Open Source.

No license is granted for commercial use, modification, or redistribution.

The code is provided strictly for academic review and demonstration purposes.

**Copyright © 2025 _Jimil Luhar_. All Rights Reserved.**
