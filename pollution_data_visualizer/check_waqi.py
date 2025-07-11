#!/usr/bin/env python3
"""
check_waqi.py

Simple script to verify your WAQI token and endpoint are returning sane JSON.
"""

import requests
import sys
import os

API_TOKEN = os.environ.get("WAQI_TOKEN", "")
BASE_URL = "https://api.waqi.info/feed/{city}/"

def check_city(city: str):
    url = BASE_URL.format(city=city)
    try:
        resp = requests.get(url,
                            params={"token": API_TOKEN},
                            timeout=5,
                            allow_redirects=True)
    except requests.RequestException as e:
        print(f"[{city}] REQUEST ERROR → {e}")
        return

    print(f"[{city}] HTTP {resp.status_code}")
    # Try parse JSON
    try:
        payload = resp.json()
    except ValueError:
        print(f"[{city}] INVALID JSON:\n  {resp.text[:200]}…")
        return

    status = payload.get("status")
    if status == "ok":
        data = payload.get("data", {})
        aqi = data.get("aqi")
        ts  = data.get("time", {}).get("iso")
        print(f"[{city}] OK → AQI={aqi}, timestamp={ts}")
    else:
        # Could be "error" or "no data"
        message = payload.get("data") or payload.get("message")
        print(f"[{city}] API ERROR → status={status}, message={message}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cities = sys.argv[1:]
    else:
        # default test cities
        cities = ["here", "beijing", "shanghai"]

    for c in cities:
        check_city(c)
