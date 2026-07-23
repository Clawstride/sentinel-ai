High-Level System Architecture

This is the architecture we'll follow.

                SentinelAI

          ┌──────────────────────┐
          │     React Frontend    │
          └──────────┬────────────┘
                     │
                REST API
                     │
          ┌──────────▼──────────┐
          │    FastAPI Backend   │
          └──────────┬──────────┘
                     │
     ┌───────────────┼────────────────┐
     │               │                │
     ▼               ▼                ▼

 Log Processor   Detection Engine   AI Service

     │               │                │
     └──────┬────────┴────────┬───────┘
            ▼                 ▼

      PostgreSQL         OpenAI / Ollama

            │
            ▼

      Incident Reports



Component Responsibilities

Frontend

Dashboard
Upload
Investigation Workspace
Reports

Backend

Responsible for:

Authentication
APIs
Processing
Detection
Correlation
Risk
Report Generation

AI Service

Responsible for:

Summaries
Explanations
Recommendations

Database

Stores:

Users
Events
Incidents
Notes
Reports