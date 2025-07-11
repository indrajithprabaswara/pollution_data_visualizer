import os

class Config:
    SECRET_KEY = 'change-me'
    API_KEY = 'c08edb637332856d22941f390ab5dcf64062499a'
    BASE_URL = 'https://api.waqi.info/feed/{}/?token=' + API_KEY

    FETCH_CACHE_MINUTES = 30
    
    db_path = os.path.join(os.path.dirname(__file__), 'pollution.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + db_path)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
