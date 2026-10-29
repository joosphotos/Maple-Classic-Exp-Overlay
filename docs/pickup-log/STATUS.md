# Pickup log reader: where we are (start here)

Last updated 2026-10-29, end of the first day (work Mac). Next: continue at home on Windows, with new sessions.

## The idea in three lines

Read the game's pickup log (bottom right: `You received EXP (+22)`, `Bonus EXP for PARTY (+7)`, `You have gained mesos
(+10)`, `Stirge Wing x1 earned. (Etc)`) with the reader v2 approach (draw the game's own font, compare pixels), at about
10 looks a second, counting every line exactly once and never reporting a wrong one. First in shadow mode (counts only),
then mesos/hr without the inventory open, a loot tracker and kills. Design and measured facts: `PLAN.md`.

## Where things are

| What | Where |
|---|---|
| Code, docs, tickets | `joosphotos/Maple-Classic-Exp-Overlay` (public fork), branch `main` |
| Plan, measured facts, design | `docs/pickup-log/PLAN.md` |
| Every kind of line seen, colours, the 6-line limit, what covers the log | `docs/pickup-log/CATALOGUE.md` |
| Ticket order, what blocks what, how a session works | `docs/pickup-log/TICKETS.md` |
| The tickets (each one's Results says what it found) | `docs/pickup-log/tickets/PL-*.md` |
| A ready prompt for every ticket session | `docs/pickup-log/PROMPTS.md` |
| Windows recordings to make, and how to upload them | `docs/pickup-log/RECORDING.md` |
| Recordings, truth files, contact sheets (private: they can show chat and names) | `joosphotos/maple-captures` (private): `captures/`, `truth/` |
| How the whole overlay works | `docs/CODEBASE.md`; `CLAUDE.md` for working notes (Linux test bench commands) |
| Release | upstream `beanguri/Maple-Classic-Exp-Overlay` (the owner's other account) |

## Done

| Ticket | What it gave |
|---|---|
| Setup (first session) | `tools/capture_log.py` (lossless recorder: `--part log`, `--fps`, `--watch`, `--name`), `tools/pickup_probe.py` (rough measurements), `pickup_types.py` (shared shapes and facts), `tests/run_pickup_tests.py` (on CI), the plan, tickets, prompts. Two Mac recordings (Default and Ideal UI, 30 s, 10 looks a second) in `maple-captures`. |
| PL-01 | The overlay's tests run in a Linux cloud session (`platforms/headless.py`, only with `MAPLE_EXP_PLATFORM=headless`; commands in `CLAUDE.md`). All test files pass there. |
| PL-02 | Hand-checked truth for both Mac recordings (every line, its arrival look, its text) in `maple-captures/truth/`, `tools/pickup_label.py` (propose, sheets, build, validate), `CATALOGUE.md`. **The log's EXP adds up exactly to the EXP bar's change in both recordings.** |
| PL-03 | `assets/items.txt` (5,151 items with their tab, from meowdb's item list; its owner agreed to this use) and `pickup_items.py` (`snap`: puts a read name right against the list, only when one name fits). |

All of it is merged into `main` (the three ticket pull requests were merged together, with one conflict in
`docs/CODEBASE.md` resolved by keeping both sides). On a Linux bench every test passes, including PL-02's truth files
checked against the private recordings.

## What we learned that changes the next tickets (details in CATALOGUE.md and each ticket's Results)

- **The game draws at most 6 lines.** A 7th drops the oldest at once, even while it is still fading. A burst of 7+
  lines between two looks loses lines: that must be a reported gap.
- **Colour doesn't tell kinds apart.** Party bonus is always yellow, mesos and items always white, but EXP lines are
  white or yellow for reasons not known yet (`win-solo-party` recording decides it). Never use colour to decide kind.
- **Character name tags are drawn over the log** and look like a line (white text, dark shadow). Damage numbers,
  sprites and skill effects are under the text.
- **Fade varies:** 12-17 strength a look, so strength says "new or not", not an exact age. A new line was never below
  strength 239 (Ideal) or 208 (Default, on the Ideal scale) at its first look.
- **Identical neighbours in a bright scene** are where counting is hardest (the rough probe missed them).
- **The log moves with the game window** (a drag in the Default recording moved it 73 px for half a second).
- **A long item name is cut with `...`** (`Halloween Can... x1 earned. (Etc)`), so the reader must snap a cut name
  (`pickup_items.snap` has to accept a prefix for that: PL-07).
- Every EXP line comes with its party bonus line in the same look (EXP on top).
- Anchors (Mac window, 28 px title bar): Ideal right 1914, bottom 958, pitch 14; Default right 1911, bottom 897,
  pitch 19.69.

## Next steps, in order

1. **You (Windows, at home): the recordings** in `RECORDING.md` (8 of them, about 1.5 h with the watch session), upload
   to `maple-captures`. Also check three things PL-03 assumed (write them in `captures/NOTES.md`): the game writes the
   tab as `Set-up` (not `Setup`), Cash-shop equips say `(Cash)`, and item names have no `(Lv 10)` style notes.
2. **PL-04 (font)**: can start now, in parallel with the recordings. Prompt in `PROMPTS.md`, wave 2.
3. **PL-02b** (truth for the Windows recordings): once they are uploaded.
4. Then waves 3 to 7 as `TICKETS.md` says: PL-05 and PL-07, then PL-06 and PL-08, PL-09 (the gate, which you
   accept), PL-10 (live in shadow mode), PL-11 (health report, release), then the field trial.

## Things that tripped us up (so they don't again)

- **The fork is public.** Recordings only ever go to `maple-captures`. Never `git add -f captures` in the fork.
- **Pushing from the Mac was refused** ("permission denied") with a token git had saved, even with the right account.
  Fix: GitHub's own sign-in. `winget install GitHub.cli` (Windows) or `brew install gh` (Mac), then `gh auth login`
  and `gh auth setup-git`.
- **A pull request on the fork may default to `beanguri` as its base.** Check the base is `joosphotos/...` `main`.
- **GitHub Actions don't run on the fork** (no checks on the ticket pull requests). Turn them on in the fork's
  Actions tab, or rely on the sessions running the tests (`CLAUDE.md` has the Linux commands).
- **Cloud sessions can only reach allowed domains.** PL-03 needed `meowdb.com` added under the environment's
  Network access, Allowed domains. Later tickets need no outside site.
- **A ticket session must be told to merge nothing and push only its branch**; you merge the pull requests. When two
  run at once they may both edit `docs/CODEBASE.md`: expect a small conflict, keep both sides.

## Starting a new session at home

New session on `joosphotos/Maple-Classic-Exp-Overlay`, branch `main`:

> Read docs/pickup-log/STATUS.md, then CLAUDE.md and docs/CODEBASE.md, then docs/pickup-log/PLAN.md and
> TICKETS.md. Tell me in a few lines where the project stands and what's next, then wait.

For a ticket, use its prompt from `PROMPTS.md` instead (they read everything they need).
