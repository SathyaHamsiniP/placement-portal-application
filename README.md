# Placement Workflow Coordination System (Flask, SQLAlchemy)

## Project Motivation

Campus recruitment workflows involve multi-stage approvals, eligibility filtering, and structured coordination between administrators, recruiters, and students. 

This project implements a role-based workflow coordination system that models these interactions through controlled application pipelines, approval gates, and recruiter-side analytics dashboards. The system simulates a simplified applicant-tracking and placement-drive management platform rather than a basic job-posting portal.

The system was designed to simulate a simplified recruiter-side applicant tracking workflow rather than a basic job-posting portal.

---

## Architectural Approach

The application follows a modular Blueprint-based architecture separating responsibilities into independent service layers:

* authentication service
* administrator supervision panel
* recruiter workflow workspace
* student interaction portal

This modular separation enables scalable workflow orchestration while maintaining a shared relational data layer through SQLAlchemy ORM.

---

## Recruiter Workflow Modeling

Recruiter access is restricted until administrator verification is completed. Once approved, recruiters can create placement drives and monitor applicant movement through multiple hiring stages.

Implemented recruiter-side tracking includes:

* placement-drive lifecycle management
* job visibility control (open / closed switching)
* applicant stage transitions across evaluation rounds
* branch-wise applicant distribution analysis
* aggregated hiring funnel statistics

These analytics allow recruiters to evaluate response quality instead of only counting applications.

---

## Eligibility-Based Job Visibility Logic

Unlike simple listing systems, placement drives are filtered before being displayed to students. Only drives meeting academic thresholds are shown.

Eligibility enforcement is implemented using:

* minimum CGPA filtering
* administrator approval validation
* job activity status verification

This prevents students from applying to roles outside eligibility criteria.

---

## Application Lifecycle Tracking

Applications move through recruiter-controlled evaluation stages instead of remaining static submissions.

Supported transitions include:

* submission stage
* screening stage
* interview stage
* offer stage
* acceptance stage

Each transition updates stored application state for dashboard analytics.

---

## Resume Storage Strategy

Students upload resumes during registration and may replace them later from their profile workspace.

Uploaded files are:

* sanitized before storage
* uniquely renamed using email-based prefixes
* stored outside template directories
* referenced through database path tracking

This ensures safe reuse during recruiter review.

---

## Administrator Oversight Capabilities

The administrator panel acts as a moderation layer between recruiters and students.

Administrative controls include:

* recruiter verification before activation
* placement-drive approval filtering
* searchable student directory
* searchable recruiter directory
* platform-wide activity summaries
* account deactivation support

This prevents unverified placement drives from appearing in the student interface.

---

## Duplicate Application Prevention Strategy

To maintain realistic placement workflows, repeated submissions to the same drive are restricted.

This constraint is enforced through:

* database-level uniqueness checks
* runtime validation before insertion

Students therefore interact with each placement drive only once.

---

## Recruiter Dashboard Insights

Instead of static counts, recruiter dashboards expose response-quality indicators such as:

* number of drives awaiting approval
* total applicants per recruiter
* pending evaluation workload
* branch distribution of applicants
* progression counts across evaluation stages

These metrics help simulate decision-support behavior seen in real hiring dashboards.

---

## Data Model Relationships

Core entities participating in placement coordination:

* Administrator accounts
* Recruiter organizations
* Student academic profiles
* Placement drives
* Application progression records
* Final placement confirmations

Relationships enforce structured mapping between drives, applicants, and recruiter ownership.

---

## Technology Choices

Backend services:

Flask with Blueprint modularization
SQLAlchemy ORM relational modeling
SQLite for lightweight deployment

Frontend rendering:

Jinja template engine
Bootstrap layout utilities

---

## Local Execution Workflow

Create environment:

python -m venv venv

Activate environment:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Initialize schema:

flask db init
flask db migrate
flask db upgrade

Run server:

flask run

---

## Implementation Notes

This system emphasizes workflow correctness over interface complexity. The focus of development was:

* enforcing eligibility before application
* maintaining recruiter approval pipelines
* tracking application-stage transitions
* supporting structured recruiter analytics
* preventing duplicate submissions

These components together simulate a structured placement workflow coordination environment similar to lightweight enterprise recruitment management systems.
