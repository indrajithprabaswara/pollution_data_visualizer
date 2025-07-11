import os
import unittest
from app import app, db
from models import PollutionRecord
from datetime import datetime

class TestPersistence(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        with app.app_context():
            db.create_all()
        self.client = app.test_client()

    def test_insert_and_query(self):
        with app.app_context():
            rec = PollutionRecord(city='X', aqi=1, pm25=2, co=3, no2=4, timestamp=datetime.now())
            db.session.add(rec)
            db.session.commit()
            fetched = PollutionRecord.query.filter_by(city='X').first()
            self.assertIsNotNone(fetched)

