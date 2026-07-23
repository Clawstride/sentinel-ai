Database Design v0.1

We only create tables that the MVP actually needs.

1. users

Purpose:
Stores everyone who can log into SentinelAI.

Column	Type
id	UUID
name	VARCHAR
email	VARCHAR
password_hash	VARCHAR
role	VARCHAR
created_at	TIMESTAMP
2. log_events

This is the raw authentication data after upload.

Column	Type
id	UUID
incident_id	UUID (nullable initially)
timestamp	TIMESTAMP
user_id	VARCHAR
ip_address	VARCHAR
country	VARCHAR
device_type	VARCHAR
login_status	VARCHAR
is_admin	BOOLEAN

Notice:

This stores exactly what came from the CSV.

Nothing AI here.

3. incidents ⭐

This becomes our most important table.

Column	Type
id	UUID
title	VARCHAR
attack_type	VARCHAR
risk_score	INTEGER
severity	VARCHAR
status	VARCHAR
created_at	TIMESTAMP

Everything points here.

4. detection_rules

Stores every rule that fired.

Column	Type
id	UUID
incident_id	UUID
rule_name	VARCHAR
description	TEXT
points	INTEGER

Example:

Brute Force

+30
5. ai_summaries

We keep AI separate.

Column	Type
id	UUID
incident_id	UUID
summary	TEXT
recommendations	TEXT
generated_at	TIMESTAMP
6. investigation_notes

Everything the analyst writes.

Column	Type
id	UUID
incident_id	UUID
user_id	UUID
notes	TEXT
created_at	TIMESTAMP
7. reports

Generated reports.

Column	Type
id	UUID
incident_id	UUID
report_path	VARCHAR
generated_at	TIMESTAMP
Database Relationships
users
   │
   └──────────────┐

log_events ───────┐
                  │
                  ▼
              incidents
          ┌────┼─────┬─────┐
          ▼    ▼     ▼     ▼
 detection_rules
 ai_summaries
 investigation_notes
 reports

Notice something.

Everything revolves around incidents.

Exactly what we wanted.

Why this design?

Because our product isn't:

Upload Logs

Our product is:

Investigate Incidents.

That difference changes the whole architecture.