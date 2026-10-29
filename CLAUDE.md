# CLAUDE.md

This is the user's fork of beanguri's Maple Classic Exp Overlay (remotes: `origin` = joosphotos fork,
`upstream` = beanguri/Maple-Classic-Exp-Overlay).

**Read `docs/CODEBASE.md` first.** It covers how the whole project works: the files, the reading pipeline and
how often each part is read, the trackers, the log and runs, the server, which rules are kept in sync by hand,
and the tests. It replaces re-reading the 6,800-line `maple_exp.py`.

**Pickup log reader (in progress):** `docs/pickup-log/PLAN.md` (design, measured facts), `TICKETS.md` (order,
what blocks what, how a ticket session works) and `tickets/PL-*.md`. Recordings and their truth are in the private
repo `joosphotos/maple-captures`: never commit pictures to this public repo.

Working notes:
- The app runs on Windows and macOS only; `import maple_exp` raises on Linux (`platforms.create_platform`).
- Tests are plain scripts (`python tests/test_logic.py` etc.), not pytest. They set `MAPLE_EXP_DATA` so nothing
  touches real data or goes online.
- Match the existing style: plain-English comments and names, constants commented in CAPS at the top,
  fail closed.
- Upstream's `.gitignore` lists `CLAUDE.md`, so this file must be added with `git add -f` to commit it.
