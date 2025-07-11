import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import AirQualityData

class TestIntegration(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        with app.app_context():
            db.create_all()
        self.client = app.test_client()

    @patch('data_collector.fetch_air_quality')
    def test_full_flow(self, mock_fetch):
        from datetime import datetime
        ts = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        mock_fetch.return_value = [
            {
                'location': 'Station',
                'parameter': 'pm25',
                'value': 50,
                'unit': 'µg/m³',
                'date': {'utc': ts}
            }
        ]
        resp = self.client.get('/data/Testville')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['aqi'], 50)
        hist_resp = self.client.get('/data/history/Testville?hours=1')
        history = hist_resp.get_json()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['aqi'], 50)

if __name__ == '__main__':
    unittest.main()
