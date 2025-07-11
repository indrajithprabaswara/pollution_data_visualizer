import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

    @patch('data_collector.requests.get')
    def test_ttl_default_city(self, mock_get):
        from cachetools import TTLCache

        # custom timer to control time progression
        t = [0]

        def timer():
            return t[0]

        cache = TTLCache(maxsize=64, ttl=300, timer=timer)
        with patch('data_collector._cache', cache):
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'status': 'ok', 'data': {'aqi': 1, 'iaqi': {}}}
            city = Config.DEFAULT_CITIES[0]

            # first call populates cache
            fetch_air_quality(city)
            mock_get.assert_called_once()
            mock_get.reset_mock()

            # within ttl should use cache
            fetch_air_quality(city)
            mock_get.assert_not_called()

            # advance time beyond ttl
            t[0] += 301
            fetch_air_quality(city)
            mock_get.assert_called_once()
