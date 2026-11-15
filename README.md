# Login Behavior Anomaly Detection

A machine learning-based system that detects suspicious login attempts by analyzing user behavior patterns. It uses an Isolation Forest model to identify anomalies in login activities based on time, location, and device information.

## 📋 Project Overview

This project implements an anomaly detection system for login behavior with the following features:

- **Real-time Anomaly Detection**: Analyzes login attempts to identify suspicious activities
- **Multi-factor Analysis**: Considers time of day, day of week, country, and device type
- **Web API**: Flask-based REST API for making predictions
- **Interactive Frontend**: User-friendly web interface for testing predictions
- **Machine Learning Model**: Uses Isolation Forest algorithm for unsupervised anomaly detection

## 🛠️ Technology Stack

- **Backend Framework**: Flask
- **Machine Learning**: scikit-learn (Isolation Forest)
- **Data Processing**: Pandas, NumPy
- **Frontend**: HTML/CSS/JavaScript
- **CORS Support**: Flask-CORS
- **Model Serialization**: Joblib

## 📁 Project Structure

```
login-behavior-anomaly-detection/
├── app.py                 # Flask application and API endpoints
├── train_model.py         # Model training script
├── data.py                # Synthetic data generation script
├── login_data.csv         # Training dataset
├── anomaly_rules.json     # Anomaly detection rules configuration
├── mappings.json          # Feature encoding mappings
├── login_anomaly_model.pkl # Trained ML model (generated after training)
└── templates/
    ├── index.html         # Main application page
    └── home.html          # Home/dashboard page
```

## 📦 Installation

### Prerequisites

- **Python 3.10+** installed on your system
- **pip** (Python package manager)
- Windows Command Prompt or PowerShell (or any terminal for Linux/Mac)

### Step 1: Clone or Download the Project

```bash
cd login-behavior-anomaly-detection
```

### Step 2: Create a Virtual Environment (Recommended)

This isolates project dependencies from your system Python:

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Running the Project

### Step 1: Generate Training Data

Generate synthetic login data with anomalies:

```bash
python data.py
```

**Output**: Creates `login_data.csv` with 1000 login records (95% normal, 5% anomalies)

**What it does**:
- Generates normal login patterns: US- and India-based logins during business hours (9 AM - 6 PM, Mon-Fri) on standard devices
- Generates anomalous patterns: Late-night logins, suspicious countries (CN, RU, IN, BR, KP, NG), and unknown devices. India appears in both classes, so it is not a deterministic block rule.

### Step 2: Train the Machine Learning Model

Train the Isolation Forest model using the generated data:

```bash
python train_model.py
```

**Output**: 
- `login_anomaly_model.pkl` - Trained model file
- `mappings.json` - Feature encoding mappings for the model
- Console output showing dataset statistics and anomaly rate

**What it does**:
- Loads the login data
- Creates feature mappings for countries and devices
- Trains an Isolation Forest model with contamination rate matching actual anomalies
- Saves the model and mappings for the API to use

### Step 3: Run the Flask Application

Start the web server:

```bash
python app.py
```

**Expected Output**:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: off
```

**Note**: If you see an error about missing model, ensure you completed Step 1 and Step 2 first.

### Step 4: Access the Web Interface

Open your web browser and navigate to:

```
http://localhost:5000
```

or

```
http://127.0.0.1:5000
```

You should see the anomaly detection interface where you can:
- Enter a username
- Specify login time (hour and day)
- Select country and device
- Click "Check Login" to get anomaly analysis

## 📊 How the Anomaly Detection Works

### Features Used

The model analyzes four key features:

1. **Hour** (0-23): Time of day when login occurred
   - Normal: 9 AM - 6 PM (09:00 - 18:00)
   - Anomalous: Midnight to 4 AM, 9 PM - 11 PM

2. **Day of Week** (0-6): Day when login occurred (0=Monday, 6=Sunday)
   - Normal: Monday - Friday (0-4)
   - Anomalous: Saturday & Sunday (5-6)

3. **Country**: Geographic location of login
   - Normal: US
   - Anomalous: CN, RU, IN, BR, KP, NG, etc.

4. **Device**: Device identifier used for login
   - Normal: DEV-A100, DEV-B200 (standard devices)
   - Anomalous: DEV-X999, DEV-UNK1, DEV-TEMP, DEV-PROXY

### Anomaly Scoring

The Isolation Forest algorithm identifies anomalies by:
- Building random decision trees on feature subsets
- Isolating anomalies in fewer steps than normal points
- Assigning anomaly scores based on isolation distance

**Prediction Output**:
- **-1**: Anomaly detected (suspicious login)
- **+1**: Normal login activity

## 🔌 API Endpoints

### POST /api/v1/login

The same handler is also available at `POST /api/login-check` and the legacy
`POST /login` route. The API validates the request and combines the model
prediction with the rules in `anomaly_rules.json`.

**Purpose**: Analyze a login attempt for anomalies

**Request Format**:
```json
{
  "username": "john_doe",
  "hour": 14,
  "day": 2,
  "country": "US",
  "device": "DEV-A100"
}
```

**Request Parameters**:
- `username` (string, required): Username attempting to login
- `hour` (integer, 0-23, optional): Hour of login (defaults to current hour)
- `day` (integer, 0-6, optional): Day of week (0=Monday, defaults to current day)
- `country` (string, optional): Country code (default: "US")
- `device` (string, optional): Known device identifier (default: `DEV-A100`)

**Response Format** (Normal Login):
```json
{
  "status": "success",
  "username": "john_doe",
  "login_analysis": "Login Verified",
  "decision": "ALLOW",
  "anomaly_score": 0.12,
  "is_anomaly": false,
  "features_analyzed": {
    "hour": 14,
    "day": 2,
    "country": "US",
    "device": "DEV-A100"
  },
  "features_used": [[14, 2, 6, 0]],
  "reasons": []
}
```

**Response Format** (Anomalous Login):
```json
{
  "status": "success",
  "username": "attacker",
  "login_analysis": "Login blocked by security policy.",
  "decision": "BLOCK",
  "is_anomaly": true,
  "features_analyzed": {
    "hour": 2,
    "day": 5,
    "country": "RU",
    "device": "DEV-X999"
  },
  "features_used": [[2, 5, 5, 5]],
  "reasons": [
    "Unusual hour: 2",
    "Suspicious country: RU"
  ]
}
```

### GET /

Serves the main HTML interface (index.html)

### GET /home

Serves the home/dashboard page (home.html)

## 🧪 Testing the System

### Using the Web Interface

1. Fill in the login form with test data
2. Click "Check Login" button
3. View the analysis results

### Using curl (Command Line)

Test with a normal login:
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","hour":10,"day":1,"country":"US","device":"DEV-A100"}'
```

