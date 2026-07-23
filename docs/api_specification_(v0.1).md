API Specification (v0.1)

Think of APIs as the contract between the frontend and backend.

Authentication
Method	Endpoint	Purpose
POST	/auth/login	Login user
POST	/auth/logout	Logout
GET	/auth/me	Current user
Log Upload
Method	Endpoint	Purpose
POST	/logs/upload	Upload CSV/JSON
GET	/logs	View uploaded logs
Incident
Method	Endpoint	Purpose
GET	/incidents	List incidents
GET	/incidents/{id}	View incident
PATCH	/incidents/{id}	Update status
AI
Method	Endpoint	Purpose
POST	/ai/summarize/{incident_id}	Generate AI summary
Reports
Method	Endpoint	Purpose
GET	/reports/{incident_id}	Download report

That's all.

Only 8 APIs.

Simple.

2. Backend Architecture

Instead of folders...

We think in modules.

Backend

├── Authentication
│
├── Log Processing
│
├── Detection Engine
│
├── Incident Manager
│
├── AI Service
│
├── Reporting
│
└── Common Utilities

Every module should work independently.

3. Folder Structure
backend/

app/

api/

models/

schemas/

services/

repositories/

utils/

config/

tests/

Notice

No random folders.

Everything has one responsibility.

Frontend Structure
frontend/

pages/

components/

hooks/

services/

layouts/

utils/

assets/
4. UI Specification

Forget Figma.

These are our pages.

Login

Purpose

Authenticate analyst.

Components

Email
Password
Login Button
Dashboard

Purpose

Overview of all incidents.

Components

Statistics Cards
Incident Table
Search
Filters
Upload Button
Upload Page

Purpose

Upload authentication logs.

Components

Drag & Drop
Upload Button
Validation
Incident Details ⭐

This is the flagship page.

Components

AI Summary
Timeline
Risk Score
Detection Rules
Notes
Status
Generate Report

This is where analysts spend 90% of their time.

Report Page

Shows

Summary
Timeline
Notes
Risk
Export PDF

That's it.

Only 5 screens.

5. GitHub Workflow

We're using Git properly.

main

Always stable.

develop

Integration branch.

Feature branches

feature/log-upload

feature/risk-score

feature/dashboard

Nobody commits directly to main.

6. Branch Ownership

Person A

Backend

Person B

Detection + AI

Person C

Frontend

Merge into develop.

After testing

↓

Merge into main.

7. Coding Standards

Every function

One responsibility.

No function longer than about 40 lines unless justified.

Meaningful names.

Comments explain why, not what.

No duplicated code.

8. Testing Strategy

Every feature passes these tests.

Upload

Can upload valid CSV.

Reject invalid CSV.

Detection

Correct rules trigger.

False positives minimized.

AI

Summary generated.

No empty response.

Reports

Correct PDF generated.

Dashboard

Correct incident count.

Filters work.

9. Sprint Roadmap
Sprint 0

Planning

Documentation

Architecture

✅

Sprint 1

Backend Foundation

FastAPI
PostgreSQL
Authentication
Upload
Sprint 2

Detection Engine

Feature Engineering

Risk Score

Sprint 3

Incident Management

Timeline

Notes

Status

Sprint 4

AI Integration

LLM

Reports

Sprint 5

Frontend

Dashboard

Investigation Workspace

Sprint 6

Testing

Bug Fixes

Deployment

Presentation

10. Project Principles

These become our commandments.

Rule 1

If it doesn't help investigate incidents,

don't build it.

Rule 2

One polished workflow

beats

ten incomplete features.

Rule 3

Understand before coding.

Rule 4

Everything must be modular.

Rule 5

Every feature must be demoable.

Rule 6

No "we'll fix it later."

If it's merged,

it should work.