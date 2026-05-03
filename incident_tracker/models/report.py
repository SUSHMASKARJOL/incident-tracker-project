"""HTML and JSON report generation."""

import html
import json
from pathlib import Path

from utils.helpers import count_by_severity, count_by_team, count_by_type


class ReportGenerator:
    def __init__(self, incidents):
        self.incidents = incidents

    def generate_html(self, output_path="output/report.html"):
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        rows = "\n".join(self._row(incident) for incident in self.incidents)
        team_counts = count_by_team(self.incidents)
        severity_counts = count_by_severity(self.incidents)
        type_counts = count_by_type(self.incidents)
        team_summary = self._summary_list(team_counts)
        severity_summary = self._summary_list(severity_counts)
        type_summary = self._summary_list(type_counts)

        document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>IT Incident Auto-Triage Report</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: Arial, sans-serif; margin: 0; color: #17202a; background: #f4f7f9; }}
    header {{ background: #143642; color: white; padding: 28px 34px; }}
    main {{ padding: 28px 34px; }}
    h1, h2 {{ margin-top: 0; }}
    .summary {{ display: grid; grid-template-columns: repeat(3, minmax(180px, 1fr)); gap: 16px; margin: 20px 0; }}
    .summary div, .panel {{ background: white; border: 1px solid #d6dee5; border-radius: 8px; padding: 14px 16px; }}
    .summary strong {{ font-size: 28px; display: block; margin-top: 6px; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 22px; }}
    ul {{ padding-left: 20px; margin-bottom: 0; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 18px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #1d4e5f; color: white; }}
    tr:nth-child(even) {{ background: #f8fafc; }}
    tr:nth-child(odd) {{ background: white; }}
    .critical {{ color: #b91c1c; font-weight: bold; }}
    .high {{ color: #c2410c; font-weight: bold; }}
    .medium {{ color: #a16207; font-weight: bold; }}
    .low {{ color: #047857; font-weight: bold; }}
    code {{ background: #eef2ff; padding: 2px 4px; border-radius: 4px; }}
    @media (max-width: 900px) {{ .summary, .grid {{ grid-template-columns: 1fr; }} table {{ font-size: 13px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>IT Incident Auto-Triage Report</h1>
    <p>Generated after classification, mock ticket creation, and tracker updates.</p>
  </header>
  <main>
    <section class="summary">
      <div>Total incidents<strong>{len(self.incidents)}</strong></div>
      <div>Critical incidents<strong>{severity_counts.get("critical", 0)}</strong></div>
      <div>Teams involved<strong>{len(team_counts)}</strong></div>
    </section>
    <section class="grid">
      <div class="panel"><h2>By Team</h2><ul>{team_summary}</ul></div>
      <div class="panel"><h2>By Severity</h2><ul>{severity_summary}</ul></div>
      <div class="panel"><h2>By Type</h2><ul>{type_summary}</ul></div>
    </section>
    <h2>Processed Incidents</h2>
    <table>
      <thead>
        <tr>
          <th>ID</th><th>Title</th><th>Type</th><th>Severity</th>
          <th>Assigned Team</th><th>ServiceNow</th><th>Jira</th><th>Azure Boards</th><th>Triage Notes</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </main>
</body>
</html>
"""
        output.write_text(document, encoding="utf-8")
        return output

    def export_json(self, output_path="output/summary.json"):
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps([incident.to_dict() for incident in self.incidents], indent=2),
            encoding="utf-8",
        )
        return output

    def _row(self, incident):
        tickets = incident.ticket_ids
        notes = "<br>".join(html.escape(note) for note in incident.triage_notes) or "-"
        return f"""<tr>
  <td><code>{html.escape(incident.id)}</code></td>
  <td>{html.escape(incident.title)}</td>
  <td>{html.escape(incident.incident_type)}</td>
  <td class="{incident.severity}">{html.escape(incident.severity)}</td>
  <td>{html.escape(incident.assigned_team)}</td>
  <td>{html.escape(tickets.get("snow", "-"))}</td>
  <td>{html.escape(tickets.get("jira", "-"))}</td>
  <td>{html.escape(tickets.get("azure", "-"))}</td>
  <td>{notes}</td>
</tr>"""

    def _summary_list(self, counts):
        return "".join(
            f"<li><strong>{html.escape(str(label))}</strong>: {count}</li>"
            for label, count in sorted(counts.items())
        )
