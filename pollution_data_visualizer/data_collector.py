import requests
from config import Config
from datetime import datetime, timedelta
from models import db, AirQualityData, Measurement

def fetch_air_quality(city):
    url = Config.BASE_URL.format(city=city)
    resp = requests.get(url, params={'token': Config.API_KEY})
    data = resp.json()
    results = []
    if 'results' in data:
        results.extend(data.get('results', []))
    elif data.get('status') == 'ok':
        d = data.get('data', {})
        pm25 = d.get('iaqi', {}).get('pm25', {}).get('v')
        val = pm25 if pm25 is not None else d.get('aqi')
        results.append({
            'location': d.get('city', {}).get('name'),
            'value': val,
            'unit': 'AQI',
            'date': {'utc': d.get('time', {}).get('iso')}
        })
    return results
        
def save_air_quality_data(city, results):
    if not results:
        return
    ts = datetime.utcnow()
    first = results[0]
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
        measurement = Measurement(
            city=city,
            utc_datetime=ts,
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
