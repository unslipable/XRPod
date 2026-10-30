"""XRPod event and error logger.
 
Records system events (mode changes, environment selections, zone changes,
manual setting changes) and software errors to two separate CSV files.
store.py keeps settings history and sensor readings; this module only
covers events and errors.
 
Usage from another module:
    from event_logger import log_event, log_error
    log_event("mode_changed", {"from": "MANUAL", "to": "AUTOMATIC"})
    log_error("web", "invalid zone 'lava' for environment 'beach'")
"""
import csv
import json
import os
import threading
from datetime import datetime, timezone
 
LOG_DIR = os.environ.get("XRPOD_LOG_DIR",
                         os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs"))
EVENTS_FILE = "events.csv"
ERRORS_FILE = "errors.csv"
 
EVENT_COLUMNS = ["timestamp", "event_type", "details"]
ERROR_COLUMNS = ["timestamp", "source", "message"]
 
# Suggested event types so everyone uses the same names.
EVENT_TYPES = {
    "mode_changed",
    "environment_selected",
    "zone_entered",
    "manual_setting_changed",
}
 
_lock = threading.Lock()
 
 
def _now():
    """ISO 8601 UTC timestamp, e.g. 2026-10-20T06:45:26Z."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
 
 
def _path(filename):
    return os.path.join(LOG_DIR, filename)
 
 
def _ensure_file(filename, columns):
    """Create the log folder and CSV (with header row) if they don't exist."""
    os.makedirs(LOG_DIR, exist_ok=True)
    path = _path(filename)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(columns)
    return path
 
 
def _append(filename, columns, row):
    with _lock:
        path = _ensure_file(filename, columns)
        with open(path, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=columns).writerow(row)
    return row
 
 
def _read_recent(filename, columns, limit):
    path = _ensure_file(filename, columns)
    with _lock, open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if limit is None or limit <= 0:
        return []
    # Newest first, which is what the HUD Logs/Errors tabs will want.
    return list(reversed(rows[-limit:]))
 
 
def log_event(event_type, details=None):
    """Record an XRPod event. details may be a string or a dict."""
    if not event_type or not isinstance(event_type, str):
        raise ValueError("event_type must be a non-empty string")
    if isinstance(details, (dict, list)):
        details = json.dumps(details, sort_keys=True)
    elif details is None:
        details = ""
    row = {"timestamp": _now(), "event_type": event_type, "details": str(details)}
    return _append(EVENTS_FILE, EVENT_COLUMNS, row)
 
 
def log_error(source, message):
    """Record an error: where it happened (source) and what went wrong."""
    if not source or not isinstance(source, str):
        raise ValueError("source must be a non-empty string")
    row = {"timestamp": _now(), "source": source, "message": str(message)}
    return _append(ERRORS_FILE, ERROR_COLUMNS, row)
 
 
def get_recent_events(limit=50):
    """Return up to `limit` most recent events, newest first."""
    rows = _read_recent(EVENTS_FILE, EVENT_COLUMNS, limit)
    for row in rows:
        try:
            row["details"] = json.loads(row["details"])
        except (ValueError, TypeError):
            pass  # plain-text details stay as a string
    return rows
 
 
def get_recent_errors(limit=50):
    """Return up to `limit` most recent errors, newest first."""
    return _read_recent(ERRORS_FILE, ERROR_COLUMNS, limit)
 
 
if __name__ == "__main__":
    # Quick demo with sample data: python event_logger.py
    log_event("environment_selected", {"environment": "beach"})
    log_event("mode_changed", {"from": "MANUAL", "to": "AUTOMATIC"})
    log_event("zone_entered", {"environment": "beach", "zone": "hot"})
    log_event("manual_setting_changed", {"fan_speed_pct": 40})
    log_error("web", "invalid zone 'lava' for environment 'beach'")
    log_error("unity", "lost connection to headset")
    print("Recent events:")
    for e in get_recent_events(10):
        print(" ", e)
    print("Recent errors:")
    for e in get_recent_errors(10):
        print(" ", e)
 