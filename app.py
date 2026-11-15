"""Flask API and web UI for login behavior anomaly detection."""

from datetime import datetime
import json
from pathlib import Path

import joblib
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "login_anomaly_model.pkl"
MAPPINGS_PATH = BASE_DIR / "mappings.json"
RULES_PATH = BASE_DIR / "anomaly_rules.json"

app = Flask(__name__)
CORS(app)


def load_json(path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


try:
    model = joblib.load(MODEL_PATH)
    mappings = load_json(MAPPINGS_PATH)
    rules = load_json(RULES_PATH)
except Exception as exc:
    # Keep the web server available so its API can return a useful setup error.
    model = mappings = rules = None
    print(f"Could not load detection files: {exc}")


def error_response(message, status):
    return jsonify({"status": "error", "message": message}), status


def evaluate_rules(hour, day, country, device):
    """Return rule hits with severity; configured rule arrays are optional."""
    hits = []
    if country in rules.get("suspicious_countries", []):
        hits.append({"rule": "suspicious_country", "severity": "block",
                     "reason": f"Suspicious country: {country}"})
    if device in rules.get("suspicious_devices", []):
        hits.append({"rule": "suspicious_device", "severity": "mfa",
                     "reason": f"Unrecognized device: {device}"})
    if hour in rules.get("suspicious_hours", []):
        hits.append({"rule": "suspicious_hour", "severity": "mfa",
                     "reason": f"Unusual login hour: {hour}"})
    if day not in rules.get("normal_days", list(range(5))):
        hits.append({"rule": "weekend_login", "severity": "mfa",
                     "reason": "Login occurred on a weekend"})
    return hits


@app.get("/")
def serve_index():
    return render_template("index.html")


@app.post("/login")
@app.post("/api/login-check")
@app.post("/api/v1/login")
def login():
    if model is None or mappings is None or rules is None:
        return error_response("Detection model or configuration is unavailable. Run train_model.py first.", 503)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error_response("Request body must be a JSON object.", 400)

    username = str(payload.get("username", "")).strip()
    if not username:
        return error_response("username is required.", 400)

    try:
        hour = int(payload.get("hour", datetime.now().hour))
        day = int(payload.get("day", datetime.now().weekday()))
    except (TypeError, ValueError):
        return error_response("hour and day must be integers.", 400)
    if not 0 <= hour <= 23 or not 0 <= day <= 6:
        return error_response("hour must be 0-23 and day must be 0-6 (Monday=0).", 400)

    country = str(payload.get("country", "US")).strip().upper()
    device = str(payload.get("device", "DEV-A100")).strip().upper()
    country_map = mappings.get("country_map", {})
    device_map = mappings.get("device_map", {})
    if country not in country_map:
        return error_response(f"Unsupported country code: {country}.", 400)
    if device not in device_map:
        return error_response(f"Unsupported device: {device}.", 400)

    features = [[hour, day, country_map[country], device_map[device]]]
    prediction = int(model.predict(features)[0])
    anomaly_score = float(model.decision_function(features)[0])
    rule_hits = evaluate_rules(hour, day, country, device)

    if any(hit["severity"] == "block" for hit in rule_hits):
        decision = "BLOCK"
    elif rule_hits or prediction == -1:
        decision = "TRIGGER_MFA"
    else:
        decision = "ALLOW"

    return jsonify({
        "status": "success",
        "username": username,
        "decision": decision,
        "is_anomaly": decision != "ALLOW",
        "prediction": prediction,
        "anomaly_score": anomaly_score,
        "login_analysis": {
            "ALLOW": "Login verified.",
            "TRIGGER_MFA": "Additional verification is required.",
            "BLOCK": "Login blocked by security policy.",
        }[decision],
        "reasons": [hit["reason"] for hit in rule_hits]
        or (["Machine learning model flagged unusual behavior."] if prediction == -1 else []),
        "features_analyzed": {
            "hour": hour, "day": day, "country": country, "device": device,
        },
        "features_used": features,
    })


@app.get("/home")
def serve_home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=False, port=5000)
