"""
Satellite simulator that stages uplink events for offline alerting.
"""
import time
from datetime import datetime, timedelta

def send(payload, delay_seconds=1.0):
    """
    Simulate a sequence of satellite events. Returns list of events.
    """
    events = []
    now = datetime.utcnow()
    events.append({"time": now.isoformat(), "status":"queued", "note":"Queued for uplink"})
    time.sleep(delay_seconds * 0.2)
    events.append({"time": (now + timedelta(seconds=1)).isoformat(), "status":"uplink", "note":"Uplink in progress"})
    time.sleep(delay_seconds * 0.5)
    events.append({"time": (now + timedelta(seconds=2)).isoformat(), "status":"delivered", "note":"Delivered to satellite network"})
    return events