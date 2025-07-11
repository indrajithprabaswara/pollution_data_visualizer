import os
import sys
import time
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_collector import TokenBucket

class TestRateLimiter(unittest.TestCase):
    def test_burst_and_rate(self):
        bucket = TokenBucket(16, 60)
        # acquiring up to burst size should not block
        start = time.time()
        for _ in range(60):
            bucket.acquire()
        self.assertLess(time.time() - start, 0.5)

        # next acquire should respect rate limit
        start = time.time()
        bucket.acquire()
        self.assertGreaterEqual(time.time() - start, 1 / 16)
