from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_socketio import SocketIO
from prometheus_client import Counter, Gauge, generate_latest
from events import publish_event, start_consumer
from config import Config
from models import db, PollutionRecord
from data_collector import collect_data, collect_data_for_multiple_cities
from data_analyzer import get_average_aqi, get_recent_aqi, get_aqi_history
from models import User, FavoriteCity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import os

monitored_cities = ['New York', 'Los Angeles', 'San Francisco', 'Paris', 'Delhi', 'Perth']

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
socketio = SocketIO(app, async_mode='threading')

REQUEST_COUNT = Counter('request_count', 'Total HTTP requests', ['method', 'endpoint'])
AQI_GAUGE = Gauge('stored_aqi_records', 'Number of AQI records in the database')

def _log_event(event):
    app.logger.info('event: %s', event)

start_consumer(_log_event)

@app.before_request
def before_request_func():
    REQUEST_COUNT.labels(request.method, request.path).inc()
    if 'tracked_cities' not in session:
        session['tracked_cities'] = []

@app.after_request
def after_request_func(response):
    AQI_GAUGE.set(PollutionRecord.query.count())
    return response

scheduler = BackgroundScheduler()

def scheduled_collection(force=False):
    with app.app_context():
        for city in list(monitored_cities):
            try:
                if force:
                    collect_data(city, max_age_minutes=0)
                else:
                    collect_data(city)
                history = get_aqi_history(city, hours=1)
                if history:
                    socketio.emit('update', {'city': city, **history[-1]})
                    publish_event('aqi_collected', {'city': city, 'aqi': history[-1]['aqi']})
            except Exception as e:
                app.logger.warning("Failed to collect data for %s: %s", city, e)


@app.before_first_request
def setup_database():
    """Ensure database tables exist and start scheduler."""
    db.create_all()
    if not User.query.first():
        user = User(username='demo', password=generate_password_hash('demo'))
        db.session.add(user)
        db.session.commit()
    scheduler.add_job(scheduled_collection, 'interval', minutes=30, id='aqi_job')
    scheduler.start()
    scheduled_collection(force=True)

@app.route('/')
def index():
    """Render the main interface."""
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile')
def profile():
    """Display the profile page which manages favorite cities client side."""
    return render_template('profile.html')

@app.route('/data/<city>')
def get_city_data(city):
    try:
        collect_data(city) 
        history = get_aqi_history(city, hours=1)
        if not history:
            return jsonify({"error": "No data"}), 404
        latest = history[-1]
        return jsonify(latest)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/data/history/<city>')
def get_city_history(city):
    try:
        hours = int(request.args.get('hours', 24))
        history = get_aqi_history(city, hours=hours)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/data/history')
def get_all_history():
    try:
        cities = list(dict.fromkeys(monitored_cities + session.get('tracked_cities', [])))
        result = {}
        for city in cities:
            records = (
                PollutionRecord.query.filter_by(city=city)
                .order_by(PollutionRecord.timestamp.asc())
                .all()
            )
            result[city] = [
                {
                    'timestamp': r.timestamp.isoformat(),
                    'aqi': r.aqi,
                    'pm25': r.pm25,
                    'co': r.co,
                    'no2': r.no2,
                }
                for r in records
            ]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/data/history_multi')
def get_history_multi():
    try:
        cities = request.args.getlist('city')
        hours = int(request.args.get('hours', 24))
        result = {}
        for city in cities:
            result[city] = get_aqi_history(city, hours=hours)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/data/average/<city>')
def get_average(city):
    try:
        start_date = datetime.now() - timedelta(days=7)
        average_aqi = get_average_aqi(city, start_date, datetime.now())
        return jsonify({"city": city, "average_aqi": average_aqi})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/search', methods=['GET'])
def search():
    city = request.args.get('city')
    if city:
        collect_data(city, max_age_minutes=0)
        if city not in monitored_cities:
            monitored_cities.append(city)
        if city not in session['tracked_cities']:
            session['tracked_cities'].append(city)
        history = get_aqi_history(city, hours=1)
        if history:
            socketio.emit('update', {'city': city, **history[-1]})
        publish_event('search_city', {'city': city})
        recent_aqi = get_recent_aqi(city)
        return render_template('index.html', city=city, aqi=recent_aqi)
    return render_template('index.html', error="City not found!")

@app.route('/collect_data_for_multiple')
def collect_data_multiple():
    cities = ['New York', 'Los Angeles', 'Chicago', 'San Francisco', 'Houston', 'Beijing', 'London']
    collect_data_for_multiple_cities(cities)
    return jsonify({"status": "Data collection for multiple cities is complete!"})

@app.route('/api/summary')
def api_summary():
    cities = request.args.getlist('city') or ['New York', 'Los Angeles', 'Chicago']
    result = {}
    for city in cities:
        start_date = datetime.now() - timedelta(days=1)
        avg = get_average_aqi(city, start_date, datetime.now())
        result[city] = avg
    return jsonify(result)

@app.route('/api/coords/<city>')
def api_coords(city):
    import json, os
    import requests
    path = os.path.join(os.path.dirname(__file__), 'city_coords.json')
    with open(path) as f:
        coords = json.load(f)
    if city in coords:
        return jsonify({'lat': coords[city][0], 'lon': coords[city][1]})
    try:
        from urllib.parse import quote
        resp = requests.get(Config.BASE_URL.format(quote(city)), timeout=10)
        data = resp.json()
        if data.get('status') == 'ok':
            lat, lon = data['data']['city']['geo']
            coords[city] = [lat, lon]
            with open(path, 'w') as f:
                json.dump(coords, f, indent=2)
            return jsonify({'lat': lat, 'lon': lon})
    except Exception:
        pass
    return jsonify({'error': 'Unknown city'}), 404

@app.route('/api/all_coords')
def api_all_coords():
    import json, os
    path = os.path.join(os.path.dirname(__file__), 'city_coords.json')
    with open(path) as f:
        coords = json.load(f)
    return jsonify(coords)

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain'}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    socketio.run(
        app,
        debug=False,
        use_reloader=False,
        host="0.0.0.0",
        port=port,
        allow_unsafe_werkzeug=True
    )