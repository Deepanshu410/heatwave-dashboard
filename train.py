"""
Extreme Heatwave Early Warning & Human Thermal Stress Index Platform
Data Ingestion, Feature Engineering & Model Training Pipeline
"""

import os
import math
import json
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "DailyDelhiClimate.csv")
MODEL_JSON_PATH = os.path.join(BASE_DIR, "delhi_climate_model.json")
EDA_CORR_PATH = os.path.join(BASE_DIR, "eda_correlation_matrix.csv")


def calculate_stull_tw(temp: float, humidity: float) -> float:
    """Psychrometric wet-bulb temperature via Stull's empirical formula."""
    return (
        temp * math.atan(0.151977 * math.sqrt(humidity + 8.313659))
        + math.atan(temp + humidity)
        - math.atan(humidity - 1.676331)
        + 0.00391838 * (humidity ** 1.5) * math.atan(0.023101 * humidity)
        - 4.686035
    )


def train_pipeline():
    print(f"[1/5] Loading historical dataset from: {CSV_PATH}")
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Dataset not found at {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    raw_count = len(df)
    print(f"      Loaded {raw_count} raw records.")

    # 1. Cleaning nulls and renaming columns
    df.dropna(inplace=True)
    df.rename(columns={'meantemp': 'temperature'}, inplace=True)
    cleaned_count = len(df)
    print(f"[2/5] Cleaned dataset has {cleaned_count} rows (dropped {raw_count - cleaned_count} nulls).")

    # 2. Derive engineered features
    hi_list = []
    tw_list = []
    utci_list = []
    target_list = []

    for _, row in df.iterrows():
        t = float(row['temperature'])
        rh = max(0.0, min(100.0, float(row['humidity'])))
        ws = max(0.0, float(row['wind_speed']))

        # Engineered features as defined in PRD Section 6
        # feature_hi: Heat Index approximation
        hi = t + (0.05 * rh)
        # feature_tw: Wet-Bulb approximation using Stull arctangent formula
        tw = calculate_stull_tw(t, rh)
        # feature_utci: UTCI-style approximation
        utci = t + (0.34 * rh) - (0.75 * max(0.5, ws))
        # Target: temperature adjusted for wind cooling
        y = t - (ws * 0.12)

        hi_list.append(hi)
        tw_list.append(tw)
        utci_list.append(utci)
        target_list.append(y)

    df['feature_hi'] = hi_list
    df['feature_tw'] = tw_list
    df['feature_utci'] = utci_list
    df['target_y'] = target_list

    # 3. Export correlation matrix
    print(f"[3/5] Calculating and exporting correlation matrix to: {EDA_CORR_PATH}")
    corr_cols = ['temperature', 'humidity', 'wind_speed', 'feature_hi', 'feature_tw', 'feature_utci', 'target_y']
    corr_matrix = df[corr_cols].corr()
    corr_matrix.to_csv(EDA_CORR_PATH)
    print(corr_matrix.round(4))

    # 4. Fit Linear Regression Model
    print("[4/5] Fitting Linear Regression model...")
    X = df[['feature_hi', 'feature_tw', 'feature_utci']]
    y = df['target_y']

    model = LinearRegression()
    model.fit(X, y)

    y_pred = model.predict(X)

    # Compute genuine empirical R^2 and MSE (PRD fix: no hardcoded placeholders!)
    accuracy_r2 = float(r2_score(y, y_pred))
    error_mse = float(mean_squared_error(y, y_pred))

    print("---------------------------------------------------------------")
    print(f"TRAINED MODEL PARAMETERS:")
    print(f"  Intercept:       {model.intercept_:.6f}")
    print(f"  w_heat_index:    {model.coef_[0]:.6f}")
    print(f"  w_wet_bulb:      {model.coef_[1]:.6f}")
    print(f"  w_utci:          {model.coef_[2]:.6f}")
    print(f"  Real R^2 Score:  {accuracy_r2:.6f} ({accuracy_r2 * 100:.2f}%)")
    print(f"  Real MSE Error:  {error_mse:.6f}")
    print(f"  Records Processed: {cleaned_count}")
    print("---------------------------------------------------------------")

    # 5. Save model parameters to JSON
    meta = {
        'intercept': round(float(model.intercept_), 6),
        'w_heat_index': round(float(model.coef_[0]), 6),
        'w_wet_bulb': round(float(model.coef_[1]), 6),
        'w_utci': round(float(model.coef_[2]), 6),
        'r2_score': round(accuracy_r2, 6),
        'mse': round(error_mse, 6),
        'records_count': cleaned_count,
        'dataset_name': 'Daily Delhi Climate Historical Records',
        'feature_names': ['feature_hi', 'feature_tw', 'feature_utci'],
        'formula_description': 'target_y = intercept + w_hi * feature_hi + w_tw * feature_tw + w_utci * feature_utci',
        'target_description': 'Temperature adjusted for convective wind cooling (temp - 0.12 * wind_speed)'
    }

    with open(MODEL_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)

    print(f"[5/5] Saved model metadata and real metrics to: {MODEL_JSON_PATH}")
    return meta


if __name__ == '__main__':
    train_pipeline()
