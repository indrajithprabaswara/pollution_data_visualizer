import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_city_data(self):
        response = self.app.get('/data/Los Angeles')
        # The endpoint may fail if external API is unreachable; ensure a response is returned
        self.assertIn(response.status_code, [200, 400])

    def test_about_page(self):
        response = self.app.get('/about')
        self.assertEqual(response.status_code, 200)

    def test_summary_endpoint(self):
        response = self.app.get('/api/summary?city=TestCity')
        self.assertIn(response.status_code, [200, 400])

if __name__ == '__main__':
    unittest.main()
