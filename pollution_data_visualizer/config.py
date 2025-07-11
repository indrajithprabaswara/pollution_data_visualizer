import os

class Config:
    SECRET_KEY = os.environ['SECRET_KEY']
    WAQI_TOKEN = os.environ['WAQI_TOKEN']
    WAQI_BASE_URL = os.environ.get('WAQI_BASE_URL')
    if WAQI_BASE_URL:
        BASE_URL = WAQI_BASE_URL
    else:
        BASE_URL = f'https://api.waqi.info/feed/{{}}/?token={WAQI_TOKEN}'

    DEFAULT_CITIES = [
        'New York',
        'Los Angeles',
        'San Francisco',
        'Perth',
        'Paris',
        'Delhi',
    ]

    FETCH_CACHE_MINUTES = 30

    db_path = os.path.join(os.path.dirname(__file__), 'pollution.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + db_path)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
