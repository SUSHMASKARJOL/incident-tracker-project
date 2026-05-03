# IT Incident Auto-Triage & Tracker

Mini Project 3 complete implementation for a Python CLI tool that reads raw IT incidents, classifies them, creates tickets in ServiceNow, Jira, and Azure Boards, and generates a final report.

## What This Project Demonstrates

- Python CLI development with `argparse`
- OOP with `Incident`, `NetworkIncident`, `AppIncident`, and `SecurityIncident`
- Inheritance, method overriding, `@property`, `__str__`, `__repr__`, and `__lt__`
- Regex-based incident type and severity detection
- Iterator protocol through `IncidentIterator`
- Batch generator through `batch_incidents`
- `map`, `filter`, and `reduce` helper functions
- Decorators for logging and retry behavior
- JSON input validation with a static method
- Mock REST integrations for ServiceNow, Jira, and Azure Boards
- Optional live REST scaffolding using `requests`
- HTML, JSON, and log file output
- Bonus `--severity` flag

## Project Structure

```text
incident_tracker/
  main.py                         CLI entry point
  config.py                       Mock flag, environment-based credentials, API URLs
  requirements.txt                Optional live API dependency
  README.md                       Setup and usage guide
  DELIVERABLE_CHECKLIST.md        Problem-statement compliance checklist
  models/
    incident.py                   Base class, subclasses, iterator, batch generator
    report.py                     HTML and JSON report generator
  services/
    servicenow.py                 ServiceNow create/update integration
    jira.py                       Jira create/update integration
    azure_boards.py               Azure Boards create integration
  utils/
    classifier.py                 Compiled regex patterns and classifier functions
    decorators.py                 @log_call and @retry
    helpers.py                    map/filter/reduce examples
  data/
    incidents.json                12 sample incident records
  output/
    report.html                   Generated report
    summary.json                  Generated JSON export
    triage.log                    Generated processing log
  tests/
    test_project.py               Lightweight validation tests
```

## Requirements

- Python 3.10 or newer
- No database required
- No live credentials required for mock mode
- Optional: `pip install -r requirements.txt` only if you want to try live API mode

## Run the Project

From the `incident_tracker` folder:

```bash
python main.py
```

Run only one severity:

```bash
python main.py --severity critical
```

Run with a custom input file:

```bash
python main.py --data data/incidents.json
```

Run tests:

```bash
python -m unittest discover -s tests
```

## Configuration

Mock mode is enabled by default:

```python
MOCK_API = True
```

For live mode, set environment variables and run with `MOCK_API=false`. The code reads credentials from the environment instead of hardcoding secrets.

```bash
set MOCK_API=false
set SERVICENOW_INSTANCE=your-instance
set SERVICENOW_USERNAME=your-user
set SERVICENOW_PASSWORD=your-password
set JIRA_DOMAIN=your-domain
set JIRA_EMAIL=your-email
set JIRA_API_TOKEN=your-token
set JIRA_PROJECT_KEY=IT
set AZURE_ORG=your-org
set AZURE_PROJECT=your-project
set AZURE_PAT=your-pat
```

## Outputs

After a successful run:

- `output/report.html`
- `output/summary.json`
- `output/triage.log`

Mock integrations print payloads and return fake ticket IDs such as `MOCK-SNOW-001`, `MOCK-JIRA-001`, and `MOCK-AZURE-001`.

## Notes

The project is designed to be demo-friendly. It performs the full pipeline in mock mode without making real API calls, but the service modules contain the payloads, URLs, headers, and response parsing needed for live integration experiments.
