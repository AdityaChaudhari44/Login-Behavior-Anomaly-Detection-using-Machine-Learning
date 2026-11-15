"""Train and save the Isolation Forest used by app.py."""

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "login_data.csv"
MODEL_PATH = BASE_DIR / "login_anomaly_model.pkl"
MAPPINGS_PATH = BASE_DIR / "mappings.json"
FEATURE_COLUMNS = ["hour", "day_of_week", "country_encoded", "device_encoded"]
REQUIRED_COLUMNS = {"hour", "day_of_week", "country_code", "device_code", "label"}


def train_model():
    if not DATA_PATH.is_file():
        raise FileNotFoundError(f"Training data not found: {DATA_PATH}. Run data.py first.")

    dataset = pd.read_csv(DATA_PATH)
    missing = REQUIRED_COLUMNS.difference(dataset.columns)
    if missing:
        raise ValueError(f"Training data is missing columns: {', '.join(sorted(missing))}")
    if dataset.empty:
        raise ValueError("Training data is empty.")

    for column, minimum, maximum in (("hour", 0, 23), ("day_of_week", 0, 6)):
        values = pd.to_numeric(dataset[column], errors="coerce")
        if values.isna().any() or not values.between(minimum, maximum).all():
            raise ValueError(f"{column} values must be integers from {minimum} to {maximum}.")
        if not (values % 1 == 0).all():
            raise ValueError(f"{column} values must be whole numbers.")
        dataset[column] = values.astype(int)

    labels = pd.to_numeric(dataset["label"], errors="coerce")
    if labels.isna().any() or not labels.isin([0, 1]).all():
        raise ValueError("Training labels must be 0 (normal) or 1 (anomaly).")
    dataset["label"] = labels.astype(int)

    country_map = {
        country: index
        for index, country in enumerate(sorted(dataset["country_code"].dropna().unique()))
    }
    device_map = {
        device: index
        for index, device in enumerate(sorted(dataset["device_code"].dropna().unique()))
    }
    dataset["country_encoded"] = dataset["country_code"].map(country_map)
    dataset["device_encoded"] = dataset["device_code"].map(device_map)

    if dataset[FEATURE_COLUMNS].isna().any().any():
        raise ValueError("Training features contain missing or unmapped values.")
    X = dataset[FEATURE_COLUMNS].to_numpy()
    anomaly_rate = float(dataset["label"].mean())
    if not 0 < anomaly_rate < 0.5:
        raise ValueError("Training labels must contain some anomalies and mostly normal records.")

    model = IsolationForest(
        contamination=anomaly_rate,
        random_state=42,
        n_estimators=100,
    )
    model.fit(X)
    joblib.dump(model, MODEL_PATH)

    mappings = {
        "country_map": country_map,
        "device_map": device_map,
        "reverse_country_map": {str(code): name for name, code in country_map.items()},
        "reverse_device_map": {str(code): name for name, code in device_map.items()},
    }
    MAPPINGS_PATH.write_text(json.dumps(mappings, indent=2), encoding="utf-8")

    print(f"Trained model from {len(dataset)} login records.")
    print(f"Model saved to {MODEL_PATH}")
    print(f"Feature mappings saved to {MAPPINGS_PATH}")
    print(f"Training contamination: {anomaly_rate:.1%}")


if __name__ == "__main__":
    train_model()
