# ParkSmart — SJSU Parking Availability Prediction System

> *Not officially affiliated with San Jose State University.*

A **data-driven web application** that helps SJSU students and faculty make informed decisions about parking by predicting garage availability. An automated **AWS Lambda** scraper collects occupancy data from all four SJSU parking garages every 15 minutes, storing time-series records in **AWS S3**. A trained **MLPRegressor** neural network predicts future occupancy, and a **Streamlit** dashboard surfaces both historical trends and ML-based predictions.

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.11+ |
| Cloud Functions | AWS Lambda (serverless) |
| Cloud Storage | AWS S3 (`sjsu-parking-data`) |
| AWS SDK | Boto3 |
| Web Scraping | BeautifulSoup4, Requests |
| Data Format | CSV (time-series) |
| ML Model | scikit-learn MLPRegressor, StandardScaler |
| Model Persistence | joblib |
| Dashboard | Streamlit |
| Visualisation | Matplotlib, Pandas |
| Time Handling | `zoneinfo` (America/Los_Angeles), `datetime` |

---

## Architecture

```
CloudWatch Events (every 15 min)
        │
        ▼
  AWS Lambda  ──► parking_scraper_aws.py
        │
        │  HTTP GET (SSL disabled)
        ▼
  sjsuparkingstatus.sjsu.edu
        │
        │  BeautifulSoup4 + regex parse
        ▼
  Occupancy rows (4 garages)
        │
        │  Boto3 append-or-create
        ▼
  AWS S3  ──► north_garage.csv
              south_garage.csv
              west_garage.csv
              south_campus_garage.csv
        │
        ├──► predictions/parking_predictor.py  (MLPRegressor per garage)
        │
        ▼
  Streamlit Dashboard  ──► parking_ui.py
```

---

## File Structure

```
ParkSmart/
├── parking_scraper_aws.py        # AWS Lambda handler — scrape, parse, store
├── parking_ui.py                 # Streamlit dashboard with ML predictions
├── plot_parking_data.py          # Standalone Matplotlib visualisation script
├── scrapingLocal.py              # Local dev scraper (15-min loop)
├── transform_csv.py              # One-time migration utility (legacy schema → current)
├── north_garage.csv              # Historical data — North Garage
├── south_garage.csv              # Historical data — South Garage
├── south_campus_garage.csv       # Historical data — South Campus Garage
├── west_garage.csv               # Historical data — West Garage
├── parking_occupancy_by_day.png  # Static occupancy visualisation
├── predictions/
│   ├── parking_predictor.py      # ParkingPredictor class (train, predict, save/load)
│   └── models/                   # Trained model and scaler files (.joblib)
│       ├── north_garage_model.joblib
│       ├── north_garage_scaler.joblib
│       ├── south_garage_model.joblib
│       ├── south_garage_scaler.joblib
│       ├── west_garage_model.joblib
│       ├── west_garage_scaler.joblib
│       ├── south_campus_garage_model.joblib
│       └── south_campus_garage_scaler.joblib
├── requirements.txt
└── README.md
```

---

## Data Schema

Each CSV file uses the following columns:

| Column | Description |
|---|---|
| `Timestamp` | ISO datetime in Pacific Time (`YYYY-MM-DD HH:MM:SS`) |
| `Garage Name` | One of: North, South, West, South Campus Garage |
| `Occupancy` | Integer 0–100 (`100` replaces the portal's "full" label) |
| `Last Updated Day` | Day of week from the portal's "Last updated" field |
| `Last Updated Month` | Month name |
| `Last Updated Date` | Date string from the SJSU portal |
| `Last Updated Time` | Time string (e.g. `10:45 AM`) from the SJSU portal |

---

## ML Model

`predictions/parking_predictor.py` trains a separate **MLPRegressor** (neural network with hidden layers `[100, 50]`, ReLU activation, Adam solver) for each of the four garages.

**Features used:**
- Hour of day
- Day of week (numeric + one-hot encoded)
- Garage identity (one-hot encoded)

**Output:** predicted occupancy percentage (0–100)

**`get_best_garage(date, hour)`** runs predictions across all four garages and returns the lowest-occupancy recommendation along with alternatives under 90%.

---

## Setup

```bash
pip install -r requirements.txt
```

**Run the Streamlit dashboard:**

```bash
streamlit run parking_ui.py
```

**Retrain ML models** (if you have new CSV data):

```bash
python predictions/parking_predictor.py
```

**Run the local scraper** (collects data every 15 minutes):

```bash
python scrapingLocal.py
```

**Generate the static occupancy chart:**

```bash
python plot_parking_data.py
```

---

## AWS Lambda Deployment

`parking_scraper_aws.py` is deployed as a Lambda function triggered by an **Amazon EventBridge** rule on a `rate(15 minutes)` schedule.

**Required Lambda environment:**
- IAM role with `s3:GetObject` and `s3:PutObject` on the `sjsu-parking-data` bucket
- Python 3.11 runtime
- Dependencies packaged in a Lambda layer: `beautifulsoup4`, `requests`, `boto3`, `urllib3`

---

## Development Roadmap

| Phase | Status | Description |
|---|---|---|
| 1 — Data Collection | ✅ Complete | Lambda scraper + S3 storage pipeline |
| 2 — ML Modelling | ✅ Complete | MLPRegressor trained per garage, models saved with joblib |
| 3 — Predictive UI | ✅ Complete | Streamlit dashboard with live predictions and historical trends |

---

## Contributors

- Ashwabh Bhatnagar
