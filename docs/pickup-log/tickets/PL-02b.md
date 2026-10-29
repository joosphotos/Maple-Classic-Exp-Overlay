# PL-02b Truth and catalogue for the Windows recordings

**Blocked by:** PL-02 (its tool and format), YOU-1 (the recordings). **Blocks:** PL-06; feeds PL-04 (more glyphs,
colours) and PL-07 (more kinds of line). **Size:** M.

## Do
Exactly PL-02's steps for every new recording in `maple-captures/captures/` (names in `captures/NOTES.md`; what
each answers is in `docs/pickup-log/RECORDING.md`), and add to `CATALOGUE.md`:
- Windows: where the log is with no title bar; Default smoothing at that size; Ideal 1x and 2x; the small window;
  the controller bar (does the log move?).
- `win-solo-party`: what white vs yellow means.
- `win-fast` (30 looks a second, the busiest spot): bursts, the most lines at once, capture timing on Windows
  (`frames.json` times), whether the fade gets faster when busy.
- `win-watch`: every new kind of line (quests, full inventory, fame, mesos spent, event items, long names, commas),
  each with a cut-out sheet in `truth/work/` and the exact wording in the catalogue. Watch frames are not every
  look, so record lines and kinds, not arrival looks.
- Update `pickup_types.py`'s measured numbers if they changed (and say so in Results).
- If PL-04 is already merged: re-run its font builder with the new truth so new glyphs and colours are in the font
  (or list what's missing for PL-04 if it isn't). If PL-07 is merged and there are new kinds of line: add them to
  its grammar and tests, or write a follow-up ticket if it is more than a few lines.

## Done when
Every new recording has a validated truth file (watch: a catalogue list instead); `CATALOGUE.md` answers each
question from RECORDING.md or says what is still unknown; Results filled in.

## Results
(filled in by the session)
