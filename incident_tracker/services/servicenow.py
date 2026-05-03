"""ServiceNow incident integration."""

import itertools

import config
from utils.decorators import log_call, retry

try:
    import requests
except ImportError:  # requests is optional in the problem statement.
    requests = None


_counter = itertools.count(1)


def _urgency(severity):
    return {"critical": "1", "high": "1", "medium": "2", "low": "3"}[severity]


@log_call
@retry(times=3)
def create_ticket(incident):
    payload = {
        "short_description": incident.title,
        "description": incident.description,
        "urgency": _urgency(incident.severity),
        "category": incident.incident_type,
        "assignment_group": incident.assigned_team,
    }

    if config.MOCK_API:
        ticket_id = f"MOCK-SNOW-{next(_counter):03d}"
        print(f"[ServiceNow MOCK] payload={payload} -> {ticket_id}")
        return ticket_id

    if requests is None:
        raise RuntimeError("Install requests to use live ServiceNow mode.")

    response = requests.post(
        config.servicenow_url(),
        auth=(config.SERVICENOW_USERNAME, config.SERVICENOW_PASSWORD),
        json=payload,
        timeout=config.REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["result"]["sys_id"]


@log_call
@retry(times=3)
def update_status(ticket_id, status="In Progress"):
    payload = {"state": status}

    if config.MOCK_API:
        print(f"[ServiceNow MOCK] update {ticket_id} payload={payload}")
        return True

    if requests is None:
        raise RuntimeError("Install requests to use live ServiceNow mode.")

    response = requests.patch(
        f"{config.servicenow_url()}/{ticket_id}",
        auth=(config.SERVICENOW_USERNAME, config.SERVICENOW_PASSWORD),
        json=payload,
        timeout=config.REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return True
