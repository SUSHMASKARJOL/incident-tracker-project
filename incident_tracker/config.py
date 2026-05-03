"""Configuration for the IT Incident Auto-Triage project.

Credentials are read from environment variables so secrets are never hardcoded
in the service modules.
"""

import os


MOCK_API = os.getenv("MOCK_API", "true").lower() == "true"
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))

SERVICENOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE", "demo-instance")
SERVICENOW_USERNAME = os.getenv("SERVICENOW_USERNAME", "demo-user")
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD", "demo-password")

JIRA_DOMAIN = os.getenv("JIRA_DOMAIN", "demo-domain")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "demo@example.com")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "demo-token")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "IT")

AZURE_ORG = os.getenv("AZURE_ORG", "demo-org")
AZURE_PROJECT = os.getenv("AZURE_PROJECT", "demo-project")
AZURE_PAT = os.getenv("AZURE_PAT", "demo-pat")


def servicenow_url():
    return f"https://{SERVICENOW_INSTANCE}.service-now.com/api/now/table/incident"


def jira_url():
    return f"https://{JIRA_DOMAIN}.atlassian.net/rest/api/3/issue"


def azure_boards_url():
    return (
        f"https://dev.azure.com/{AZURE_ORG}/{AZURE_PROJECT}/_apis/wit/workitems/"
        "$Bug?api-version=7.1"
    )
