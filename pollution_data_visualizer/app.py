from flask import Flask, render_template, jsonify, request
from config import Config
from models import db
from data_collector import collect_data, collect_data_for_multiple_cities
from data_analyzer import get_average_aqi, get_recent_aqi, get_aqi_history
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


@app.before_first_request
def setup_database():
    """Ensure database tables exist."""
    db.create_all()

# Route to show the main page with a search bar
@app.route('/')
def index():
    return render_template('index.html')

# Simple about page
@app.route('/about')
def about():
    return render_template('about.html')

# Route to get real-time data for a specific city
@app.route('/data/<city>')
def get_city_data(city):
    try:
        collect_data(city)  # Collect the latest data
        recent_aqi = get_recent_aqi(city)
        return jsonify({"city": city, "aqi": recent_aqi})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to get AQI history for the last 24 hours
@app.route('/data/history/<city>')
def get_city_history(city):
    try:
        history = get_aqi_history(city)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to get the average AQI for a city in the past 7 days
@app.route('/data/average/<city>')
def get_average(city):
    try:
        start_date = datetime.now() - timedelta(days=7)
        average_aqi = get_average_aqi(city, start_date, datetime.now())
        return jsonify({"city": city, "average_aqi": average_aqi})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to handle search requests
@app.route('/search', methods=['GET'])
def search():
    city = request.args.get('city')
    if city:
        collect_data(city)  # Collect new data for the city
        recent_aqi = get_recent_aqi(city)
        return render_template('index.html', city=city, aqi=recent_aqi)
    return render_template('index.html', error="City not found!")

# Collect data for multiple cities (could be triggered on a schedule or manually)
@app.route('/collect_data_for_multiple')
def collect_data_multiple():
    cities = ['New York', 'Los Angeles', 'Chicago', 'San Francisco', 'Houston', 'Beijing', 'London']
    collect_data_for_multiple_cities(cities)
    return jsonify({"status": "Data collection for multiple cities is complete!"})

# Provide a summary of average AQI for a list of cities
@app.route('/api/summary')
def api_summary():
    cities = request.args.getlist('city') or ['New York', 'Los Angeles', 'Chicago']
    result = {}
    for city in cities:
        start_date = datetime.now() - timedelta(days=1)
        avg = get_average_aqi(city, start_date, datetime.now())
        result[city] = avg
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
