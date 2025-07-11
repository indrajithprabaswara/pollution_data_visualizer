from models import PollutionRecord
from datetime import datetime, timedelta

def get_average_aqi(city, start_date, end_date):
    data = PollutionRecord.query.filter(PollutionRecord.city == city,
                                        PollutionRecord.timestamp >= start_date,
                                        PollutionRecord.timestamp <= end_date).all()

    if not data:
        return None

    total_aqi = sum([record.aqi for record in data])
    return total_aqi / len(data)

def get_recent_aqi(city):
    data = PollutionRecord.query.filter(PollutionRecord.city == city).order_by(PollutionRecord.timestamp.desc()).first()
    return data.aqi if data else None

def get_aqi_history(city, hours=24):
    start_time = datetime.now() - timedelta(hours=hours)
    records = (
        PollutionRecord.query
        .filter(PollutionRecord.city == city, PollutionRecord.timestamp >= start_time)
        .order_by(PollutionRecord.timestamp.asc())
        .all()
    )
    return [
        {
            "timestamp": record.timestamp.isoformat(),
            "aqi": record.aqi,
            "pm25": record.pm25,
            "co": record.co,
            "no2": record.no2,
        }
        for record in records
    ]
