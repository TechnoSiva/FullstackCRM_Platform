# Enterprise CRM & Sales Intelligence Platform

Production-style full-stack CRM built with FastAPI + React, aligned to [`AGENT.md`](./AGENT.md) and phased delivery in [`Phases.md`](./Phases.md).

## Overview
This project delivers a Salesforce-like CRM with enterprise architecture and operational analytics:
- Lead, Opportunity, and Activity management
- Pipeline tracking with stage and probability updates
- KPI dashboard and revenue trend analytics
- Role-Based Access Control (`ADMIN`, `MANAGER`, `SALES`)
- AI-assisted lead scoring (scikit-learn logistic regression)

## Architecture
Backend follows strict layering:
- `Router -> Service -> Repository -> DB`

Key implementation rules in effect:
- Thin routers (validation, auth dependencies, service delegation)
- Business logic centralized in services
- DB access isolated in repositories
- Pydantic request/response contracts
- Server-side RBAC enforcement on protected endpoints

## Tech Stack
- Backend: FastAPI, SQLAlchemy, Pydantic, JWT (`python-jose`), bcrypt
- ML: scikit-learn, joblib
- Migrations: Alembic
- Frontend: React (Vite), Axios, Recharts
- Testing: pytest, Vitest, React Testing Library

## Repository Layout
- `backend/app/` - API, domain, services, repositories, ML, security
- `backend/tests/` - backend test suite (auth, CRUD, analytics, service-layer)
- `backend/alembic/` - migration environment + initial schema
- `frontend/src/` - app pages, components, auth context, API client
- `Phases.md` - implementation phase tracking

## Implemented Features
- Auth: `/auth/register`, `/auth/login`, `/auth/me`
- User admin (ADMIN only): `/users` CRUD-like management
- Leads: list/create/get/update/delete with assignment and score updates
- Opportunities: list/create/update/delete + kanban stage persistence
- Activities: create/list by lead
- Analytics: `/dashboard/kpis`, `/dashboard/revenue-trend`
- Frontend: premium role-aware UI, charts, forms, drag/drop workflow
- Global 401 handling in frontend (auto session reset on invalid/expired token)

## Quick Start
### 1) Backend
```bash
cd backend
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload
```
Backend: `http://127.0.0.1:8000`

### 2) Frontend
```bash
cd frontend
cmd /c npm install
cmd /c npm run dev
```
Frontend: `http://127.0.0.1:5173`

## Database Migration
```bash
cd backend
py -m alembic -c alembic.ini upgrade head
```

## ML Model Training
```bash
cd backend
py app/ml/train_model.py
```
Artifact output: `backend/app/ml/lead_scoring_model.joblib`

## Testing
### Backend
```bash
cd backend
py -m pytest
```

### Frontend
```bash
cd frontend
cmd /c npm test
```

## API Security and RBAC
- JWT required for protected routes
- Roles:
  - `ADMIN`: full access + user management
  - `MANAGER`: analytics + broad CRM visibility
  - `SALES`: assigned-lead scope, pipeline/activity updates within scope

## Current Compliance Status
- `Phases.md`: implemented through Phase 5
- `AGENT.md`: requirements satisfied
- Planned TODO retained by design: manager team-scoping refinement when team model is introduced

## First Login
If database is empty, register an admin first:
- `POST /auth/register` with role `ADMIN`

Then login from UI or `/auth/login`.
