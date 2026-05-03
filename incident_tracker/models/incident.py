"""Incident domain models and iteration helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Iterator

from utils.classifier import detect_severity


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


class Incident:
    """Base class shared by all incident types."""

    required_fields = {
        "id",
        "title",
        "description",
        "reported_by",
        "timestamp",
        "assigned_team",
    }

    def __init__(self, id, title, description, reported_by, timestamp, assigned_team):
        self.id = id
        self.title = title
        self.description = description
        self.reported_by = reported_by
        self.timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        self.assigned_team = assigned_team
        self._severity = None
        self.ticket_ids = {}
        self.triage_notes = []

    @staticmethod
    def validate_record(record: dict) -> bool:
        missing = Incident.required_fields - set(record)
        if missing:
            raise ValueError(f"Incident record is missing fields: {sorted(missing)}")
        if not all(record.get(field) for field in Incident.required_fields):
            raise ValueError(f"Incident record has blank required values: {record!r}")
        return True

    def combined_text(self) -> str:
        return f"{self.title} {self.description}"

    def classify(self):
        raise NotImplementedError("Subclasses must implement classify()")

    @property
    def severity(self):
        return self._severity

    @property
    def incident_type(self):
        return self.__class__.__name__

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "reported_by": self.reported_by,
            "timestamp": self.timestamp.isoformat(),
            "assigned_team": self.assigned_team,
            "severity": self.severity,
            "incident_type": self.incident_type,
            "ticket_ids": self.ticket_ids,
            "triage_notes": self.triage_notes,
        }

    def __str__(self):
        return f"{self.id} [{self.severity}] {self.title}"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id={self.id!r}, "
            f"severity={self.severity!r}, team={self.assigned_team!r})"
        )

    def __lt__(self, other):
        return SEVERITY_ORDER[self.severity] < SEVERITY_ORDER[other.severity]


class NetworkIncident(Incident):
    def __init__(self, *args, affected_host="unknown", protocol="unknown", **kwargs):
        super().__init__(*args, **kwargs)
        self.affected_host = affected_host
        self.protocol = protocol

    def classify(self):
        self._severity = detect_severity(self.combined_text())
        self.triage_notes.append(self.escalate())
        return self._severity

    def escalate(self):
        return f"Paged on-call network team for {self.id}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"affected_host": self.affected_host, "protocol": self.protocol})
        return data


class AppIncident(Incident):
    def __init__(self, *args, app_name="unknown", error_code="unknown", **kwargs):
        super().__init__(*args, **kwargs)
        self.app_name = app_name
        self.error_code = error_code

    def classify(self):
        self._severity = detect_severity(self.combined_text())
        if self.severity in {"critical", "high"}:
            self.triage_notes.append(self.get_stack_trace())
        return self._severity

    def get_stack_trace(self):
        return f"Stack trace snippet for {self.id}: {self.description[:140]}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"app_name": self.app_name, "error_code": self.error_code})
        return data


class SecurityIncident(Incident):
    def __init__(self, *args, threat_type="unknown", source_ip="unknown", **kwargs):
        super().__init__(*args, **kwargs)
        self.threat_type = threat_type
        self.source_ip = source_ip

    def classify(self):
        self._severity = detect_severity(self.combined_text())
        self.triage_notes.append(self.notify_soc())
        return self._severity

    def notify_soc(self):
        return f"SOC alert sent for {self.id}"

    def to_dict(self):
        data = super().to_dict()
        data.update({"threat_type": self.threat_type, "source_ip": self.source_ip})
        return data


class IncidentIterator(Iterator):
    """Iterate through incidents, optionally filtering by severity."""

    def __init__(self, incidents: Iterable[Incident], severity: str | None = None):
        self.incidents = list(incidents)
        self.severity = severity
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        while self.index < len(self.incidents):
            incident = self.incidents[self.index]
            self.index += 1
            if self.severity is None or incident.severity == self.severity:
                return incident
        raise StopIteration


def batch_incidents(incidents, batch_size=3):
    """Yield incidents in batches of batch_size."""
    for i in range(0, len(incidents), batch_size):
        yield incidents[i : i + batch_size]
