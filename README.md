# heatwave-dashboard
# 🌡️ Hai Garmi — Regional Heat-Risk & Mortality Index Console

## 📌 About the Project

Hai Garmi is a heatwave early-warning and human thermal-stress monitoring system designed to identify heat-related risk for a specific city or ward.

The system combines live weather data, physiological heat-stress indicators, and Machine Learning to generate a **Mortality Risk Index (MRI) from 0–10**.

It also provides recommended actions for:
- Disaster Management
- Healthcare Systems
- Power Grid Management

---

## 🎯 Objectives

- Fetch live temperature, humidity and wind-speed data.
- Calculate important heat-stress indicators:
  - IMD Heat Index
  - Wet-Bulb Temperature
  - UTCI
  - sWBGT
- Use Machine Learning to calculate a 0–10 Mortality Risk Index.
- Provide a simple backend API.
- Display heat-risk information through an interactive dashboard.
- Generate administrative recommendations according to risk level.

---

## 🏗️ System Architecture

User Input (City/Ward)
        ↓
Geocoding / Ward Data
        ↓
Live Weather API
        ↓
Heat-Stress Calculations
        ↓
Humidity Filter
        ↓
Machine Learning Model
        ↓
Mortality Risk Index (0–10)
        ↓
Dashboard + Administrative Actions

---

## 🤖 Machine Learning

### Model Used
**Linear Regression**

The model combines heat-stress indicators to produce the Mortality Risk Index.

### Dataset

The current prototype uses the **Daily Delhi Climate Dataset** containing daily temperature, humidity and wind-speed records for Delhi from 2013–2017.

### Train/Test Split

- 80% Training Data
- 20% Testing Data

### Model Results

- R² Score: **0.78**
- Mean Squared Error (MSE): **0.26**

> Note: The current risk label is a research-based proxy score and is not trained directly on actual mortality records.

---

## 🌦️ Live Weather Data

The project uses the **Open-Meteo API** to obtain live weather information.

The system uses:
- Temperature
- Relative Humidity
- Wind Speed

If the API is unavailable, cached weather values can be used.

---

## ⚙️ Backend

The backend is developed using:

- Python
- Built-in `http.server`
- REST-style API

### API Endpoint

```text
GET /analyze?city=<city_name>

👨‍💻 Technologies Used
Python
Machine Learning
Scikit-learn
HTML
CSS
JavaScript
Open-Meteo API
Kaggle Dataset
