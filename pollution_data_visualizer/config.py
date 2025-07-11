import os

class Config:
    SECRET_KEY = 'change-me'
    API_KEY = '19ae9358e032b2a613a6e20605b39b95b106a9a6'
    BASE_URL = 'https://api.waqi.info/feed/{}/?token=' + API_KEY

    FETCH_CACHE_MINUTES = 30
    
    db_path = os.path.join(os.path.dirname(__file__), 'pollution.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + db_path)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
