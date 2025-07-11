import requests
import time
import threading
from config import Config
from urllib.parse import quote
from datetime import datetime, timedelta
from models import db, PollutionRecord
from events import publish_event
from cachetools import TTLCache
from prometheus_client import Counter
from contextlib import contextmanager
from token_bucket import Limiter, MemoryStorage

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

class _BucketWrapper:
    def __init__(self, rate, capacity):
        self._rate = rate
        self._limiter = Limiter(rate, capacity, MemoryStorage())

    @contextmanager
    def consume(self, tokens=1):
        while not self._limiter.consume(b'global', tokens):
            time.sleep(1 / self._rate)
        try:
            yield
        finally:
            pass

bucket = _BucketWrapper(16, 60)


_cache = TTLCache(maxsize=64, ttl=300)
COLLECTION_SUCCESS = Counter('collection_success_total', 'Successful data collections')
COLLECTION_FAILURE = Counter('collection_failure_total', 'Failed data collections')

def fetch_air_quality(city):
    if city in Config.DEFAULT_CITIES:
        cached = _cache.get(city)
        if cached:
            return cached

    url = Config.BASE_URL.format(quote(city))
    tries = 0
    while tries < 3:
        with bucket.consume(1):
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
    COLLECTION_SUCCESS.inc()
    try:
        from app import socketio
        socketio.emit('new_record', {
            'city': city,
            'timestamp': timestamp.isoformat(),
            'aqi': aqi,
            'pm25': pm25,
            'co': co,
            'no2': no2,
        }, namespace='/')
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
    try:
        aqi, pm25, co, no2, timestamp = fetch_air_quality(city)
    except Exception:
        COLLECTION_FAILURE.inc()
        raise
    save_air_quality_data(city, aqi, pm25, co, no2, timestamp)

def collect_data_for_multiple_cities(cities):
    for city in cities:
        try:
            collect_data(city)
        except Exception as e:
            print(f"Error collecting data for {city}: {e}")
