"""Tests for event_logger.py. Run with: python -m unittest test_event_logger"""
import csv
import os
import shutil
import tempfile
import unittest
 
import event_logger
 
 
class EventLoggerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        event_logger.LOG_DIR = self.tmp
 
    def tearDown(self):
        shutil.rmtree(self.tmp)
 
    def test_creates_files_with_headers(self):
        event_logger.get_recent_events()
        event_logger.get_recent_errors()
        with open(os.path.join(self.tmp, "events.csv")) as f:
            self.assertEqual(next(csv.reader(f)), event_logger.EVENT_COLUMNS)
        with open(os.path.join(self.tmp, "errors.csv")) as f:
            self.assertEqual(next(csv.reader(f)), event_logger.ERROR_COLUMNS)
 
    def test_log_and_read_event(self):
        event_logger.log_event("mode_changed", {"to": "AUTOMATIC"})
        events = event_logger.get_recent_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "mode_changed")
        self.assertEqual(events[0]["details"], {"to": "AUTOMATIC"})
        self.assertTrue(events[0]["timestamp"].endswith("Z"))
 
    def test_errors_go_to_separate_file(self):
        event_logger.log_event("zone_entered", "hot")
        event_logger.log_error("web", "invalid zone")
        self.assertEqual(len(event_logger.get_recent_events()), 1)
        errors = event_logger.get_recent_errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["source"], "web")
        self.assertEqual(errors[0]["message"], "invalid zone")
 
    def test_limit_returns_newest_first(self):
        for i in range(60):
            event_logger.log_event("zone_entered", {"n": i})
        events = event_logger.get_recent_events()
        self.assertEqual(len(events), 50)
        self.assertEqual(events[0]["details"], {"n": 59})
        self.assertEqual(len(event_logger.get_recent_events(limit=5)), 5)
 
    def test_details_with_commas_and_quotes(self):
        event_logger.log_event("manual_setting_changed", 'scent "Ocean", 40%')
        self.assertEqual(event_logger.get_recent_events()[0]["details"],
                         'scent "Ocean", 40%')
 
    def test_rejects_empty_names(self):
        with self.assertRaises(ValueError):
            event_logger.log_event("", "x")
        with self.assertRaises(ValueError):
            event_logger.log_error("", "x")
 
 
if __name__ == "__main__":
    unittest.main()