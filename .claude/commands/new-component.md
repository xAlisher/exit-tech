Build a new component for exit.tech.

Steps:
1. Read CLAUDE.md
2. Read specs/$ARGUMENTS.md
3. Use builder agent to create src/components/$ARGUMENTS.js
4. Use verifier agent to verify against specs/$ARGUMENTS.md
5. Report final verdict

If verifier returns FAIL, fix issues and re-verify until PASS.
