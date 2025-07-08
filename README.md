# Pollution Data Visualizer

This project is a simple Flask web application that collects air quality data from the AQICN API and visualizes it.
It provides a responsive interface with dark and light themes, search suggestions, and historical AQI charts.

## Features
- Search for a city to retrieve its latest Air Quality Index (AQI).
- Store historical AQI data in a local SQLite database.
- REST endpoints to fetch real-time, historical and average AQI values.
- About page and summary API endpoint.
- Basic unit tests for the data collector and application routes.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python app.py
   ```
The application will be available at `http://localhost:5000`.
Navigate to `/about` for project information. Use `/api/summary` to fetch average AQI for several cities.

## Running Tests
Use pytest to run the test suite:
```bash
PYTHONPATH=. pytest -q
```

