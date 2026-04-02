# exit.tech — Fergie/Senty Workflow

Multi-agent development workflow using two AI agents:
- **Fergie (Claude Code):** Builder — writes components, follows specs
- **Senty (Codex):** Reviewer — checks specs, catches issues, never writes code
- **Alisher:** Architect — creates issues, makes final decisions, merges

---

## Session Setup (one-time per session)

```bash
# In Fergie's pane
tmux-bridge name "$(tmux-bridge id)" fergie

# In Senty's pane
tmux-bridge name "$(tmux-bridge id)" senty

# Verify
tmux-bridge list
```

---

## Standard Component Workflow

### 1. Issue Creation (Alisher)

Alisher creates a GitHub issue with:
- Component name
- Link to spec file (or spec written inline)
- Success criteria — what LGTM looks like

### 2. Spec First (Fergie)

Before any code:

```bash
gh issue view XX
```

- Read issue, confirm understanding
- If spec file doesn't exist — write it to `specs/<component>.md` first
- Ask if anything is ambiguous

### 3. Branch

```bash
git checkout main
git pull origin main
git checkout -b issue-XX-component-name
```

### 4. Build (Fergie)

- Read `CLAUDE.md`
- Read `specs/<component>.md`
- Read `src/data/exits.js` for data shape
- Build component in `src/components/<component>.js`
- Check visually at http://localhost:8000
- Fix until it looks and behaves right

### 5. Commit

```bash
git add src/components/<component>.js
git commit -m "feat: add <component> component

Implements spec in specs/<component>.md.

Closes #XX

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

git push origin issue-XX-component-name
```

### 6. Handoff to Senty (Fergie)

Post GitHub comment:

```
Fergie: <component> built and pushed.

Implementation:
- Branch: issue-XX-component-name
- Commit: <SHA>

Spec compliance:
- [x] Matches spec inputs
- [x] Matches spec DOM output
- [x] No data fetching inside component
- [x] No inline styles
- [x] Correct data shape from exits.js
- [x] Renders at localhost:8000

Not verified:
- <anything not checked>

Ready for review, Senty!
```

Notify Senty:

```bash
tmux-bridge read senty 20
tmux-bridge message senty '/btw check issue #XX'
tmux-bridge read senty 20
tmux-bridge keys senty Enter
```

### 7. Review (Senty)

```bash
gh issue view XX
```

- Read spec
- Read component file
- Check all items in CODEX.md checklist

Post findings:

```
Senty: Reviewed — Round 1

Findings:
[HIGH] src/components/exit-form.js:34 — fetches data internally, violates spec
[LOW] src/components/exit-form.js:12 — variable name 'el' not descriptive

Overall: needs fixes
```

Notify Fergie:

```bash
tmux-bridge read fergie 20
tmux-bridge message fergie '/btw check issue #XX'
tmux-bridge read fergie 20
tmux-bridge keys fergie Enter
```

### 8. Fix Loop (Fergie → Senty)

Fergie addresses findings → commits → comments → pings Senty.
Repeat until Senty posts LGTM.

```
Senty: LGTM ✓

All spec checks pass. Clear to merge.
```

### 9. Merge (Alisher)

```bash
gh pr create --title "feat: <component> component" --base main
gh pr merge XX --squash --delete-branch
```

---

## Handoff Status Tags

Use in tmux pings: `/btw [TAG] check issue #XX — one-line summary`

| Tag | Meaning |
|-----|---------|
| `READY` | Complete, all success criteria met |
| `PARTIAL` | Incomplete — state what's still pending |
| `FIX` | Previous findings addressed, ready for re-review |
| `BLOCKED` | Cannot proceed — need input or decision |

Examples:
```
/btw READY check issue #3 — exit-form component complete
/btw FIX check issue #3 — inline style removed, paths corrected
/btw BLOCKED issue #4 — share-card needs design decision on image format
```

---

## Clarification Triggers

Stop and ask Alisher before proceeding when:

- Issue has no clear success criteria — ask what LGTM looks like
- Spec is missing or ambiguous — write draft spec and confirm before building
- Change touches `src/data/exits.js` — data shape is the contract, changes ripple everywhere
- Change touches `styles/base.css` — design tokens affect the whole system
- Something unexpected breaks at http://localhost:8000

---

## Branch Rules

- `main` — stable, always works at localhost:8000
- `issue-XX-name` — one branch per issue
- Never commit directly to main
- Squash merge only — clean history

---

## GitHub Is The Record

- Every handoff, finding, fix, and LGTM lives on the GitHub issue
- tmux-bridge is for nudges only — not decisions
- If you post a new comment, always ping the other agent — unpinged updates are invisible

---

## Communication Protocol

| Agent | Comment prefix |
|-------|---------------|
| Fergie | `Fergie:` |
| Senty | `Senty:` |
| Alisher | (none) |

---

## After Every Merge

Fergie updates `ROADMAP.md` — check the completed item, note any lessons.
No separate lessons file needed for this project — ROADMAP and CLAUDE.md are enough.
