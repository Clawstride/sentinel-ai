Task Breakdown Document (TBD) v1.0

This is the execution plan for the MVP.

Sprint 1 — Foundation (Week 1)
Task 1.1 — Repository Setup

Owner: Everyone

Create GitHub repository
Clone locally
Create main and develop branches
Add .gitignore
Create README
Initial commit

Done When

Everyone can clone and run the project.
Task 1.2 — Backend Setup

Owner: Backend

Create FastAPI project
Setup folder structure
Configure environment variables
Configure database connection

Done When

FastAPI server starts successfully.
Task 1.3 — Frontend Setup

Owner: Frontend

Create React project
Install Tailwind
Setup routing
Create layouts

Done When

Empty dashboard loads.
Task 1.4 — Database Setup

Owner: Backend

PostgreSQL
SQLAlchemy
Create tables
Database migration

Done When

Tables created successfully.
Sprint 2 — Log Processing
Task 2.1

CSV Upload

Task 2.2

CSV Validation

Task 2.3

Log Parsing

Task 2.4

Store Events

Task 2.5

Display Upload Status

Done When

Uploading a CSV stores events in the database.

Sprint 3 — Security Engine
Task 3.1

Failed Login Count

Task 3.2

New IP Detection

Task 3.3

Country Change

Task 3.4

Off-Hours Login

Task 3.5

New Device Detection

Task 3.6

Brute Force Rule

Task 3.7

Impossible Travel Rule

Task 3.8

New Device Rule

Task 3.9

Privileged Login Rule

Task 3.10

Risk Score

Done When

Detection engine creates incidents.

Sprint 4 — Incident Management
Task 4.1

Group events into incidents.

Task 4.2

Generate timeline.

Task 4.3

Incident list API.

Task 4.4

Incident detail page.

Task 4.5

Status update.

Task 4.6

Notes.

Done When

Analyst can investigate an incident.

Sprint 5 — AI Integration
Task 5.1

Prompt Design

Task 5.2

LLM API

Task 5.3

Summary Generation

Task 5.4

Recommendations

Task 5.5

Store AI Output

Done When

Every incident has an AI summary.

Sprint 6 — Reports
Task 6.1

PDF Template

Task 6.2

Generate Report

Task 6.3

Download Report

Done When

Analyst downloads report.

Sprint 7 — Dashboard
Task 7.1

Statistics Cards

Task 7.2

Incident Table

Task 7.3

Filters

Task 7.4

Upload Button

Task 7.5

Navigation

Done When

Complete application works.

Sprint 8 — Polish
Bug Fixes
UI Improvements
Testing
Demo Dataset
Presentation
Team Responsibilities
Person A

Backend

FastAPI
Database
Upload
APIs
Person B

Security Engine

Features
Rules
AI
Reports
Person C

Frontend

React
Dashboard
Investigation Page
UI

Everyone reviews everyone else's code before merging.

Definition of Done

A task is complete only if:

Code works
Code reviewed
Tested
No major bugs
Documentation updated
Successfully merged

Otherwise it is not done.