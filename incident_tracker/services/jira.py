"""Jira issue integration."""

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
    return {
        "critical": "Highest",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }[severity]


@log_call
@retry(times=3)
def create_ticket(incident):
    payload = {
        "fields": {
            "project": {"key": config.JIRA_PROJECT_KEY},
            "summary": incident.title,
            "description": incident.description,
            "issuetype": {"name": "Bug"},
            "priority": {"name": _priority(incident.severity)},
            "labels": [incident.incident_type, incident.severity],
        }
    }

    if config.MOCK_API:
        ticket_id = f"MOCK-JIRA-{next(_counter):03d}"
        print(f"[Jira MOCK] payload={payload} -> {ticket_id}")
        return ticket_id

    if requests is None:
        raise RuntimeError("Install requests to use live Jira mode.")

    response = requests.post(
        config.jira_url(),
        headers=_headers(),
        json=payload,
        timeout=config.REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["key"]


@log_call
@retry(times=3)
def update_priority(ticket_id, severity):
    payload = {"fields": {"priority": {"name": _priority(severity)}}}

    if config.MOCK_API:
        print(f"[Jira MOCK] update {ticket_id} payload={payload}")
        return True

    if requests is None:
        raise RuntimeError("Install requests to use live Jira mode.")

    response = requests.put(
        f"{config.jira_url()}/{ticket_id}",
        headers=_headers(),
        json=payload,
        timeout=config.REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return True


def _headers():
    token = base64.b64encode(f"{config.JIRA_EMAIL}:{config.JIRA_API_TOKEN}".encode()).decode()
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
