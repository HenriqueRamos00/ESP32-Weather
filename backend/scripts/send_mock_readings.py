#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///
"""
Send mock ESP32 weather readings to the API to test aggregation/bucketing.
Needs uv

Examples:
  # send 3 days of data at 1-minute resolution
  ./scripts/send_mock_weather_readings.py --days 3 --every-seconds 60

  # send 7 days of data at 5-minute resolution to a different base url
  ./scripts/send_mock_weather_readings.py --base-url http://localhost:8000 --days 7 --every-seconds 300

  # just send 200 points starting from a specific ISO timestamp
  ./scripts/send_mock_weather_readings.py --count 200 --start 2026-01-01T00:00:00Z
"""

from __future__ import annotations

import argparse
import math
import os
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    import requests  # type: ignore
except ImportError:
    print("Missing dependency: requests. Install with: pip install requests", file=sys.stderr)
    raise


def isoformat_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_iso(s: str) -> datetime:
    # accept "...Z" or "+00:00"
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def make_reading(ts: datetime, i: int, seed: int | None = None) -> dict[str, Any]:
    """
    Generate a semi-realistic timeseries with daily cycles + noise.
    """
    if seed is not None:
        random.seed(seed + i)

    # daily cycle in [0..2pi)
    day_phase = (ts.hour * 3600 + ts.minute * 60 + ts.second) / 86400.0 * (2.0 * math.pi)

    base_temp = 24.0 + 6.0 * math.sin(day_phase - 1.0)  # warmer mid-day
    temperature = base_temp + random.uniform(-0.8, 0.8)

    # inverse-ish relation with temp + noise
    humidity = 55.0 - 10.0 * math.sin(day_phase - 1.0) + random.uniform(-3.0, 3.0)
    humidity = max(5.0, min(95.0, humidity))

    # pressure slow drift
    pressure = 1013.0 + 8.0 * math.sin(i / 500.0) + random.uniform(-1.5, 1.5)

    # gusty wind
    wind_speed = max(0.0, 2.2 + 1.2 * math.sin(i / 30.0) + random.uniform(-0.8, 0.8))

    # occasional rain pulses
    rain_amount = 0.0
    if random.random() < 0.03:  # 3% of points
        rain_amount = round(random.uniform(0.1, 2.5), 2)

    return {
        "temperature": round(temperature, 2),
        "humidity": round(humidity, 2),
        "pressure": round(pressure, 2),
        "wind_speed": round(wind_speed, 2),
        "rain_amount": rain_amount,
        "recorded_at": isoformat_z(ts),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default=os.getenv("BASE_URL", "http://localhost:8000"))
    p.add_argument("--endpoint", default=os.getenv("ENDPOINT", "/api/v1/esp32/readings"))
    p.add_argument(
        "--api-key",
        default=os.getenv("ESP32_API_KEY", "sk_esp_***"),
        help="X-API-Key value (or set ESP32_API_KEY env var).",
    )

    # choose one of these input modes:
    p.add_argument("--days", type=float, default=None, help="Generate this many days ending at --end (or now).")
    p.add_argument("--count", type=int, default=None, help="Generate a fixed number of points from --start.")

    p.add_argument("--every-seconds", type=int, default=300, help="Interval between points.")
    p.add_argument("--start", default=None, help="ISO timestamp for start (used with --count).")
    p.add_argument("--end", default=None, help="ISO timestamp for end (used with --days). Default: now.")

    p.add_argument("--seed", type=int, default=123, help="Random seed.")
    p.add_argument("--sleep", type=float, default=0.0, help="Sleep between POSTs (seconds).")
    p.add_argument("--timeout", type=float, default=10.0)
    p.add_argument("--dry-run", action="store_true", help="Don't send, just print first few payloads.")

    args = p.parse_args()

    if (args.days is None) == (args.count is None):
        print("Choose exactly one mode: either --days or --count", file=sys.stderr)
        return 2

    every = timedelta(seconds=args.every_seconds)

    if args.days is not None:
        end = parse_iso(args.end) if args.end else datetime.now(timezone.utc)
        start = end - timedelta(days=float(args.days))
        # inclusive count-ish
        total = int(((end - start).total_seconds()) // args.every_seconds) + 1
    else:
        total = int(args.count)
        if not args.start:
            # default: go back from now so it looks like historical series
            start = datetime.now(timezone.utc) - (every * total)
        else:
            start = parse_iso(args.start)

    url = args.base_url.rstrip("/") + args.endpoint
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-API-Key": args.api_key,
    }

    print(f"POST {url}")
    print(f"Generating {total} readings every {args.every_seconds}s starting at {isoformat_z(start)}")
    if args.days is not None:
        print(f"Range end: {isoformat_z(end)}") # type: ignore

    sess = requests.Session()

    sent = 0
    t0 = time.time()
    for i in range(total):
        ts = start + (every * i)
        payload = make_reading(ts, i, seed=args.seed)

        if args.dry_run:
            if i < 5:
                print(payload)
            continue

        r = sess.post(url, json=payload, headers=headers, timeout=args.timeout)
        if r.status_code >= 400:
            print(f"Error {r.status_code}: {r.text}", file=sys.stderr)
            return 1

        sent += 1
        if sent % 200 == 0:
            elapsed = time.time() - t0
            rate = sent / elapsed if elapsed > 0 else sent
            print(f"Sent {sent}/{total} ({rate:.1f} req/s)")

        if args.sleep > 0:
            time.sleep(args.sleep)

    if args.dry_run:
        print(f"Dry run complete. Would have sent {total} readings.")
        return 0

    elapsed = time.time() - t0
    rate = sent / elapsed if elapsed > 0 else sent
    print(f"Done. Sent {sent} readings in {elapsed:.2f}s ({rate:.1f} req/s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())