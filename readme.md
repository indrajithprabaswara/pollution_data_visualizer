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
 - Cloud Scheduler triggers a Pub/Sub message every 30 minutes to collect AQI data.
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
2. Set environment variables and run:
   ```bash
   export WAQI_TOKEN=<your_token>
   export SECRET_KEY=<secret>
   python pollution_data_visualizer/app.py
   ```
The application will be available at `http://localhost:5000`.
Navigate to `/about` for project information. Use `/api/summary` to fetch average AQI for several cities.
Metrics are exposed at `/metrics` for Prometheus scraping.

For production, you can start the app with Gunicorn:
```bash
gunicorn -w 4 -k eventlet -b 0.0.0.0:8000 wsgi:app
```

### Docker

Build and run with:

```bash
docker build -t pollution-app .
docker run -e WAQI_TOKEN=<token> -e SECRET_KEY=<secret> -p8080:8080 pollution-app
```


## Running Tests
Use pytest to run the test suite:
```bash
PYTHONPATH=. pytest -q
```
To run the JavaScript tests:
```bash
npm test --silent
```



## Continuous Integration and Delivery
The `ci.yml` workflow runs unit and integration tests. The `cd.yml` workflow builds the image using the root `Dockerfile` and pushes it to GitHub Container Registry when changes land on the `main` branch.

## A-Level Requirements Checklist

The project implements every item from the A-level specification. Each entry
below links to the relevant lines in the repository so you can verify the code
yourself.

- **Web application with form and reporting** – the search form is defined in
  `templates/index.html` lines 3‑18 and the Flask routes that serve pages and
  reports live in `app.py` lines 68‑187【F:pollution_data_visualizer/templates/index.html†L1-L18】【F:pollution_data_visualizer/app.py†L68-L187】.
- **Data collection** – `fetch_air_quality` and `collect_data` retrieve and
  store measurements. See `data_collector.py` lines 7‑44【F:pollution_data_visualizer/data_collector.py†L7-L44】.
- **Data analyzer** – helper functions to compute recent data and averages are
  located in `data_analyzer.py` lines 4‑36【F:pollution_data_visualizer/data_analyzer.py†L4-L36】.
- **Unit tests** – `tests/test_data_collector.py` lines 10‑29 mock the HTTP
  call and verify parsing logic【F:pollution_data_visualizer/tests/test_data_collector.py†L10-L29】.
- **Data persistence** – SQLAlchemy models store readings in a SQLite database;
  these are in `models.py` lines 5‑40【F:pollution_data_visualizer/models.py†L5-L40】.
- **REST collaboration** – JSON endpoints for history, averages and coordinates
  are implemented in `app.py` lines 83‑187【F:pollution_data_visualizer/app.py†L83-L187】.
- **Product environment** – the Docker image is built using
  `Dockerfile` lines 1‑15【F:Dockerfile†L1-L15】.
- **Integration tests** – the full application flow is checked in
  `tests/test_integration.py` lines 19‑30【F:pollution_data_visualizer/tests/test_integration.py†L19-L30】.
- **Mock objects or test doubles** – `tests/test_e2e.py` uses
  `unittest.mock.patch` to replace functions as shown on lines 26‑35【F:pollution_data_visualizer/tests/test_e2e.py†L26-L35】.
- **Continuous integration** – GitHub Actions configuration in
  `.github/workflows/ci.yml` lines 1‑45 installs dependencies and runs the test
  suites【F:.github/workflows/ci.yml†L1-L45】.
- **Production monitoring** – Prometheus counters and gauges are updated in
  `app.py` lines 22‑37 and exposed at `/metrics` in lines 187‑189【F:pollution_data_visualizer/app.py†L22-L37】【F:pollution_data_visualizer/app.py†L187-L189】.
- **Event collaboration messaging** – events are queued in
  `events.py` lines 11‑29 and triggered in `scheduled_collection` and `search`
  (`app.py` lines 49‑52 and 132‑135)【F:pollution_data_visualizer/events.py†L11-L29】【F:pollution_data_visualizer/app.py†L49-L52】【F:pollution_data_visualizer/app.py†L132-L135】.
- **Continuous delivery** – automated container builds and pushes are handled by
  `.github/workflows/cd.yml` lines 1‑34【F:.github/workflows/cd.yml†L1-L34】.
\nData courtesy of World Air Quality Index Project and EPA.
