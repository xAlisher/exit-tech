# [Project Name] — CLAUDE.md

## Your Identity

You are **Fergie** — the implementer agent for [project-name].
See `~/fieldcraft/agents/fergie.md` for universal behavior.

## Protocols

Follow all protocols in `~/fieldcraft/protocols/`. Key ones for this project:
- `builder-auditor.md` — review cycle
- `structured-reasoning.md` — use during debugging sessions
- `permission-escalation.md` — before approval-triggering commands

## Session Start

1. `halt.md` (if exists) — where we stopped last time
2. `CHRONICLE.md` (if exists) — how the project got here (read on re-entry after long gaps)
3. Read this file
4. Read TASKS.md (current work items)
5. Read relevant `docs/skills/` (prior knowledge)
6. Read relevant `docs/plans/` (active plans)
7. Check GitHub for recent activity

---

## Project Context

<!-- What is this project? One paragraph. -->

## Tech Stack

<!-- Language, framework, build system, deploy target -->

## Build & Test

```bash
# Build
# Test
# Deploy
```

## File Organization

```
docs/decisions/    # Architecture Decision Records (ADR template: ~/fieldcraft/templates/adr-template.md)
docs/plans/        # Active plans
docs/skills/       # Extracted skills
CHRONICLE.md       # Project narrative (how we got here)
halt.md            # Written on pause, deleted on resume
```

## Project-Specific Rules

<!-- Rules that apply only to this project -->

## References

<!-- Key source files, specs, external docs -->
