1. Functional Requirements Specification (FRS v0.1)

Instead of writing 20 pages, we're making a practical engineering document.

Module 1 — Authentication
Functional Requirements
User can log in securely.
User can log out.
Only authenticated users can access the dashboard.
Module 2 — Log Ingestion
Functional Requirements
Upload CSV file
Validate file format
Parse authentication logs
Store raw events in database
Display upload success/failure
Module 3 — Feature Engineering

System automatically calculates:

Failed Login Count
New IP Detection
Country Change
Login Hour Deviation
New Device Detection

No user interaction.

Module 4 — Threat Detection

System detects:

Brute Force
Impossible Travel
New Device + Success
Suspicious Privileged Login

Automatically create alerts.

Module 5 — Incident Correlation

System automatically:

Groups related alerts
Creates one incident
Generates timeline
Links all events
Module 6 — Risk Scoring

Automatically calculate:

Score
Severity

Display:

Low
Medium
High
Critical
Module 7 — AI Investigation Assistant

Generate:

Incident Summary
Explanation
Suggested Actions

One LLM call per incident.

Module 8 — Investigation Workspace

Analyst can:

View timeline
Read AI summary
Add notes
Change incident status
Generate report
Module 9 — Reports

Generate PDF containing:

Incident Summary
Timeline
Risk Score
Triggered Rules
Notes
Status