# CLAUDE.md

This is the user's fork of beanguri's Maple Classic Exp Overlay (remotes: `origin` = joosphotos fork,
`upstream` = beanguri/Maple-Classic-Exp-Overlay).

**Read `docs/CODEBASE.md` first.** It covers how the whole project works: the files, the reading pipeline and
how often each part is read, the trackers, the log and runs, the server, which rules are kept in sync by hand,
and the tests. It replaces re-reading the 6,800-line `maple_exp.py`.

**Pickup log reader (in progress): start with `docs/pickup-log/STATUS.md`** (where things stand, what's next), then `docs/pickup-log/PLAN.md` (design, measured facts), `TICKETS.md` (order,
what blocks what, how a ticket session works) and `tickets/PL-*.md`. Recordings and their truth are in the private
repo `joosphotos/maple-captures`: never commit pictures to this public repo.

Working notes:
- The app runs on Windows and macOS only; `import maple_exp` raises on Linux (`platforms.create_platform`),
  except for the tests: they set `MAPLE_EXP_PLATFORM=headless` (the test-only `platforms/headless.py`).
- **Running the tests in a Linux cloud container** (tried 2026-10-29; the default `python3` is 3.13, which has no
  Tk, so use 3.12):
  ```
  apt-get update && apt-get install -y python3-tk tesseract-ocr xvfb
  python3.12 -m venv --system-site-packages .venv
  .venv/bin/pip install -r requirements.txt
  for t in test_logic test_screen test_health test_v2 test_report test_ocr; do .venv/bin/python tests/$t.py; done
  xvfb-run -a .venv/bin/python tests/test_ui.py
  .venv/bin/python tests/run_pickup_tests.py
  ```
  The venv must use the system Python 3.12 so it sees `python3-tk` (Pillow from apt lacks `ImageTk`; the pip one
  has it). `.venv/` is ignored by git. Without `tesseract-ocr`, `test_ocr.py` still passes but skips what needs
  the program. The site tests (`server/`, Node) were not tried here.
- Tests are plain scripts (`python tests/test_logic.py` etc.), not pytest. They set `MAPLE_EXP_DATA` so nothing
  touches real data or goes online.
- Match the existing style: plain-English comments and names, constants commented in CAPS at the top,
  fail closed.
- Upstream's `.gitignore` lists `CLAUDE.md`, so this file must be added with `git add -f` to commit it.
