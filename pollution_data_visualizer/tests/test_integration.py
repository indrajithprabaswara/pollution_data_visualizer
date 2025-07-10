import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as app_module
app = app_module.app
db = app_module.db
from models import PollutionRecord

class TestIntegration(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        try:
            app_module.scheduler.shutdown(wait=False)
        except Exception:
            pass
        app_module.scheduler.add_job = lambda *a, **k: None
        app_module.scheduler.start = lambda *a, **k: None
        app_module.monitored_cities = []
        with app.app_context():
            db.create_all()
        self.client = app.test_client()

    @patch('data_collector.fetch_air_quality')
    def test_full_flow(self, mock_fetch):
        from datetime import datetime
        mock_fetch.return_value = (50, 12, 0.4, 14, datetime.now())
        resp = self.client.get('/data/Testville')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['aqi'], 50)
        with app.app_context():
            self.assertGreaterEqual(PollutionRecord.query.count(), 1)
        hist_resp = self.client.get('/data/history/Testville?hours=1')
        history = hist_resp.get_json()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['aqi'], 50)

if __name__ == '__main__':
    unittest.main()
