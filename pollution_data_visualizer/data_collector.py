import requests
import time
import threading
from config import Config
from urllib.parse import quote
from datetime import datetime, timedelta
from models import db, PollutionRecord
from events import publish_event
from cachetools import TTLCache

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.timestamp = time.monotonic()
        self.lock = threading.Lock()

    def _add_tokens(self):
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.timestamp) * self.rate)
        self.timestamp = now

    def acquire(self, tokens=1):
        while True:
            with self.lock:
                self._add_tokens()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
            time.sleep(max(0, 1 / self.rate))

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc, tb):
        pass


bucket = TokenBucket(16, 60)
_cache = TTLCache(maxsize=64, ttl=300)

def fetch_air_quality(city):
    if city in Config.DEFAULT_CITIES:
        cached = _cache.get(city)
        if cached:
            return cached

    url = Config.BASE_URL.format(quote(city))
    tries = 0
    while tries < 3:
        with bucket:
            resp = requests.get(url, allow_redirects=True, timeout=10)
        if resp.status_code in (429,) or 300 <= resp.status_code < 400:
            time.sleep(2 ** tries)
            tries += 1
            continue
        data = resp.json()
        if data.get("status") == "ok":
            break
        raise Exception(f"Failed to fetch data for {city}. Error: {data.get('data', {}).get('error', 'Unknown error')}")
    else:
        raise Exception(f"Failed to fetch data for {city}")

    if data.get("status") == "ok":
        aqi = data["data"].get("aqi")
        iaqi = data["data"].get("iaqi", {})
        pm25 = iaqi.get("pm25", {}).get("v")
        co = iaqi.get("co", {}).get("v")
        no2 = iaqi.get("no2", {}).get("v")
        timestamp = datetime.now()
        result = (aqi, pm25, co, no2, timestamp)
        if city in Config.DEFAULT_CITIES:
            _cache[city] = result
        return result
    else:
        raise Exception(f"Failed to fetch data for {city}. Error: {data.get('data', {}).get('error', 'Unknown error')}")
        
def save_air_quality_data(city, aqi, pm25, co, no2, timestamp):
    air_quality_data = PollutionRecord(
        city=city,
        aqi=aqi,
        pm25=pm25,
        co=co,
        no2=no2,
        timestamp=timestamp,
    )
    db.session.add(air_quality_data)
    db.session.commit()
    try:
        from app import socketio
        socketio.emit('update', {
            'city': city,
            'timestamp': timestamp.isoformat(),
            'aqi': aqi,
            'pm25': pm25,
            'co': co,
            'no2': no2,
        })
    except Exception:
        pass
    publish_event('aqi_collected', {'city': city, 'aqi': aqi})

def collect_data(city, max_age_minutes=Config.FETCH_CACHE_MINUTES):
    latest = (
        PollutionRecord.query.filter_by(city=city)
        .order_by(PollutionRecord.timestamp.desc())
        .first()
    )
    if latest and datetime.now() - latest.timestamp < timedelta(minutes=max_age_minutes):
        return
    aqi, pm25, co, no2, timestamp = fetch_air_quality(city)
    save_air_quality_data(city, aqi, pm25, co, no2, timestamp)

def collect_data_for_multiple_cities(cities):
    for city in cities:
        try:
            collect_data(city)
        except Exception as e:
            print(f"Error collecting data for {city}: {e}")
