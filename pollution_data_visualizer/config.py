import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', '')
    WAQI_TOKEN = os.environ.get('WAQI_TOKEN', '')
    BASE_URL = 'https://api.waqi.info/feed/{}/?token=' + WAQI_TOKEN

    DEFAULT_CITIES = ['New York', 'Los Angeles', 'San Francisco']

    FETCH_CACHE_MINUTES = 30

    db_path = os.path.join(os.path.dirname(__file__), 'pollution.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + db_path)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
