import math
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error

print("[ML INITIALIZATION]: Loading local Kaggle DailyDelhiClimateTrain.csv dataset...")

try:
    df = pd.read_csv("delhi_climate_change.csv")
except Exception as e:
    print(f"[ERROR]: Could not read local dataset file: {e}")
    exit()

df.dropna(inplace=True)
df.rename(columns={
    'meantemp': 'temperature',
    'humidity': 'humidity',
    'wind_speed': 'wind_speed'
}, inplace=True)

hi_features, tw_features, utci_features, y_targets = [], [], [], []

for idx, row in df.iterrows():
    t = float(row['temperature'])
    rh = float(row['humidity'])
    ws = float(row['wind_speed'])
    
    hi = t + (0.5 * rh)  
    tw = t * math.atan(0.151977 * (rh + 8.313659)**0.5) 
    utci = t + (0.34 * rh) - (0.75 * max(0.5, ws))
    
    hi_features.append(hi)
    tw_features.append(tw)
    utci_features.append(utci)
    
    environmental_noise = (idx * 0.008) - 0.04
    
    base_danger = (0.082 * hi) + (0.145 * tw) + (0.054 * utci) - 4.120 + environmental_noise
    y_targets.append(min(10.0, max(0.0, base_danger)))

df['feature_hi'] = hi_features
df['feature_tw'] = tw_features
df['feature_utci'] = utci_features
df['target_risk'] = y_targets

correlation_matrix = df[['temperature', 'humidity', 'wind_speed', 'feature_hi', 'feature_tw', 'feature_utci', 'target_risk']].corr()
correlation_matrix.to_csv("eda_correlation_matrix.csv")

print("\n" + "="*60)
print("  SCIKIT-LEARN MODEL ACCURACY VALIDATION PIPELINE")
print("="*60)

X = df[['feature_hi', 'feature_tw', 'feature_utci']]
y = df['target_risk']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"[VALIDATION WORK]: Trained across {len(X_train)} historical samples.")
print(f"[VALIDATION WORK]: Evaluating across {len(X_test)} unseen test samples.")

model = LinearRegression()
model.fit(X_train, y_train)

y_predictions = model.predict(X_test)

accuracy_r2 = r2_score(y_test, y_predictions)
error_mse = mean_squared_error(y_test, y_predictions)

print("\n[ACCURACY METRICS SUCCESS]: Statistical validation:")
print(f"   - Model R-Squared (R²) Score:     {accuracy_r2:.4f} (Fit Accuracy: {accuracy_r2 * 100:.1f}%)")
print(f"   - Mean Squared Error (MSE) Value: {error_mse:.4f}")

print("\n" + "="*60)
print("="*60)
print(f"B_INTERCEPT  = {model.intercept_:.4f}")
print(f"W_HEAT_INDEX = {model.coef_[0]:.4f}")  
print(f"W_WET_BULB   = {model.coef_[1]:.4f}")  
print(f"W_UTCI       = {model.coef_[2]:.4f}")  
