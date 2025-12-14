---
id: 0003
title: Plan Web App Architecture
stage: plan
date: 2025-12-10
surface: agent
model: claude-opus-4-5-20251101
feature: 002-web-app-transformation
branch: 001-basic-todo-ops
user: interactive
command: /sp.plan
labels: ["planning", "architecture", "fastapi", "nextjs", "postgresql", "jwt"]
links:
  spec: specs/002-web-app-transformation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-web-app-transformation/plan.md
  - specs/002-web-app-transformation/research.md
  - specs/002-web-app-transformation/data-model.md
  - specs/002-web-app-transformation/quickstart.md
  - specs/002-web-app-transformation/contracts/api.yaml
tests:
  - null
---

## Prompt

/sp.plan - Execute the implementation planning workflow using the plan template to generate design artifacts.

## Response snapshot

Generated comprehensive implementation plan with Phase 0 and Phase 1 artifacts:

**Phase 0: Research (research.md)**
- Better Auth + FastAPI integration pattern (frontend-only auth, backend JWT verification)
- Neon PostgreSQL connection pooling best practices
- JWT claim structure (sub, exp, iat)
- Next.js 16+ App Router component strategy
- SQLModel entity design patterns
- CORS configuration for cookie-based auth

**Phase 1: Design (plan.md, data-model.md, contracts/api.yaml, quickstart.md)**

**Architecture Decisions (4 ADRs documented):**
1. ADR-001: Monorepo with separate backend/frontend directories
2. ADR-002: JWT storage in httpOnly cookies (XSS protection)
3. ADR-003: SQLModel over raw SQLAlchemy (type safety)
4. ADR-004: Better Auth for frontend authentication

**Key Artifacts:**
- `plan.md`: Technical context, project structure, security implementation, testing strategy
- `data-model.md`: User/Task entities, SQLModel definitions, TypeScript interfaces, migrations
- `contracts/api.yaml`: OpenAPI 3.1 spec with all CRUD endpoints
- `quickstart.md`: Step-by-step setup guide for development environment

**Constitution Check:**
- 3 violations identified (CLI-only, in-memory, no dependencies)
- All justified as Phase 1 → Phase 2 transition
- Constitution amendment required before implementation (version 1.0.0 → 2.0.0)

## Outcome

- Impact: Created complete technical blueprint for web app transformation
- Tests: N/A (planning phase)
- Files: 5 artifacts created in specs/002-web-app-transformation/
- Next prompts: Update constitution (/sp.constitution), then /sp.tasks to generate implementation tasks
- Reflection: Constitution amendment is blocking item; must be resolved before implementation

## Evaluation notes (flywheel)

- Failure modes observed: Current branch (001-basic-todo-ops) caused script to detect wrong feature; manually specified correct feature
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run /sp.constitution to update to Phase 2 principles before /sp.tasks
