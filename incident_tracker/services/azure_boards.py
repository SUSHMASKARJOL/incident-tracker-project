"""Azure Boards work item integration."""

import base64
import itertools

import config
from utils.decorators import log_call, retry

try:
    import requests
except ImportError:
    requests = None


_counter = itertools.count(1)


def _priority(severity):
    return {"critical": 1, "high": 2, "medium": 3, "low": 4}[severity]


@log_call
@retry(times=3)
def create_ticket(incident):
    payload = [
        {"op": "add", "path": "/fields/System.Title", "value": incident.title},
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Common.Priority",
            "value": _priority(incident.severity),
        },
        {
            "op": "add",
            "path": "/fields/System.AssignedTo",
            "value": incident.assigned_team,
        },
        {"op": "add", "path": "/fields/System.Description", "value": incident.description},
    ]

    if config.MOCK_API:
        ticket_id = f"MOCK-AZURE-{next(_counter):03d}"
        print(f"[Azure Boards MOCK] payload={payload} -> {ticket_id}")
        return ticket_id

    if requests is None:
        raise RuntimeError("Install requests to use live Azure Boards mode.")

    response = requests.post(
        config.azure_boards_url(),
        headers=_headers(),
        json=payload,
        timeout=config.REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return str(response.json()["id"])


def _headers():
    token = base64.b64encode(f":{config.AZURE_PAT}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json-patch+json",
    }
