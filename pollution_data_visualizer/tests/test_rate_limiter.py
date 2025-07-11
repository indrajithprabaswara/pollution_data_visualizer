import time
import unittest
from data_collector import TokenBucket

class TestRateLimiter(unittest.TestCase):
    def test_burst_and_rate(self):
        bucket = TokenBucket(16, 60)
        for _ in range(60):
            bucket.acquire()
        start = time.time()
        bucket.acquire()
        self.assertGreaterEqual(time.time() - start, 1/16)
