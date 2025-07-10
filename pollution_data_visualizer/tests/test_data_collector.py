import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_collector import fetch_air_quality

class TestDataCollector(unittest.TestCase):
    @patch('data_collector.requests.get')
    def test_fetch_air_quality(self, mock_get):
        mock_get.return_value.json.return_value = {
            'status': 'ok',
            'data': {
                'aqi': 42,
                'iaqi': {
                    'pm25': {'v': 10},
                    'co': {'v': 0.5},
                    'no2': {'v': 15}
                }
            }
        }
        aqi, pm25, co, no2, timestamp = fetch_air_quality('TestCity')
        self.assertEqual(aqi, 42)
        self.assertEqual(pm25, 10)
        self.assertEqual(co, 0.5)
        self.assertEqual(no2, 15)
        self.assertIsNotNone(timestamp)

if __name__ == '__main__':
    unittest.main()
