Hey, this is the project overview.

# Pollution Data Visualizer

This project is a Flask web application that collects air quality data from the AQICN API and visualizes it.
The interface uses Bootstrap together with Tailwind CSS for a modern look. Global search suggestions, animated charts and a theme toggle provide an interactive experience. City cards highlight when added and expand for detailed metrics and advice.

## Features
- Search for a city to retrieve its latest Air Quality Index (AQI).
- View additional metrics such as PM2.5, CO and NO2.
- Store historical AQI data in a local SQLite database.
- REST endpoints to fetch real-time, historical and average AQI values. Use `/data/history/<city>?hours=48` or `/data/history_multi?city=A&city=B` for comparisons.
- About page and summary API endpoint.
- Offcanvas drawer showing detailed charts, progress bars and pollution advice.
- Global city suggestions when searching.
- Basic unit tests for the data collector and application routes.
- Automatic data refresh every 30 minutes for displayed cities.
- Background scheduler stores AQI data every 30 minutes for all monitored cities.
- Tailwind CSS styling with gradient hero section and animated typewriter heading.
- Animated line and pie charts that update smoothly with a toggle to switch chart type.
- Real-time updates using WebSockets so cards refresh automatically.
- Interactive world map shows cities with markers.
- Autocomplete search with jQuery UI.
- Color-coded map markers based on AQI levels.
- Save favorite cities locally with optional AQI alerts.
- Compare multiple cities with a side-by-side chart.
- Prometheus `/metrics` endpoint for monitoring.
- Simple internal event queue used for background notifications.
- Delhi, Perth and Paris are shown by default when the app loads.

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
Metrics are exposed at `/metrics` for Prometheus scraping.

For production, you can start the app with Gunicorn:
```bash
gunicorn -w 4 -k eventlet -b 0.0.0.0:8000 wsgi:app
```

## Running Tests
Use pytest to run the test suite:
```bash
PYTHONPATH=. pytest -q
```


## Continuous Integration and Delivery
This repository uses GitHub Actions for automated testing and delivery.
The `ci.yml` workflow runs unit and integration tests for both Python and JavaScript
and builds the Docker image. The `cd.yml` workflow pushes the built image
to GitHub Container Registry whenever changes land on the `main` branch.
