import os

class Config:
    API_KEY = 'da422a944c1edaa853351550b87c87b02b7563ab'
    BASE_URL = 'https://api.waqi.info/feed/{city}/'

    FETCH_CACHE_MINUTES = 30
    
    db_path = os.path.join(os.path.dirname(__file__), 'pollution.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + db_path)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
