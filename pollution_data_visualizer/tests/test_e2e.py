import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as app_module
app = app_module.app
db = app_module.db

class TestE2E(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test'
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
        self.events = []
        self._orig_publish = app_module.publish_event
        app_module.publish_event = lambda t, p=None: self.events.append({'type': t, 'payload': p})

    def tearDown(self):
        app_module.publish_event = self._orig_publish

    @patch('data_collector.fetch_air_quality')
    @patch('app.socketio.emit')
    def test_search_and_event(self, mock_emit, mock_fetch):
        from datetime import datetime
        mock_fetch.return_value = (75, 22, 0.6, 20, datetime.now())
        resp = self.client.get('/search?city=DemoCity')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(self.events), 1)
        event = self.events[0]
        self.assertEqual(event['type'], 'search_city')

if __name__ == '__main__':
    unittest.main()
