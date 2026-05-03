"""Lightweight verification tests for the mini project."""

import json
import sys
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from main import DATA_PATH, make_incident  # noqa: E402
from models.incident import IncidentIterator  # noqa: E402
from utils.classifier import detect_severity, detect_type  # noqa: E402
from utils.helpers import count_by_team, get_critical_incidents  # noqa: E402


class IncidentTrackerTests(unittest.TestCase):
    def setUp(self):
        self.records = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        self.incidents = [make_incident(record) for record in self.records]

    def test_sample_data_has_required_12_records(self):
        self.assertEqual(12, len(self.records))

    def test_classifier_examples(self):
        self.assertEqual("network", detect_type("ICMP packet loss on VLAN 30"))
        self.assertEqual("security", detect_type("ransomware breach detected"))
        self.assertEqual("app", detect_type("HTTP-503 NullPointerException stack trace"))
        self.assertEqual("critical", detect_severity("production outage is down"))
        self.assertEqual("high", detect_severity("service timeout unavailable"))
        self.assertEqual("medium", detect_severity("slow intermittent warning"))
        self.assertEqual("low", detect_severity("minor audit note"))

    def test_expected_distribution(self):
        severities = [incident.severity for incident in self.incidents]
        self.assertEqual(3, severities.count("critical"))
        self.assertEqual(3, severities.count("high"))
        self.assertEqual(4, severities.count("medium"))
        self.assertEqual(2, severities.count("low"))

    def test_iterator_and_helpers(self):
        critical_only = list(IncidentIterator(self.incidents, severity="critical"))
        self.assertEqual(3, len(critical_only))
        self.assertEqual(3, len(get_critical_incidents(self.incidents)))
        self.assertEqual(4, count_by_team(self.incidents)["Network Operations"])


if __name__ == "__main__":
    unittest.main()
