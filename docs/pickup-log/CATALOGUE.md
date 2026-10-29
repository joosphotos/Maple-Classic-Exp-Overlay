# Pickup log: catalogue of what the game writes

What the pickup log (bottom right of the game) shows, from the truth read off the recordings. Every line of both Mac
recordings was transcribed by eye and checked (`tools/pickup_label.py`, `PL-02`). Add to this file, never rewrite it
(PL-02b adds the Windows recordings). Truth files and pictures stay in the private repo `joosphotos/maple-captures`
(`truth/`); only words and numbers are here.

## Recordings (Mac, 1920 x 1080 game, Lv 37 Bandit, 6-person party, Kerning City Subway, 30 s, 299 looks each)

| | `log-20261029-131006` | `log-20261029-130655` |
|---|---|---|
| UI Size | Ideal (1x, crisp font) | Default (x1.406 = 1080/768, smoothed font) |
| Lines in the truth | 96 (6 already on screen at look 0, 90 arrived) | 88 (3 already on screen, 2 of them unreadable, 85 arrived) |
| Looks with arrivals | 58: 27 with 1 line, 30 with 2, 1 with 3 | 52: 22 with 1 line, 28 with 2, 1 with 3, 1 with 4 |
| New lines a second | 3.0 | 2.8 |
| Most new lines at one look | 3 (look 277) | 4 (look 233) |
| Looks hidden by another window | 64-73 (a white Terminal window) | 259-261 and 272-279 (the same); 247-253: the game window was dragged, see Odd things |
| Right end of the text, game-window x | 1914 (last text pixel 1912, shadow 1913) | 1911 (last text pixel 1909) |
| Under the newest line, game-window y | 958 (baseline row 954, descenders to 956) | 897 (baseline row 892) |
| Line pitch | 14 | 19.69 (baselines 892, 872, 852, 833: 14 x 1080/768, rounded) |

Game-window pixels = frame pixels + `(1056, 499)` in both (`frames.json` box minus game rect). The Mac window is 1920 x
1108 and includes a 28 px title bar: take 28 off y for the 1080 game area (bottom 930 and 869). Text is right-aligned:
the last text pixel is on one column in every look (Ideal x 1912); the left end depends on the line (widest Ideal line
`You have gained mesos (+26)` is 160 px wide, `Stiff Feather x1 earned. (Etc)` 152 px).

## Kinds of line (exact wording as drawn)

| Kind | Wording | Colour | Seen |
|---|---|---|---|
| EXP | `You received EXP (+N)` | yellow or white, see below | N = 5, 6, 8, 9, 10, 12, 13, 16, 18, 19, 22, 24 |
| Party bonus | `Bonus EXP for PARTY (+N)` | always yellow | N = 2, 3, 4, 5, 6, 7 |
| Mesos | `You have gained mesos (+N)` | always white | N = 5, 6, 8, 9, 10, 15, 16, 18, 19, 23, 25, 26 |
| Item | `<name> x<qty> earned. (<tab>)` | always white | `Tablecloth`, `Stirge Wing`, `Stiff Feather`, `Halloween Can...`; qty 1; tab `Etc` |

- Numbers have a `+` and sit in parentheses. No comma was seen (the biggest amount is 26): numbers with commas are
  still unknown.
- Every EXP line is followed, in the same look, by its Party bonus line (Default: 31 of 31, Ideal: 29 of 29; look 0
  is left out). EXP is on top, the bonus under it. Mesos and item lines come in any order next to them (look 206
  Default: item, EXP, bonus; look 277 Ideal: mesos, EXP, bonus).
- **The bar adds up exactly.** Sum of all EXP and Party bonus lines that arrived (lines already on screen at look 0
  excluded, `game_start.png` already counts them): Ideal 256 + 80 = 336 = 158,013 - 157,677; Default 351 + 104 = 455 =
  155,495 - 155,040. So `You received EXP` and `Bonus EXP for PARTY` are separate EXP and together all of it.
- Pairs seen (EXP / bonus, EXP colour): 5/2 y, 6/2 y, 8/2 y (27 times), **8/3 y (once)**, 10/3 y, 9/3 w, 12/4 w, 13/4 w,
  16/6 w, 18/5 y, 19/7 y, 22/7 w, 24/7 w. The bonus is about a third of the EXP, rounded unevenly.
