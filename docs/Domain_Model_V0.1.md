Domain Model v0.1

These are the core entities (nouns) in our system.

1. User

Represents the SOC analyst using SentinelAI.

Attributes:

User ID
Name
Email
Password
Role
2. Raw Log Event

Represents one authentication event.

Examples:

09:02
User A
Login Success
India
Chrome

Attributes:

Timestamp
User ID
IP Address
Country
Device
Login Status
Admin Flag
3. Detection Rule

Represents one security rule.

Examples:

Brute Force
Impossible Travel
New Device
Suspicious Admin Login

Each rule has:

Name
Description
Trigger Logic
Risk Points
4. Incident ⭐ (Most Important)

This is the heart of the product.

An Incident is a collection of related log events.

Instead of:

Event 1

Event 2

Event 3

We get:

Incident #102

Contains:

Event 1
Event 2
Event 3

Everything revolves around Incidents.

5. Risk Assessment

Every incident gets:

Score
Severity
Triggered Rules

Example:

Score: 82

Severity: High
6. AI Summary

Generated using the LLM.

Contains:

Summary
Explanation
Recommended Actions
7. Investigation

The analyst's work.

Contains:

Notes
Status

Statuses:

Open
Investigating
Resolved
False Positive
8. Report

Generated at the end.

Contains:

Incident Summary
Timeline
Risk
Notes
Status
Relationships

This is the important part.

User

↓

uploads

↓

Raw Log Events

↓

Detection Rules

↓

Incident

↓

Risk Assessment

↓

AI Summary

↓

Investigation

↓

Report

This is literally the life cycle of data in SentinelAI.