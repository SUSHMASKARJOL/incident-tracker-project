# Deliverable Checklist

This checklist maps the project files to the Mini Project 3 problem statement.

## Core Requirements

- [x] CLI entry point: `main.py`
- [x] Configuration file with `MOCK_API`: `config.py`
- [x] Incident base class: `models/incident.py`
- [x] Three subclasses: `NetworkIncident`, `AppIncident`, `SecurityIncident`
- [x] `classify()` overridden in each subclass
- [x] `severity` property
- [x] `to_dict()`, `__str__`, `__repr__`, and `__lt__`
- [x] `IncidentIterator` with optional severity filtering
- [x] `ReportGenerator.generate_html()`
- [x] `ReportGenerator.export_json()`
- [x] Regex classifier with `detect_type()` and `detect_severity()`
- [x] `@log_call` and `@retry(times=3)` decorators
- [x] `map`, `filter`, and `reduce` helper functions
- [x] Batch generator: `batch_incidents()`
- [x] 12 sample JSON records in `data/incidents.json`
- [x] Generated `output/report.html`

## Integrations

- [x] ServiceNow mock create ticket
- [x] ServiceNow mock update status
- [x] Jira mock create ticket
- [x] Jira mock update priority
- [x] Azure Boards mock create ticket
- [x] Live-mode request payload scaffolding
- [x] Credentials read from config/environment variables

## Bonus / Stretch Goals

- [x] `--severity` filter
- [x] Generator expression in `main.py`
- [x] Static JSON schema validation method on `Incident`
- [x] Optional live API scaffolding for all three platforms

## Generated Outputs

- [x] `output/report.html`
- [x] `output/summary.json`
- [x] `output/triage.log`

