# ~~EXIT~~
> exit as culture

Social network for logging exits from dependencies.
Dark. Minimal. Sovereign.

---

## Steps: 0 → first prompt

### 0. Clone and enter
```bash
git clone https://github.com/YOUR_USERNAME/exit-tech.git
cd exit-tech
```

### 1. Run locally
```bash
python3 -m http.server 8000
```
Open http://localhost:8000 — you should see the feed with mock exits.

### 2. Install Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### 3. Enable auto mode + start session
```bash
claude --enable-auto-mode
```
Then inside session press `Shift+Tab` to cycle to auto mode.

### 4. Your first prompt

```
Read CLAUDE.md and specs/exit-card.md.
Then use the verifier agent to verify src/components/exit-card.js
against the spec. Report pass/fail for each check.
```

### 5. Next prompts to build Phase 1

**Spec then build pattern — always in this order:**

```
Read CLAUDE.md and specs/exit-form.md.
Use the builder agent to create src/components/exit-form.js.
Then use the verifier agent to verify it. Fix any issues until PASS.
```

```
Read CLAUDE.md.
Use the builder agent to create src/components/profile-header.js.
Input: profile object from src/data/exits.js profiles array.
Output: <div class="profile-header"> showing handle, bio, exit count.
Write the spec to specs/profile-header.md first, then build.
```

---

## Project structure

```
exit-tech/
├── index.html              # shell — loads app
├── CLAUDE.md               # agent context — read every session
├── .claudeignore           # auto mode safety boundaries
├── .claude/
│   ├── agents/
│   │   ├── builder.md      # writes code
│   │   └── verifier.md     # reviews only, never writes
│   └── commands/
│       └── new-component.md
├── src/
│   ├── app.js              # init, router, handlers
│   ├── components/
│   │   └── exit-card.js    # ✓ built
│   ├── data/
│   │   └── exits.js        # mock data + shape definition
│   └── utils/
│       ├── storage.js      # localStorage → Codex later
│       ├── date.js         # formatting
│       └── share.js        # share → Android native later
├── styles/
│   ├── base.css            # tokens, reset, typography
│   ├── layout.css          # grid, containers
│   └── components.css      # cards, buttons, badges
└── specs/
    └── exit-card.md        # ✓ specced
```

---

## Phase 1 build order

- [x] exit-card component
- [ ] exit-form component (post new exit)
- [ ] profile-header component
- [ ] counter-badge modal (who else exited)
- [ ] share-card component (shareable image)
- [ ] category filter bar

---

## Stack decisions

| Layer | Now | Phase 4 |
|---|---|---|
| Storage | localStorage via utils/storage.js | Codex |
| Messaging | — | Waku |
| Identity | random local ID | Status DID / wallet |
| Hosting | GitHub Pages | Decentralised |

---

## Run

```bash
python3 -m http.server 8000
```

No build step. No node_modules. No config.
Open file, edit, refresh. Done.
