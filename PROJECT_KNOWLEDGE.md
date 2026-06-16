# PROJECT_KNOWLEDGE — exit.tech

Accumulated project wisdom: pitfalls, patterns, proven gotchas. Distinct from
`CHRONICLE.md` (narrative) and `docs/skills/` (drafting recipes). Append durable
lessons here; raw per-task captures go to `docs/retro-log.md` (if used) and get
reshuffled in.

## CI / deploy

- **Green deploy ≠ live page.** After merging a data change, `deploy.yml` can go
  green while the new page 404s. Always verify the live URL, not the workflow
  status. (verify-before-claiming caught this on PR #18.)
- **deploy.yml / refresh.yml race (issue #20).** Both fire on master pushes and
  share `concurrency: {group: pages, cancel-in-progress: true}`. `deploy.yml`
  only uploads the *committed* `public/` (no build); `refresh.yml` runs
  `build.py` to generate pages — and loses the race, cancelled. New pages
  therefore don't appear until the **weekly** scheduled refresh (Mon 06:20 UTC).
  **Workaround:** after any data merge, `gh workflow run refresh.yml --ref master`,
  poll to `completed/success`, verify the live URL.
- **refresh commits `public/` back to master** as `refresh: live data rebuild`.
  So before your next local push: `git pull --rebase`, and clean regenerable
  working-tree artifacts first — `git checkout -- public/ && git clean -fdq public/`
  — or rebase aborts on untracked `public/exit/*.html`.
- **`gh pr edit` is broken on this repo** (Projects-classic GraphQL deprecation
  error). Use the REST API instead: `gh api -X PATCH repos/xAlisher/exit-tech/pulls/<N> -f title=... -F body=@file`.

## Drafting pipeline

- **The research pack cannot discover alternatives (issue #19).** It matches each
  source by the dependency's own *name*, but the alternatives-catalogs
  (awesome-privacy / awesome-selfhosted / web3privacy) never contain that name —
  empty by construction, not flaky sources. An empty pack means "do the manual
  recheck", not "no alternatives exist". See `docs/skills/drafting-exits.md` step 2.
- **`build.py` crashed on a non-string `prompt:` item** (a dict) with a raw
  traceback instead of a validation error, starving `draft_local.py`'s retry loop.
  Fixed: `validate_exit` now rejects non-string prompt entries, so the model gets
  a clean signal and self-corrects.
- **A bare catalog listing is the weakest backing.** awesome-selfhosted is an
  inclusion list, not an endorsement. Don't stand up a dedicated route on one
  alone — require an editorial recommender (Privacy Guides, switching.software,
  awesome-privacy). See local-voice rule 9.
- **`privacy-guides` is wired in `sources.yaml` but never queried** by
  `research_exit.py` — check it by hand (privacyguides.org categories).

---

## Retro log

### 2026-06-16 — google-docs page + pipeline hardening

**Wins**
- [process] *verify-before-claiming* caught a silent prod failure: deploy went
  green on PR #18, but checking the live URL (not the workflow) surfaced a 404 →
  traced to the deploy/refresh race. Claiming "deployed" on green CI would have
  shipped a broken link.
- [process] *investigate-then-file* held: two structural problems (#19 research
  gap, #20 deploy race) were filed with root-cause + proposed fixes and handed
  back, not patched mid-task.
- [project] `build.py` validation fix turned a 3-attempt pipeline failure into a
  1-retry self-correct.
- [project] Manual source recheck recovered 7 source-backed alternatives the
  pack returned as empty — promoted the page from stub to curated routes.

**Fails**
- [project] **Mis-diagnosed the empty research pack as "flaky sources."** Wrong
  hypothesis; corrected only after reading `research_exit.py`. Root cause: the
  name-substring match against alternatives-catalogs returns empty by design (#19).
- [project] **Shipped a 404.** Merged PR #18, deploy green, page absent. Root
  cause: deploy/refresh concurrency race; deploy (no build) cancelled refresh
  (the builder). Filed #20 + manual-refresh workaround.
- [project] **Added "Docs (La Suite)" as a route on a single catalog listing.**
  Wrong action: treated an awesome-selfhosted listing as enough to stand up a
  dedicated route. Root cause: didn't apply local-voice rule 9 ("listing ≠ good
  advice") at route-creation time. User caught it ("who recommends them?");
  Privacy Guides confirmed no endorsement; removed, CryptPad strengthened.
- [process] **Push friction after the bot's refresh commit.** Push rejected,
  rebase aborted twice on untracked `public/` artifacts. Root cause: didn't
  anticipate refresh.yml commits `public/` back to master. Now documented above.
