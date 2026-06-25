# SubLedger

SubLedger is a FastAPI-based backend for a SaaS subscription and billing platform. It manages plans, customers, subscriptions, invoices, payments, and an append-only ledger with JWT-based authentication, PostgreSQL persistence, Redis/Celery background processing, and Docker-based local development.

## Overview

This project was designed as an Airtribe backend engineering assignment and follows a layered architecture:

- FastAPI for the API layer
- SQLAlchemy + Alembic for persistence and migrations
- Pydantic for request/response schemas
- PostgreSQL for transactional data
- Redis + Celery for asynchronous billing workflows
- JWT auth for protected mutations

## Core capabilities

- Plan creation and management
- Customer management with unique email handling
- Subscription lifecycle management including pause/resume/cancel flows
- Subscription-driven invoice generation
- Standalone one-time invoice creation
- Payment recording with idempotency protection
- Append-only ledger history for billing events
- Local Docker Compose setup for backend services

## Architecture at a glance

The backend is organized around a repository + service layer pattern:

- app/api/v1/: versioned API routes
- app/services/: business logic and orchestration
- app/repositories/: database access logic
- app/models/: SQLAlchemy models
- app/schemas/: request and response DTOs
- app/workers/: Celery tasks and automation
- app/core/: configuration, security, and shared utilities

## Tech stack

- Python 3.14
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL 18.3
- Redis
- Celery
- Pydantic v2
- Docker Compose

## Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose
- Python 3.14 (recommended for local development parity)

## Local development

### 1. Clone the repository

```bash
git clone <repository-url>
cd subledger_backend
```

### 2. Configure environment variables

Create a local environment file for Docker and app configuration:

```bash
copy .env.example .env.local
```

If no sample file is present in your environment, configure the following values in .env.local:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=subledger
POSTGRES_HOST=db
POSTGRES_PORT=5432
SECRET_KEY=change-me-to-a-long-secret-key
ADMIN_EMAIL=admin@subledger.local
ADMIN_PASSWORD_HASH=<bcrypt-hash>
RANDOM_HASH=<random-value>
```

### 3. Start the stack

```bash
docker compose up --build
```

This starts:

- the FastAPI app on port 8001
- PostgreSQL on port 8081
- Redis on port 6380
- Celery worker
- Celery beat

### 4. Run database migrations

```bash
docker compose exec web alembic upgrade head
```

### 5. Access the API

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- Health check: http://localhost:8001/health

## API surface

The API is mounted under /api/v1 and includes endpoints for:

- Auth: /api/v1/auth/login
- Plans: /api/v1/plans
- Customers: /api/v1/customers
- Subscriptions: /api/v1/subscriptions
- Invoices: /api/v1/invoices and /api/v1/invoices/generate
- Payments: /api/v1/payments/record
- Ledger: /api/v1/customers/{customer_id}/ledger

## Testing

Run the test suite with:

```bash
pytest
```

## Project status

This repository contains the backend MVP for SubLedger, including the core subscription billing domain and supporting infrastructure for local development.

## Planned live URLs

These are future deployment targets and are not currently active:

- api.subledger.obtuse.in — backend API, hosted on an EC2 instance
- subledger.obtuse.in — frontend application, planned for Next.js on Vercel

## Notes

The current implementation intentionally keeps the backend focused on the assignment scope while leaving room for future productization work such as richer billing workflows, payment provider integrations, and customer-facing experiences.
