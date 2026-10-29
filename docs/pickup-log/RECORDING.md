# Recordings to make (at home, on Windows)

These answer what the Mac recordings can't (PLAN.md, "Still unknown"). Each takes a few minutes. Anything you can't
do (no 1440p screen, no controller), skip and note it.

## Once: get the code

Everything is on the fork's `main` already:

```bash
git clone https://github.com/joosphotos/Maple-Classic-Exp-Overlay.git
cd Maple-Classic-Exp-Overlay
```

(If you cloned it before, `git pull` instead.) Then a Python for the recorder:

```bash
py -3 -m venv .venv
.venv\Scripts\python -m pip install mss numpy opencv-python-headless
```

## Before each recording

- Move the overlay's window away from the bottom right (or close it).
- Nothing over the bottom right of the game (inventory, party list, Quest Helper...).
- Write one line per recording in `captures\NOTES.md`: its folder name, the UI size, screen and window size, what
  was happening (solo/party, map, what you did when).

## The recordings

| # | Name (`--name`) | Set up | Command | Answers |
|---|---|---|---|---|
| 1 | `win-default` | UI Size Default, your normal window, party grinding | `.venv\Scripts\python tools\capture_log.py --name win-default` | Windows layout (no title bar), Default smoothing |
| 2 | `win-ideal` | UI Size Ideal, same window | `... --name win-ideal` | Ideal 1x on Windows |
| 3 | `win-ideal-2x` | Ideal, window at least 1440 px tall (1440p+ screen) | `... --name win-ideal-2x` | Ideal 2x (blocks copied, bigger font) |
| 4 | `win-small` | Default, a small window (1280 x 720 or the smallest) | `... --name win-small` | Small scale, log position |
| 5 | `win-controller` | Controller quick-slot layout (Standard or Cross-Style), Default | `... --name win-controller` | Does the log move with the bar? |
| 6 | `win-solo-party` | Default. First 15 s: kill alone (party members away or not attacking). Then 15 s: party kills | `... --name win-solo-party` | What white vs yellow lines mean |
| 7 | `win-fast` | Default, the busiest spot you can find | `... --part log --fps 30 --name win-fast` | Capture speed on Windows, bursts |
| 8 | `win-watch` | Play normally for up to an hour (see below) | `... --watch --seconds 3600 --name win-watch` | Rare lines: the catalogue |

Each normal recording is 30 s, 10 looks a second, about 250 MB. The watch keeps only the pictures where a new line
came in (about 1 in 4 looks while fighting) plus the whole window every 10 minutes.

### During the watch, try to cause each of these once (note the time in NOTES.md)

- Finish a quest that gives EXP or mesos, and one that gives an item.
- Pick up a quest item, an event item, a potion, an equip, a scroll (each tab: Equip, Use, Etc, Set-up, Cash).
- Pick up several of one item at once (x2 or more) and a big pile of mesos (4+ digits, a comma?).
- An item with a long name.
- A full inventory tab, then try to pick something up.
- Buy and sell at a shop, drop mesos, use a teleport rock or anything that might print a line.
- Die once (EXP loss line?).
- Level up.
- Anything that adds a bonus line (event EXP, a ring, a buff).
- Pick up a Set-up item and a Cash item: does the line say `(Set-up)` or `(Setup)`, and `(Cash)`? (PL-03 assumed
  `Set-up` and `Cash`.) Do item names ever carry a note like `(Lv 10)`? Write the answers in NOTES.md.

And check in Settings: is there an option that hides pickup messages? (Note what it's called.)

## Upload (to the private repo only)

Your fork is public: never push recordings there. They go to `joosphotos/maple-captures` (private):

```bash
git clone https://github.com/joosphotos/maple-captures.git %USERPROFILE%\maple-captures
robocopy captures %USERPROFILE%\maple-captures\captures /E
cd %USERPROFILE%\maple-captures
git add .
git commit -m "Windows recordings"
git push
```

If git refuses the push, use GitHub's own sign-in: `winget install GitHub.cli`, then `gh auth login` and
`gh auth setup-git`, and push again.
