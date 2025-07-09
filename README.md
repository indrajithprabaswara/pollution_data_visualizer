# Pollution Data Visualizer

This project is a Flask web application that collects air quality data from the AQICN API and visualizes it.
The interface uses Bootstrap together with Tailwind CSS for a modern look. Global search suggestions, animated charts and a theme toggle provide an interactive experience. City cards highlight when added and expand for detailed metrics and advice.

## Features
- Search for a city to retrieve its latest Air Quality Index (AQI).
- View additional metrics such as PM2.5, CO and NO2.
- Store historical AQI data in a local SQLite database.
- REST endpoints to fetch real-time, historical and average AQI values. Use `/data/history/<city>?hours=48` to specify the time range.
- About page and summary API endpoint.
- Offcanvas drawer showing detailed charts, progress bars and pollution advice.
- Global city suggestions when searching.
- Basic unit tests for the data collector and application routes.
- Automatic data refresh every minute for displayed cities.
- Background scheduler stores AQI data every 30 minutes for all monitored cities.
- Tailwind CSS styling with gradient hero section and animated typewriter heading.
- Animated line and pie charts that update smoothly with a toggle to switch chart type.

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

