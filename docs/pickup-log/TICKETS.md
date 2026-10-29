# Pickup log reader: tickets

The plan is `PLAN.md`. Each ticket below is one session (Sonnet), one branch, one pull request into the fork's
`main`. A ticket file says everything its session needs; the shared shapes are in `pickup_types.py`.

## Order and what blocks what

```
YOU-1 Windows recordings ─────────────────────────┐
                                                   v
PL-01 Cloud test bench ───────────────────────────────────────────────────────────┐
PL-02 Truth + catalogue (Mac) ──> PL-02b (Windows) ──> PL-06 Find ──┐              │
        │                                                 ^         │              v
        └──> PL-04 Font ──┬──> PL-05 Synthetic logs ──> PL-08 Stack ┼──> PL-09 Gate ──> PL-10 Live (shadow)
                          │                                         │                    │
PL-03 Item list ──────────┴──> PL-07 Read ──────────────────────────┘                    v
                                                                     PL-11 Health report + release ──> YOU-2 Trial
```

| Wave | Ticket | Title | Blocked by | Size |
|---|---|---|---|---|
| 1 | YOU-1 | Windows recordings (`RECORDING.md`) | nothing | you, ~1.5 h |
| 1 | PL-01 | Cloud test bench: the overlay's tests on Linux | nothing | S |
| 1 | PL-02 | Truth and message catalogue (Mac recordings) | nothing | M |
| 1 | PL-03 | The game's item list and name matching | nothing | S |
| 2 | PL-04 | The pickup log font | PL-02 | M-L |
| 3 | PL-02b | Truth and catalogue for the Windows recordings | PL-02, YOU-1 | M |
| 3 | PL-05 | Synthetic pickup logs | PL-04 | M |
| 3 | PL-07 | Reading a line | PL-04, PL-03 | L |
| 4 | PL-06 | Finding the log | PL-04, PL-02b | M |
| 4 | PL-08 | Following the stack | PL-05 (and PL-02) | L, the hardest |
| 5 | PL-09 | End-to-end check and the 100% gate | PL-06, PL-07, PL-08 | M |
| 6 | PL-10 | Live, in shadow mode | PL-09, PL-01 | L |
| 7 | PL-11 | Health report, bug report, release | PL-10 | M |
| 8 | YOU-2 | Field trial, then decide what goes live | PL-11 released | you |

- **Critical path:** PL-02 → PL-04 → PL-05 → PL-08 → PL-09 → PL-10 → PL-11. Start PL-02 first.
- **In parallel:** wave 1 all at once; PL-05 and PL-07 together; PL-06 whenever the Windows truth is in.
- PL-08 can start with PL-02's hand-checked anchors and swap in PL-06's finder when it lands; it only needs
  PL-05's synthetic logs for its stress tests.
- After YOU-2: new tickets for what goes live (mesos/hr from the log, a loot tracker, kills), written then.

## How a ticket session works

1. **Start a new session on the fork** (`joosphotos/Maple-Classic-Exp-Overlay`, branch `main`), with:

   > Read CLAUDE.md, docs/CODEBASE.md and docs/pickup-log/PLAN.md, then do ticket
   > docs/pickup-log/tickets/PL-0X.md. Follow its "Done when" exactly; ask me only for owner decisions it names.

2. **Private recordings:** the session attaches `joosphotos/maple-captures` (read only; PL-02/PL-02b need push to
   write `truth/`), clones it and sets `MAPLE_CAPTURES` to that folder. **Never commit a recording, frame or crop to
   the public fork**: only to `maple-captures`.
3. **Tests:** each part adds `tests/test_pickup_<part>.py` (found by `tests/run_pickup_tests.py`, already on CI).
   Tests on recordings skip when `MAPLE_CAPTURES` isn't set; synthetic ones always run.
4. **Results:** before the pull request, the session fills in its ticket's **Results** section: what was built,
   the numbers measured, decisions made, anything the next tickets must know, and changes to `pickup_types.py`
   (and updates every user of it).
5. **Pull request** into the fork's `main`; you merge. Upstream (`beanguri`) gets it when you choose: docs and tools
   any time, the reader once PL-09 passes, the shadow release with PL-11.

## Done when (every ticket, on top of its own list)

- Pure modules (everything but `pickup_live`) import nothing from `maple_exp` and run on Linux.
- Its tests pass (`python tests/run_pickup_tests.py`, plus any existing test file it touched); CI green.
- Style as `CLAUDE.md` says: plain English comments and names, constants in CAPS at the top with a comment each,
  fail closed. `docs/CODEBASE.md` updated for new files.
- No picture in the public repo; Results filled in.
