# ParkSmart — SJSU Parking Availability Prediction System

> *Not officially affiliated with San Jose State University.*

A **data-driven web application** that helps SJSU students and faculty make informed decisions about parking by predicting garage availability. An automated **AWS Lambda** scraper collects occupancy data from all four SJSU parking garages every 15 minutes, storing time-series records in **AWS S3**. A **Streamlit** dashboard visualises historical trends and occupancy patterns.

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
        ▼
  Streamlit Dashboard  ──► parking_ui.py
```

---

## File Structure

```
ParkSmart/
├── parking_scraper_aws.py     # AWS Lambda handler — scrape, parse, store
├── parking_ui.py              # Streamlit dashboard
├── plot_parking_data.py       # Standalone Matplotlib visualisation script
├── scrapingLocal.py           # Local dev scraper (runs every 15 min via sleep loop)
├── transform_csv.py           # One-time migration utility (legacy schema → current)
├── north_garage.csv           # Historical data — North Garage
├── south_garage.csv           # Historical data — South Garage
├── south_campus_garage.csv    # Historical data — South Campus Garage
├── west_garage.csv            # Historical data — West Garage
├── parking_occupancy_by_day.png  # Static occupancy visualisation
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

## Setup

```bash
pip install -r requirements.txt
```

**Run the Streamlit dashboard** (reads local CSV files):

```bash
streamlit run parking_ui.py
```

**Run the local scraper** (collects data every 15 minutes):

```bash
python scrapingLocal.py
```

**Generate the static occupancy chart**:

```bash
python plot_parking_data.py
```

---

## AWS Lambda Deployment

`parking_scraper_aws.py` is deployed as a Lambda function triggered by an **Amazon EventBridge** (CloudWatch Events) rule on a `rate(15 minutes)` schedule.

```
S3 append-or-create pattern:
  try:
      existing = s3.get_object(Bucket=bucket, Key=key)  # read existing CSV
  except NoSuchKey:
      write header row first              # new file
  append new row → s3.put_object(...)     # write back
```

**Required Lambda environment:**
- IAM role with `s3:GetObject` and `s3:PutObject` on the `sjsu-parking-data` bucket
- Python 3.11 runtime
- Dependencies packaged in a Lambda layer: `beautifulsoup4`, `requests`, `boto3`, `urllib3`

---

## Development Roadmap

| Phase | Status | Description |
|---|---|---|
| 1 — Data Collection | ✅ Complete | Lambda scraper + S3 storage pipeline |
| 2 — ML Modelling | 🔄 In Progress | Train time-series occupancy forecasting models on collected data |
| 3 — Predictive UI | 📋 Planned | Integrate model predictions into the Streamlit dashboard |

---

## Key Design Decisions

- **Lambda over EC2** — charges per invocation; far cheaper than an always-on instance for a 15-minute polling job.
- **S3 CSV over a database** — zero operational overhead; the append-or-create pattern keeps the pipeline simple while the dataset is still small.
- **`zoneinfo` for Pacific Time** — ensures timestamps reflect local campus time regardless of where Lambda executes.
- **Regex on raw text** — the SJSU portal's HTML structure is inconsistent; extracting from `soup.get_text()` with a targeted pattern is more robust than navigating the DOM.

---

## Contributors

- Ashwabh Bhatnagar
