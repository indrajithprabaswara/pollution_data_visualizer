import requests
from config import Config
from urllib.parse import quote
from datetime import datetime, timedelta
from models import db, AirQualityData

def fetch_air_quality(city):
    url = Config.BASE_URL.format(quote(city))
    response = requests.get(url)
    data = response.json()

    if data.get("status") == "ok":
        aqi = data["data"].get("aqi")
        iaqi = data["data"].get("iaqi", {})
        pm25 = iaqi.get("pm25", {}).get("v")
        co = iaqi.get("co", {}).get("v")
        no2 = iaqi.get("no2", {}).get("v")
        timestamp = datetime.now()
        return aqi, pm25, co, no2, timestamp
    else:
        raise Exception(f"Failed to fetch data for {city}. Error: {data.get('data', {}).get('error', 'Unknown error')}")
        
def save_air_quality_data(city, aqi, pm25, co, no2, timestamp):
    air_quality_data = AirQualityData(
        city=city,
        aqi=aqi,
        pm25=pm25,
        co=co,
        no2=no2,
        timestamp=timestamp,
    )
    db.session.add(air_quality_data)
    db.session.commit()

def collect_data(city, max_age_minutes=Config.FETCH_CACHE_MINUTES):
    latest = (
        AirQualityData.query.filter_by(city=city)
        .order_by(AirQualityData.timestamp.desc())
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
