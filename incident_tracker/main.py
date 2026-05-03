"""CLI entry point for the IT Incident Auto-Triage & Tracker project."""

import argparse
import json
import logging
import re
from pathlib import Path

from models.incident import (
    AppIncident,
    Incident,
    IncidentIterator,
    NetworkIncident,
    SecurityIncident,
    batch_incidents,
)
from models.report import ReportGenerator
from services import azure_boards, jira, servicenow
from utils.classifier import PATTERNS, detect_type
from utils.helpers import get_critical_incidents


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "incidents.json"
OUTPUT_DIR = BASE_DIR / "output"


def parse_args():
    parser = argparse.ArgumentParser(description="Auto-triage IT incidents and create mock tickets.")
    parser.add_argument("--data", default=str(DATA_PATH), help="Path to the incident JSON file.")
    parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low"],
        help="Only push incidents with this severity.",
    )
    return parser.parse_args()


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def load_records(path):
    with open(path, "r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("Input JSON must contain a list of incident records.")

    for record in records:
        Incident.validate_record(record)
    return records


def make_incident(record):
    text = f"{record['title']} {record['description']}"
    incident_type = detect_type(text)
    common = {
        **record,
        "title": clean_text(record["title"]),
        "description": clean_text(record["description"]),
    }

    if incident_type == "network":
        host = _first_match(PATTERNS["network"], text)
        protocol = _first_protocol(text)
        incident = NetworkIncident(**common, affected_host=host, protocol=protocol)
    elif incident_type == "security":
        source_ip = _first_ip(text)
        threat = _first_match(PATTERNS["security"], text)
        incident = SecurityIncident(**common, threat_type=threat, source_ip=source_ip)
    else:
        error_code = _first_match(PATTERNS["app"], text)
        app_name = _guess_app_name(text)
        incident = AppIncident(**common, app_name=app_name, error_code=error_code)

    incident.classify()
    return incident


def _first_match(pattern, text):
    match = pattern.search(text)
    return match.group(0) if match else "unknown"


def _first_ip(text):
    match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text)
    return match.group(0) if match else "unknown"


def _first_protocol(text):
    match = re.search(r"\b(TCP|UDP|ICMP)\b", text, re.IGNORECASE)
    return match.group(1).upper() if match else "unknown"


def _guess_app_name(text):
    lowered = text.lower()
    if "checkout" in lowered:
        return "checkout-service"
    if "payment" in lowered or "stripe" in lowered:
        return "payment-gateway"
    if "api" in lowered:
        return "api-service"
    if "job" in lowered:
        return "scheduler"
    return "application"


def create_all_tickets(incidents):
    for batch in batch_incidents(incidents, batch_size=3):
        logging.info("Processing batch of %s incident(s)", len(batch))
        for incident in batch:
            incident.ticket_ids["snow"] = servicenow.create_ticket(incident)
            incident.ticket_ids["jira"] = jira.create_ticket(incident)
            incident.ticket_ids["azure"] = azure_boards.create_ticket(incident)
            servicenow.update_status(incident.ticket_ids["snow"], "In Progress")
            jira.update_priority(incident.ticket_ids["jira"], incident.severity)


def main():
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[logging.FileHandler(OUTPUT_DIR / "triage.log", encoding="utf-8")],
    )

    records = load_records(args.data)
    incidents = sorted(make_incident(record) for record in records)
    selected = list(IncidentIterator(incidents, severity=args.severity))

    create_all_tickets(selected)

    # A generator expression keeps the summary lazy until join consumes it.
    summary_lines = (f"{incident.id}:{incident.severity}" for incident in selected)
    print("Processed:", ", ".join(summary_lines))
    print("Critical count:", len(get_critical_incidents(selected)))

    report = ReportGenerator(selected)
    html_path = report.generate_html(OUTPUT_DIR / "report.html")
    json_path = report.export_json(OUTPUT_DIR / "summary.json")
    print(f"HTML report generated: {html_path}")
    print(f"JSON summary generated: {json_path}")


if __name__ == "__main__":
    main()
