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
        mock_fetch.return_value = [
            {
                'location': 'Station',
                'parameter': 'pm25',
                'value': 75,
                'unit': 'µg/m³',
                'date': {'utc': '2020-01-01T00:00:00Z'}
            }
        ]
        resp = self.client.get('/search?city=DemoCity')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(self.events), 1)
        event = self.events[0]
        self.assertEqual(event['type'], 'search_city')

if __name__ == '__main__':
    unittest.main()
