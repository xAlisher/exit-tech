# exit.tech — Stack & Architecture

## Core decision: Vanilla JS + ES modules
No framework. No build step. No node_modules.

### Why
- One file, one responsibility — agents read whole files, edit whole files
- No build step gap between what agent writes and what browser runs
- Any contributor opens a file and understands it immediately — no framework gatekeeping
- Philosophically aligned — open, legible, no black boxes
- Modular structure maps directly onto future Waku/Codex migration

### Run locally
```bash
python3 -m http.server 8000
```
Open http://localhost:8000 — never open index.html directly as file://

## Project structure
```
exit-tech/
├── index.html                  # shell only, loads app
├── CLAUDE.md                   # agent context, read every session
├── .claudeignore               # auto mode safety boundaries
├── .gitignore
├── PROJECT.md                  # vision and concept (this ecosystem)
├── STACK.md                    # technical decisions (this file)
├── ROADMAP.md                  # phases and milestones
├── .claude/
│   ├── agents/
│   │   ├── builder.md          # writes code
│   │   └── verifier.md         # reviews only, never writes
│   └── commands/
│       └── new-component.md    # /new-component slash command
├── src/
│   ├── app.js                  # init, router, handlers
│   ├── components/             # one file per component, one default export
│   │   └── exit-card.js        # ✓ built
│   ├── data/
│   │   └── exits.js            # mock data + shape definition (source of truth)
│   └── utils/
│       ├── storage.js          # localStorage → Codex in Phase 4
│       ├── date.js             # formatting utilities
│       └── share.js            # share → Android native in Phase 3
├── styles/
│   ├── base.css                # tokens, reset, typography
│   ├── layout.css              # grid, containers, spacing
│   └── components.css          # cards, buttons, badges, tags
└── specs/
    └── exit-card.md            # ✓ specced
```

## Data shape — source of truth
All components consume this shape. Defined in src/data/exits.js.
When switching to Waku/Codex, only the data layer changes.

```js
{
  id: String,
  what: String,              // what was exited
  why: String,               // short reason
  alternative: String,       // what replaced it (or null)
  alternativeUrl: String,    // link to alternative (or null)
  category: String,          // digital | financial | relational | institutional | substance
  date: String,              // "YYYY-MM" format
  exitCount: Number,         // how many others exited this
  almostOut: Boolean,        // soft pre-exit state
  privacy: String,           // public | community | private
  authorId: String,
  authorHandle: String,
}
```

## Migration path to decentralised stack
The modular utils layer is the swap point — nothing above it changes.

| Layer | Phase 1 (now) | Phase 4 |
|---|---|---|
| Storage | localStorage via utils/storage.js | Codex node |
| Messaging | — | Waku pub/sub |
| Identity | random local ID | Status DID / wallet sign-in |
| Hosting | GitHub Pages | Decentralised |
| Notifications | Web push / PWA | Waku |

## Android path
- Phase 1 — PWA, installable on Android, web push notifications
- Phase 2 — WebView wrapper, same JS files inside native container
- Phase 3 — F-Droid listing (critical for cypherpunk credibility)
- Phase 4 — Native notification layer, Android Keystore identity

## Claude Code setup

### Agent pattern
- **builder agent** — writes code, reads spec first, one file at a time
- **verifier agent** — read-only, checks against spec, never writes
- Always separate sessions — verifier must have fresh context

### Permission mode
```bash
claude --enable-auto-mode
# Shift+Tab inside session to cycle to auto
```

### Auto mode boundaries (.claudeignore)
```
.env
.env.*
**/*.pem
**/*.key
**/secrets/**
~/.ssh
.git/config
```

### Discipline
Spec → builder session → verifier session → commit. Never skip the spec.

### Key Claude Code practices
- /compact at 50% context usage — never let it fill
- /clear when switching tasks
- ultrathink keyword for architectural decisions
- /rewind (Esc Esc) when agent goes off track
- GitHub issues as inter-agent communication

## Alternatives considered and rejected

| Option | Reason rejected |
|---|---|
| React + Vite | Build step gap, agents break across boundaries |
| Flutter | Full rewrite to adopt, Dart less agent-trained |
| Svelte | Still has build step, smaller corpus |

## Code style
- ES modules: import/export
- 2 space indent
- Semicolons — use them
- Descriptive names: renderExitCard not render
- Comments only when behaviour is non-obvious
- No inline styles — CSS classes only
- No data fetching inside components
