"""Regex-based incident type and severity classification."""

import re


PATTERNS = {
    "network": re.compile(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b|"
        r"\b(?:TCP|UDP|ICMP|VLAN|switch|DNS|packet loss|unreachable|offline|"
        r"firewall|connection timeout|prod-db-\d+)\b",
        re.IGNORECASE,
    ),
    "security": re.compile(
        r"\b(?:breach|ransomware|brute[- ]force|malware|phishing|unauthorized|"
        r"suspicious login|unknown IP|firewall rule|misconfiguration)\b",
        re.IGNORECASE,
    ),
    "app": re.compile(
        r"\b(?:error code|NullPointerException|HTTP[- ]?\d{3}|stack trace|"
        r"exception|API|service returning|scheduled job|failed|latency)\b",
        re.IGNORECASE,
    ),
    "critical_kw": re.compile(
        r"\b(?:outage|down|breach|ransomware|(?<!non-)production|prod)\b",
        re.IGNORECASE,
    ),
    "high_kw": re.compile(
        r"\b(?:timeout|failing|unavailable|unreachable|HTTP[- ]?5\d{2}|"
        r"NullPointerException|suspicious login|unauthorized|multiple attempts)\b",
        re.IGNORECASE,
    ),
    "medium_kw": re.compile(
        r"\b(?:slow|degraded|warning|intermittent|phishing|packet loss|latency)\b",
        re.IGNORECASE,
    ),
}


def detect_type(text: str) -> str:
    """Return network, security, app, or general for an incident."""

    if PATTERNS["security"].search(text):
        return "security"
    if PATTERNS["app"].search(text):
        return "app"
    if PATTERNS["network"].search(text):
        return "network"
    return "general"


def detect_severity(text: str) -> str:
    """Return critical, high, medium, or low for an incident."""

    if PATTERNS["critical_kw"].search(text):
        return "critical"
    if PATTERNS["high_kw"].search(text):
        return "high"
    if PATTERNS["medium_kw"].search(text):
        return "medium"
    return "low"