Test with a suspicious login:
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"hacker","hour":2,"day":5,"country":"RU","device":"DEV-X999"}'
```

### Using Python Requests

```python
import requests

# Test normal login
response = requests.post('http://localhost:5000/login', json={
    "username": "user1",
    "hour": 14,
    "day": 2,
    "country": "US",
    "device": "DEV-A100"
})
print(response.json())

# Test anomalous login
response = requests.post('http://localhost:5000/login', json={
    "username": "hacker",
    "hour": 3,
    "day": 5,
    "country": "CN",
    "device": "DEV-PROXY"
})
print(response.json())
```

## ⚙️ Configuration Files

### mappings.json

Contains encoding mappings for categorical features:
```json
{
  "country_map": {
    "BR": 0,
    "CN": 1,
    "IN": 2,
    "KP": 3,
    "NG": 4,
    "RU": 5,
    "US": 6
  },
  "device_map": {
    "DEV-A100": 0,
    "DEV-B200": 1,
    "DEV-PROXY": 2,
    "DEV-TEMP": 3,
    "DEV-UNK1": 4,
    "DEV-X999": 5
  }
}
```

### anomaly_rules.json

Contains active rule-based checks used by the API:
```json
{
  "suspicious_hours": [0, 1, 2, 3, 23],
  "suspicious_countries": ["CN", "BR", "RU", "KP", "NG"],
  "suspicious_devices": ["DEV-X999", "DEV-PROXY", "DEV-TEMP", "DEV-UNK1"],
  "normal_days": [0, 1, 2, 3, 4],
  "normal_country": "US",
  "normal_device": ["DEV-A100", "DEV-B200"]
}
```

Suspicious countries are blocked. Suspicious devices, suspicious hours,
weekend logins, and model anomalies trigger MFA.

## 🐛 Troubleshooting

### Issue: "Detection model or configuration is unavailable"

**Solution**: 
1. Check that `login_anomaly_model.pkl`, `mappings.json`, and
   `anomaly_rules.json` exist in the project directory.
2. If the model or mappings are missing, run `python data.py` and then
   `python train_model.py`.
3. Run `python app.py`.

### Issue: "FileNotFoundError: login_data.csv"

**Solution**: Run `python data.py` from the project directory to generate the dataset.

### Issue: "Port 5000 already in use"

**Solution**: Change the port in app.py:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change to 5001 or another available port
```

### Issue: Module not found errors (ImportError)

**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: CORS errors in browser console

**Solution**: Flask-CORS is already configured in app.py. If issues persist, ensure CORS is enabled in the browser or check network settings.

## 📈 Model Performance Metrics

The model is trained with:
- **Dataset Size**: 1000 login records
- **Anomaly Rate**: 5% (50 anomalies)
- **Algorithm**: Isolation Forest with 100 estimators
- **Features**: 4 (hour, day_of_week, country_encoded, device_encoded)
- **Training Method**: Unsupervised learning

## 🔒 Security Notes

This is a demonstration project. For production use:
- Implement proper authentication (JWT, OAuth)
- Use environment variables for sensitive data
- Validate and sanitize all inputs
- Use HTTPS instead of HTTP
- Implement rate limiting
- Add logging and monitoring
- Use a production-grade web server (Gunicorn, uWSGI)
- Store models securely with access controls

## 📝 Example Workflow

1. **First Time Setup**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # or: source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Prepare Data**:
   ```bash
   python data.py
   ```

3. **Train Model**:
   ```bash
   python train_model.py
   ```

4. **Run Application**:
   ```bash
   python app.py
   ```

5. **Test in Browser**:
   Open http://localhost:5000

## 🤝 Contributing

To modify the system:
- Adjust anomaly generation parameters in `data.py`
- Modify model hyperparameters in `train_model.py`
- Add new features in both scripts
- Update the HTML/CSS templates for UI changes

## 📚 References

- [scikit-learn Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pandas Documentation](https://pandas.pydata.org/)

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## ✅ Completion Checklist

- [x] Generate synthetic data with `python data.py`
- [x] Train the model with `python train_model.py`
- [x] Run the Flask app with `python app.py`
- [x] Access the web interface at `http://localhost:5000`
- [x] Test anomaly detection with sample logins
- [x] Review API responses in the console

---

**Last Updated**: January 3, 2026

For questions or issues, refer to the troubleshooting section above.
