from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AirQualityData(db.Model):
    __tablename__ = 'air_quality_data'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(80), nullable=False)
    aqi = db.Column(db.Integer, nullable=False)
    pm25 = db.Column(db.Float)
    co = db.Column(db.Float)
    no2 = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, city, aqi, timestamp, pm25=None, co=None, no2=None):
        self.city = city
        self.aqi = aqi
        self.pm25 = pm25
        self.co = co
        self.no2 = no2
        self.timestamp = timestamp


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128))
    favorites = db.relationship('FavoriteCity', backref='user', lazy=True)


class FavoriteCity(db.Model):
    __tablename__ = 'favorite_cities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    alert = db.Column(db.Integer)
