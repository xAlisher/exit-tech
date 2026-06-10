# Drafting an exit page

Protocol for turning an `exit-request` issue into `data/exits/<id>.yaml`.
Used by the draft workflow (CI) and by local Claude Code sessions alike.

## Pipeline

1. **Research**: `python3 .github/scripts/research_exit.py --issue <N>` (or `<term>`).
   The pack tells you which enrichment keys are real and which sources list
   alternatives. Read `data/exits/_template.yaml` for the schema and 2–3
   existing exits for voice (`whatsapp.yaml` full, `smoking.yaml` sensitive
   stub, `spotify.yaml` enriched stub).
2. **Draft** `data/exits/<id>.yaml`.
3. **Validate**: `python3 build.py --offline` must pass.
4. **PR**: branch `draft/<id>`, commit only the data file, body `Closes #<N>`.
   Never commit `public/` in a draft PR — master rebuilds automatically.

## House rules (the taste part)

- **Tagline**: one sharp line, dry not snarky. It states the dependency's
  cost, not an insult. ("Renting access to music you'll never own.")
- **Truth over coverage**: only set `enrich` keys the research pack confirmed.
  Only claim `recommended_by` for sources that actually list that alternative
  — credits are load-bearing, validation rejects unknown ids.
- **Stub honestly**: no curated routes you'd vouch for → `stub: true` with a
  genuinely useful agent prompt beats invented alternatives.
- **The prompt is the product**: write it as instructions TO the user's agent
  (ask before recommending, one step at a time, export data first). Include
  the human parts — telling friends, the habit gap, the relapse plan.
- **Sensitive topics** (relationships, substances, safety, regimes): the
  prompt must tell the agent to defer to professional/emergency help and
  never play expert. Reflective questions, not directives. See
  `toxic-relationship.yaml` for the register.
- **Category honesty**: digital | physical | food | financial | relational |
  institutional | substance | behavioral — pick what the dependency *is*,
  not where its app lives.
- **Found gaps?** If research shows a source we don't aggregate yet, note it
  in the PR body — don't wedge it into this PR.
