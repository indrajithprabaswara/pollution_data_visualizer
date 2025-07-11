import unittest
from unittest.mock import patch
from config import Config
from data_collector import fetch_air_quality, _cache

class TestCache(unittest.TestCase):
    def setUp(self):
        _cache.clear()

    @patch('data_collector.requests.get')
    def test_cache_default_city(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'status': 'ok', 'data': {'aqi': 1, 'iaqi': {}}}
        city = Config.DEFAULT_CITIES[0]
        fetch_air_quality(city)
        mock_get.assert_called()
        mock_get.reset_mock()
        fetch_air_quality(city)
        mock_get.assert_not_called()