- A long item name is cut with `...` and the rest of the line stays: `Halloween Can... x1 earned. (Etc)` (the event item
  Halloween Candies). `Stiff Feather` (13 letters) is not cut; the rule (letters or width) is unknown.

## White or yellow?

- Always one colour: Party bonus yellow; mesos and items white.
- EXP lines: **yellow** for 5, 6, 8, 10, 18, 19 (Ideal 26 lines, Default 20); **white** for 9, 12, 13, 16, 22, 24
  (Ideal 5, Default 11). Not a threshold on the amount (18 and 19 are yellow, 9 is white), not the party size (same
  party all along). Meaning: **unknown**. Guess to test: white = the player's own kill, yellow = a party member's kill
  (a killer's share is bigger). `RECORDING.md` #6 (solo then party) decides it; PL-02b/PL-07 must not rely on colour.
- Colour was measured, not just seen: white lines have blue = green = red in the brightest pixels, yellow lines have
  blue about a third of green. The tool's colour names are `white` and `yellow`.

## The stack

- **At most 6 lines are on screen.** With 10 lines arriving in 1.4 s (Ideal look 173, Default look 246) exactly 6 are
  drawn: the oldest is dropped the moment a seventh arrives, even while it is still fading. The probe's "7 seen" was
  scenery. So a burst of more than 6 lines between two looks loses the oldest ones unseen: the plan's "gap".
- New lines are drawn at the bottom and everything moves up one line pitch, in the same look (no sliding).
- **Fade**: a new line is strong at its first look (lowest seen 239 at Ideal, 208 at Default on the Ideal scale; the
  Default font is smoothed, its peaks are 173 raw, 0.69 of Ideal) and loses about 12 to 17 a look (120 to 170 a
  second, not a steady 120: it varies from line to line and with the scene). Readable about 1.0 s, faint at 1.5 s,
  gone at about 2 s. Strength gives a line's age only to about +- 0.2 s; it jumps back up when a new line arrives.
- Identical lines in a row happen constantly (`You have gained mesos (+9)` twice, an EXP/bonus pair twice in a row):
  only the arrival look (strength jump) and the stack height tell them apart. Cases where the strength gave no jump
  (a bright scene lowers it): Default looks 258, 266, 271 (a new `mesos (+9)` under an old one).
- The stack grid is fixed: lines never sit between slots.

## What is drawn over or under the log

- **Under the text** (text stays readable on top): damage numbers (orange digits, Default looks 133-135, 255-256),
  character sprites and their skill effects (blue arc, gold glow: Ideal looks 21-33, Default 1-6).
- **Over the text**: character **name tags** (white text on a dark box: `Brown Puppy`, `Brown Kitty`, `Peruanito`,
  `IXTNI`) hide the part of the line behind them (Default 264, 268-270). They also look like lines to a reader: white
  text, dark shadow.
- Another application's window (macOS Terminal, white) covered the capture region completely at the times above; no
  line arrived in them (the stack before and after matches line for line), but nothing could have been read there.
- Bright scenery in the upper slots looks like a line (strength 150-170 in slot 6 or 7, or a bright edge in a lower
  one): 22 look/slot pairs in Default, 7 in Ideal. Listed in each truth file as `scenery`.

## Odd things

- **The game window moved during the Default recording** (looks 247-253, from x 478 to 14: `frames.json` "game" changes
  eight times). The capture box lagged behind, so in look 248 the whole log sits 73 px left of its place and a few
  pixels up, and a white Terminal window fills the right of the frame. A finder must handle a log that moves with its
  window, and a look whose box is out of date.
- A look is occasionally 0.2 s after the one before (one per recording); 0.1 s otherwise.
- Look 0 of the Default recording starts with two almost faded lines (`You received EXP (+?)`, `Bonus EXP for PARTY (+?)`)
  whose last digit is under a bright part of the scene: truth text is `null`.
- Lines at look 0 arrived before the recording: 6 in Ideal (`Bonus EXP for PARTY (+2)`, `You received EXP (+8)`, `Bonus
  EXP for PARTY (+2)`, `You have gained mesos (+9)`, `You received EXP (+18)`, `Bonus EXP for PARTY (+5)`), 3 in Default.

## Still unknown (not in these recordings)

Quest, level-up, death, full-inventory, fame, event and equipment lines; item quantities above 1 and other tabs; mesos
with commas; what hides or reorders lines at more than 6; Windows layout and Ideal 2x (PL-02b and the Windows
recordings).
