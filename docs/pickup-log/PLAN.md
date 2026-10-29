# Pickup log reader: plan

Read the game's pickup log (bottom right: `You received EXP (+22)`, `Bonus EXP for PARTY (+7)`,
`You have gained mesos (+10)`, `Stirge Wing x1 earned. (Etc)`) with the reader v2 approach (draw the game's own
font, compare pixels), fast enough for a busy party, and light on the CPU.

What it would give players once it is trusted: mesos/hr without the inventory open, a loot tracker (items per
hour), kills, and a check on the EXP reader. It is built in tickets (`TICKETS.md`) and runs in shadow mode first.

## What "100%" means here

1. **Every line it reports is right: 100%.** Anything doubtful is left out and counted as unread, never guessed
   (the project's fail-closed rule).
2. **Every line the game shows is counted exactly once: 100%**, as long as the line was on screen, not covered, for
   at least one look.
3. **What no reader can see is flagged, never silently missed:** lines pushed out by a big multi-kill burst before
   they are drawn long enough to see, lines covered for their whole life (a sprite, a window, this overlay). Each
   such moment is a *gap* with a time.
4. **Checked against truth all the time:** EXP from the log against the EXP bar (exact), mesos from the log against
   the inventory when it is open. In shadow mode these comparisons are the proof.

## What the recordings show

Mac, 1920 x 1080 game, 6-person party, Kerning City Subway, 30 s each at 10 looks a second (private repo
`joosphotos/maple-captures`: `log-20261029-130655` Default UI, `log-20261029-131006` Ideal UI). Numbers from
`tools/pickup_probe.py` (rough: it finds text by its shadow and is fooled by the scene now and then).

| Fact | Measured | Means |
|---|---|---|
| Place | Right-aligned to the window's right edge (about 8 px in), just above the quick-slot bar; newest line at the bottom | Read lines from their right end, like `mesos_v2` |
| Font | A pixel font with a 1 px dark shadow; crisp at Ideal 1x, bilinearly smoothed at Default (scale 1080/768) | The v2 glyph engine fits it (as for the EXP bar) |
| Colours | White and yellow (meaning not known yet) | The font asset needs several fills |
| Grid | Lines sit on a fixed grid (14 px at 1x) and jump up by one line when one arrives; no sliding | Compare whole lines between looks |
| Fade | Starts the moment a line shows, steady: strength about 250, about -120 a second; readable about 1.0 s (90% within 1.4 s) | **A line's strength tells its age**: tells identical lines apart; read new lines at full strength |
| Lines at once | **6 at most** (PL-02: with 10 lines arriving in 1.4 s still 6 are drawn; the probe's "7" was scenery) | A 7th arrival drops the oldest at once, even while it fades: a burst of 7+ between two looks loses lines (a gap) |
| Rate | 2.7 new lines a second; busiest second 7; busiest look 3 (a kill gives 2 lines at once: EXP + party bonus) | Bursts decide how often to look |
| Speed-up test | Same data played 2x / 3x faster at 10 looks a second: busiest look 4 / 5 lines | 10 looks a second holds 3x with little room: look 20 a second when busy |
| Quiet looks | 74% of looks had nothing new | Most looks cost almost nothing |
| Capture on the Mac | 100 ms steady, one 200 ms hiccup per 30 s | Hiccups happen: time every look |

The real speed limit is the game: if one skill kills 6 mobs at once (12+ lines in the same instant), only the
newest ~7 are ever drawn. The reader can't count the rest; it flags the gap, and EXP stays exact from the bar.

## Design

```
game window ──(own thread, own mss, 10-20 looks/s, only the log's box)──> picture of the log
   pickup_find  : where the log is (Anchor)            once, then only when the window or UI size changes
   pickup_stack : how far the stack moved since the     every look, cheap (~0.3 ms): new lines, gaps
                  last look (StackLook)
   pickup_read  : what each new line says (Line)        only new lines (~3-9 a second), at full strength
   pickup_live  : the thread, timing, counts, checks    shadow mode: counts only, changes nothing shown
                  against the EXP bar and inventory
```

Shared shapes and the measured numbers are in `pickup_types.py` (Anchor, Line, StackLook, Event). Every part is a
pure module (picture in, answer out) except `pickup_live`, so it can be tested anywhere, including Linux.

- **Find (`pickup_find.py`).** Expected place from the window size and UI mode (`ui_layout`), confirmed from the
  lines themselves (right-aligned rows on the pitch). Remembered; looked for again when the window or UI size
  changes or lines stop lining up. Nothing about the Mac title bar or the bar layout is assumed: measured.
- **Stack (`pickup_stack.py`).** The feature that survives fading and any scene behind it: *each pixel minus its
  shadow pixel* (one down and right). On a line that is `alpha x (fill - shadow)`, the same shape whatever the
  background, only scaled by the fade. Each look: find the shift s (0..lines shown) that maps the last look's lines
  onto this look's, with two checks: new lines are at full strength, old lines faded by what the time between the
  looks says. That makes runs of identical lines (`mesos (+9)` three times) unambiguous. A shift as big as the
  lines shown, nothing lining up, or looks too far apart = a gap.
- **Read (`pickup_read.py`).** Grammar first: the fixed phrases are matched whole (`You received EXP (+`,
  `Bonus EXP for PARTY (+`, `You have gained mesos (+`, `earned. (`), then the number digit by digit (commas
  allowed), or for items the name, `xN` and the tab, the name snapped to the game's item list (`assets/items.txt`,
  like map names). A line covered or doubtful at its first look is read again at the next looks while it is still
  strong (about 0.5 s); one that never reads for sure is unread. Matching works on contrast, not exact colours
  (like `mesos_v2`), so a line already fading a little still reads.
- **Live (`pickup_live.py`).** Its own thread and mss (mss is not shared between threads). 10 looks a second
  while tracking, 20 after a burst of 3+, none while paused or with no lines for a while. The overlay's own window
  is blacked out of the picture as everywhere else, and a warning says when it covers the log. Every look is timed;
  one too late to be sure (the stack could have moved by more than it holds) is a gap. A CPU guard like
  `shadow.py`'s. Shadow mode: counts lines by kind, unread, gaps, most lines at once, look timing, and how log EXP
  and mesos compare with the EXP bar and the inventory.

**Compute budget** (per look, at 1x; Default and 2x scale it): grab the log box (about 270 x 110 px) 2-4 ms, stack
check 0.3 ms, about 2 ms per new line read. About 3-6% of one core at the busiest, far less when quiet.

## Testing: how we know it is 100%

- **Truth for the recordings** (ticket PL-02): every line, the look it arrived at, its text. Stored with the
  recordings in the private repo (`truth/`); tests read them from the folder in `MAPLE_CAPTURES` and skip without.
- **Synthetic logs** (PL-05): the real font, drawn with the measured fade onto real backgrounds, at 1x, 3x and 5x
  the measured rate, with bursts up to 14 lines, runs of identical lines, things covering the log, and late looks.
  Every line is known, so the whole reader's precision and recall are exact. This is how 3x is tested without a
  character that can mob. Runs on CI with made-up backgrounds.
- **Gate** (PL-09) before anything goes live in shadow mode: 0 wrong lines anywhere; 100% of lines counted on the
  recordings and on synthetic 1x and 3x (except lines no reader could see, which must all be flagged); timing and
  CPU inside the budget.
- **In the field** (shadow mode, PL-10/11): the EXP check and the counts in the health report (numbers only).

## Still unknown (each owned by a ticket)

| Unknown | Found out by |
|---|---|
| What a big multi-kill burst does (the limit is 6 lines, PL-02) | Windows 30 fps recording, watch sessions (RECORDING.md); live: most lines at once (PL-10) |
| What white and yellow EXP lines mean (own kill vs party's?). PL-02: not the amount, not the party; party bonus is always yellow, mesos and items always white | Solo vs party recording (RECORDING.md) |
| Other kinds of line: quests, a full inventory, fame, event items, mesos spent, numbers with commas, long item names (wrapped? cut?) | Watch sessions, PL-02 catalogue |
| Where the log sits on Windows (no title bar), at Ideal 2x, small windows, the controller bar | Windows recordings, PL-06 |
| Whether sprites and damage numbers are drawn over the log. PL-02: no, they are under the text; name tags are over it | Windows recordings (PL-02b) |
| A game setting that hides pickup lines? | You, in game |
| Capture speed on Windows | Windows 30 fps recording |

## Privacy

The log holds no names or chat: item names and amounts. They stay on the player's PC. Health reports get counts
only (lines read, unread, gaps, timing), never items or amounts. Test frames stay in the private repo; the public
repo gets synthetic tests and only crops the owner approves.
