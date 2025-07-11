import requests
from config import Config
from datetime import datetime, timedelta
from models import db, AirQualityData, Measurement

def fetch_air_quality(city):
    page = 1
    results = []
    while True:
        response = requests.get(Config.BASE_URL, params={'city': city, 'limit': 100, 'page': page})  # updated to OpenAQ v3
        data = response.json()
        results.extend(data.get('results', []))
        if page >= data.get('meta', {}).get('pages', 1):
            break
        page += 1
    return results  # updated to OpenAQ v3
        
def save_air_quality_data(city, results):
    if not results:
        return
    first = results[0]
    ts = datetime.fromisoformat(first['date']['utc'].replace('Z', '+00:00')).replace(tzinfo=None)
    aqi = first.get('value')
    air_quality_data = AirQualityData(
        city=city,
        aqi=aqi,
        pm25=first.get('value'),
        co=None,
        no2=None,
        timestamp=ts,
    )
    db.session.add(air_quality_data)
    for item in results:
        dt = datetime.fromisoformat(item['date']['utc'].replace('Z', '+00:00')).replace(tzinfo=None)
        measurement = Measurement(
            city=city,
            utc_datetime=dt,  # updated to OpenAQ v3
            value=item.get('value'),
            unit=item.get('unit'),
            location=item.get('location'),
        )
        db.session.add(measurement)
    db.session.commit()  # updated for persistence

def collect_data(city, max_age_minutes=Config.FETCH_CACHE_MINUTES):
    latest = (
        AirQualityData.query.filter_by(city=city)
        .order_by(AirQualityData.timestamp.desc())
        .first()
    )
    if latest and datetime.now() - latest.timestamp < timedelta(minutes=max_age_minutes):
        return
    results = fetch_air_quality(city)
    save_air_quality_data(city, results)

def collect_data_for_multiple_cities(cities):
    for city in cities:
        try:
            collect_data(city)
        except Exception as e:
            print(f"Error collecting data for {city}: {e}")
