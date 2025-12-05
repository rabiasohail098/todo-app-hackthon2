---
id: 0002
title: Clarify Todo Ops CLI Design
stage: misc
date: 2025-12-05
surface: agent
model: claude-haiku-4-5-20251001
feature: 001-basic-todo-ops
branch: 001-basic-todo-ops
user: user
command: /sp.clarify
labels: ["cli-design", "interaction-model", "command-syntax", "display-format"]
links:
  spec: specs/001-basic-todo-ops/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-basic-todo-ops/spec.md
tests:
  - none
---

## Prompt

Run clarification workflow on Basic Todo Operations spec to identify and resolve ambiguities before planning phase.

## Response snapshot

Conducted 4 clarification questions addressing CLI interaction design ambiguities:

1. **Command Invocation**: Separate command then prompts (vs. single-line args or menu)
2. **Display Format**: Table with columns (vs. list or verbose format)
3. **Command Names**: Short verbs: add, view, update, delete, mark, exit
4. **Mark Complete Syntax**: Command with ID on same line (e.g., `mark 2`)

All answers aligned with Phase 1 MVP approach and Unix CLI conventions. Updated spec with 4 clarifications + enhanced 6 functional requirements to reflect command syntax specifics.

## Outcome

- ✅ Impact: CLI interaction model now fully specified and unambiguous. Functional requirements enhanced from 12 to 13 items with explicit command invocation details. Developers have clear interface contract (separate prompts, table display, command+ID syntax). Reduces implementation ambiguity and testing rework. Specification now ready for architectural planning.
- 🧪 Tests: Clarifications provide concrete test cases (e.g., typing `mark 2` must mark task 2 complete; `view` must display table with 4 columns)
- 📁 Files: `specs/001-basic-todo-ops/spec.md` updated with Clarifications section + enhanced FR-001 through FR-013
- 🔁 Next prompts: `/sp.plan` to create implementation architecture; ready for task generation after plan approval
- 🧠 Reflection: All 4 questions addressed highest-impact ambiguities (interaction model, display format, command syntax). Answers follow best practices for Phase 1 (simple, learner-friendly, Unix-aligned). Spec now sufficiently precise for implementation without further clarification loops.

## Evaluation notes (flywheel)

- Failure modes observed: none - all questions answered decisively; no contradictions introduced
- Graders run and results (PASS/FAIL): Specification update PASS - clarifications integrated into Clarifications section + functional requirements; no lingering vague language; column format and command syntax explicit
- Prompt variant (if applicable): baseline - spec was well-structured, only CLI interaction details needed clarification
- Next experiment (smallest change to try): Validate spec updates align with constitution compliance before proceeding to `/sp.plan`
