import subprocess
import time
import unittest
import threading
import http.server
import json
import requests

class StubHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        payload = {
            'status': 'ok',
            'data': {
                'aqi': 42,
                'city': {'geo': [0,0]},
                'iaqi': {
                    'pm25': {'v': 10},
                    'co': {'v': 0.5},
                    'no2': {'v': 5}
                }
            }
        }
        self.wfile.write(json.dumps(payload).encode())

    def log_message(self, format, *args):
        pass

def start_stub(port=5005):
    server = http.server.HTTPServer(('0.0.0.0', port), StubHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

class TestEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(['docker','build','-t','pdv-test','.'], check=True)
        cls.stub = start_stub()
        cls.proc = subprocess.Popen(
            ['docker','run','--network=host','-e','WAQI_TOKEN=x','-e','SECRET_KEY=x','-e','WAQI_BASE_URL=http://127.0.0.1:5005/feed/{}/?token=x','pdv-test'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        # wait for server
        for _ in range(30):
            try:
                requests.get('http://localhost:8080/')
                break
            except Exception:
                time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait(timeout=20)
        cls.stub.shutdown()

    def test_end_to_end(self):
        cur = requests.get('http://localhost:8080/data/current', params={'city':'New York'})
        self.assertEqual(cur.status_code, 200)
        data = cur.json()
        self.assertEqual(data['aqi'], 42)
        self.assertEqual(data['pm25'], 10)
        self.assertEqual(data['co'], 0.5)
        self.assertEqual(data['no2'], 5)

        task = requests.post('http://localhost:8080/tasks/collect')
        self.assertEqual(task.status_code, 204)

        hist_resp = requests.post('http://localhost:8080/data/history', json={'cities':['New York']})
        self.assertEqual(hist_resp.status_code, 200)
        history = hist_resp.json()
        self.assertIn('New York', history)
        self.assertTrue(len(history['New York']) >= 1)
        self.assertEqual(history['New York'][-1]['aqi'], 42)

if __name__ == '__main__':
    unittest.main()
