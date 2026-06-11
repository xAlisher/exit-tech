# Halt — 2026-06-11 (post-midnight, end of build-day 1)

## Where we stopped

exit.tech went from holding page to live product in one session: 14 exit pages
on https://exit.tech, full content pipeline operational. Last act: contribute
block (page-feedback issues) added to every exit page + spacing fix, deployed.
Nothing in progress — clean break point.

## Current state

- Branch: master, clean tree, synced with origin
- Last commit: 00eb0a7 "exit pages: breathing room above contribute button"
- Build status: passing (deploy green, site verified live)
- Open review: none (PRs #4 netflix, #17 tiktok both merged)

## Next steps (in order)

1. Work the tier-1 queue (issues #5–#16, 10 remaining: x/twitter, amazon,
   gmail, google search, windows, adobe, facebook, youtube, alcohol, gambling,
   fast fashion): `python3 .github/scripts/draft_local.py --issue <N>` →
   Claude reviews → distill into `docs/skills/local-voice.md` (MANDATORY,
   see drafting-exits.md "taste loop") → PR. Sensitive ones (alcohol,
   gambling) per house rules: professional-help register, consider
   hand-drafting.
2. Optional CI drafting: needs `claude setup-token` (interactive, Alisher) →
   `gh secret set CLAUDE_CODE_OAUTH_TOKEN` + repo setting "Allow GitHub
   Actions to create and approve PRs". Until then, local pipeline covers it.
3. Sneg follow-up (separate session): reinstall Ollama 11434 for Anqa
   embeddings — Anqa RAG is down until then (see infra repo retro-log
   2026-06-10).
4. Phase-3 ideas parked: auto-stubs from JDM×ToS;DR intersection (taste-check
   3 examples first), privacy-respecting analytics for query demand.

## Blockers

- None for local pipeline. CI drafting blocked on Alisher's OAuth token (2.).

## Context that's hard to re-derive

- **Taste loop is a protocol, not just code**: after every review of a local
  draft, diff `.review/<slug>.draft.yaml` vs merged file and distill rules
  into `docs/skills/local-voice.md` (10 rules so far, each cites its review).
  Skipping this wastes the review.
- **qwen3.6-27b failure mode**: unquoted YAML strings containing ": " —
  prompt + retry message already handle it; if drafts fail 3×, check
  `.review/<slug>.failed-N.txt`.
- **llama-server thinking control changed** with the 2026-06 rebuild:
  `/no_think` is dead; use `chat_template_kwargs: {enable_thinking: false}`;
  thinking lands in `reasoning_content`, not `content`. draft_local.py
  disables thinking.
- **GITHUB_TOKEN pushes don't trigger workflows** — that's why refresh.yml
  deploys itself (don't "simplify" that back out).
- **Issue label streams**: exit-request (new pages, triage dedupes daily into
  ×N weights), page-feedback (contribute buttons, page URL in form), draft
  label = CI drafting trigger (gated, currently skips without token).
- ToS;DR search is flaky: netflix returned no match one day, rating D the
  next. Truth-check handles it, but a "no match" in research isn't proof of
  absence — reviewer may re-check.
- Local model endpoint: http://100.108.127.3:11435/v1 (Tailscale), ~38 tok/s,
  resource-limited so it can't freeze Sneg (CPUQuota 800%, MemoryMax 32G).
