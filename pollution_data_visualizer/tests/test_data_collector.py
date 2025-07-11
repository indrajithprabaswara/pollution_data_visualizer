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
            'meta': {'page': 1, 'pages': 1},
            'results': [
                {
                    'location': 'Station',
                    'parameter': 'pm25',
                    'value': 12.34,
                    'unit': 'µg/m³',
                    'date': {'utc': '2020-01-01T00:00:00Z'}
                }
            ]
        }
        data = fetch_air_quality('TestCity')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['value'], 12.34)

if __name__ == '__main__':
    unittest.main()
