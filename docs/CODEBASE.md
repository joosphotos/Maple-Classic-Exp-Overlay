# Codebase notes

How this project is put together, written from a full read of the code at upstream commit `02039db`
(0.9.14-beta). Use it to get back up to speed without re-reading everything. If the code and these notes
disagree, the code is right.

## What it is

Maple Classic Exp Overlay: a Windows/macOS desktop overlay (Python + Tkinter) for MapleStory Classic World.
It only reads the screen (mss screenshots). It never touches the game's memory or files, and never sends input.
It shows EXP/hr, last-5-min EXP/hr, time to the next level, mesos/hr and net mesos/hr (mesos minus potion
cost), and keeps a log per map. Players can share finished 15-minute runs with a stats site (mcwo.app,
`server/`) that ranks maps by class and level. MIT license, sole author beanguri.

- Upstream: `beanguri/Maple-Classic-Exp-Overlay`. Fork: `joosphotos/Maple-Classic-Exp-Overlay`
  (remotes: `origin` = fork, `upstream` = beanguri).
- The data folder is `%APPDATA%\MapleEXP` (macOS: `~/Library/Application Support/MapleEXP`). `MAPLE_EXP_DATA`
  moves it, and while it is set nothing goes online (`sharing_blocked()`) unless `MAPLE_EXP_ALLOW_SHARE=1`.

## Files

| File | What it holds |
|---|---|
| `maple_exp.py` (~6,800 lines) | Almost everything: config, update check and posting, the EXP and mesos readers, `ScreenReader`, `ExpTracker`, `MesoTracker`, `Session`, `AutoLog`, `App` (Tk UI, settings, bug reports), `main()` |
| `capture.py` | `grab()` (mss, clipped to the monitors) and the `Capture` / `ScreenCapture` classes |
| `ocr.py` | `Tesseract`: one subprocess run for many images (`--psm 7`); after a timeout it is left alone for 60 s |
| `platforms/` | `base.Platform` interface, plus `windows.py` (ctypes user32: window finding, DPI, `RegisterHotKey`, mutex) and `macos.py`. Raises on Linux. |
| `ui_main.py`, `ui_gfx.py`, `ui_kit.py` | The custom smooth widgets (drawn 3x, then shrunk), `MainView`, the compact shapes (`square`/`wide`/`bar`), the colours |
| `ui_layout.py` | The game's 1024x768 design area. UI Size "Default" scales by window height/768 (min 1x); "Ideal" scales 1x below 1440 px tall, 2x from 1440 |
| `exp_font.py`, `digits_v2.py`, `glyphs.py`, `mesos_v2.py`, `party_v2.py` | Reader v2: redraws the game's bitmap font (`assets/exp_font.json`, `assets/fonts_v2/*.json`) at screen scale and compares pixel by pixel |
| `shadow.py` | Shadow mode: v2 runs beside today's reader and only counts agree/disagree. It never changes a reading. A CPU guard runs it every other look, or turns it off for the session if it is too costly. |
| `level_ocr.py` | The LV badge reader (font-drawn), plus `name_print` / `name_match` (a picture of the name row, memory only, never read as text) |
| `potion_bar.py`, `potions.py` | Finds the quick-slot bar (keyboard or controller layouts), recognises items by icon fingerprint (`assets/potion_table.json`), `PotionTracker`, `Prices` |
| `healthlog.py` | Daily anonymous health counts (`health.json`), with validation matching `server/src/reports.js` |
| `report.py` | Bug-report text (`summary`, `details`), `scrub()` (strips paths and user names), the body for `/api/report` |
| `build.py` | PyInstaller one-folder build plus bundled Tesseract, zipped into `release/` |
| `tools/` | Asset builders (fonts, potion table, EXP scale fit) |
| `server/` | Cloudflare Pages + D1: `src/index.js` (API), `src/reports.js`, `src/mapnames.js`, `src/maps.js`, `public/` (site: `index.html`, `app.js`), `schema*.sql`, `tools/moderation.sql` |

## The reading pipeline

The `App._worker` thread calls `ScreenReader.read()` every `POLL_SECONDS` = 1.5 s. Each result is a `Reading`
namedtuple, put on a queue. `App._pump` (every 200 ms) hands it to `_handle`. `_refresh` (every 500 ms) redraws
the screen and ticks the session, log, sharing and health.

| Part | How it is read | How often |
|---|---|---|
| EXP bar | `find_exp`: green `[` `]` brackets plus white digits. Each digit is rescaled to 24 px and correlated with `assets/digits.npz` (`MIN_SCORE` 0.75, `MIN_LEAD` 0.03); Tesseract is the fallback. A reading is trusted only if it fits the EXP table (`fits_exp_table`). | Every look (a crop at the known box). After 3 misses: search the bottom 22% strip; the whole window at most every 10 s. |
| %-only bar (about Lv 57+) | `[58.47%]` with no number; found by the "EXP." label's dot. The level comes from the LV badge (`level_ocr`), and EXP is estimated as table × % and shown with ≈. Estimated runs are never shared. Settings > Level fallback lets the player type the level. | Badge: confirmed by 2 looks 1.5 s apart, rechecked every 30 s; failures back off 2/5/30 s |
| Mesos | Solid white box with a gold coin (`find_mesos_fields`), or a see-through one found by its outline (`MesosBoxFinder`, `assets/mesos_box.npz`). Digits are read at fixed positions from the box's right edge; the mesos digit examples are learned on the player's PC (`mesos_digits.npz`), checked by Tesseract until all 10 digits are known. | Box read every look once found. Whole-window scan every 4 s (2 s while there is no box), outline search at most every 8 s. |
| Shop / storage / trade | `find_money_window`: button colour columns | In the window scan; every 1 s while one is open |
| Party size | `find_party_bars`: an evenly spaced column of HP bars | In the 4 s scan; must be seen twice to change |
| Map name | `find_map_box` (light-blue minimap box), then Tesseract voting (`_ocr_votes`), then `snap_map_name` against `assets/maps.txt` (which also marks towns) | A 64x16 picture is compared every look; the text is read only on a change. Retry every 5 s (2 s if hidden); box search every 3 s (1 s if hidden) |
| Class | Tesseract, left of the HP bar; matched to `JOBS` | Every 60 s once read, retry 10 s (5 s if covered) |
| Potions | `potion_bar.read_potions` | Every 3 s; every 9 s with no bar visible |
| Name-row picture | `level_ocr.name_print` | Every 5 s |

- The overlay's own window is blacked out of every shot (`_hide_own`). `_blocked` reports what the overlay is
  covering.
- One part failing never stops the others (`ScreenReader._part` context manager, `PART_NOTES` status lines).

## Tracking logic

- **`ExpTracker`:**
  - `req` (the level's EXP) comes from the table once 2 clean readings point at one level; otherwise it is
    learned from readings that agree.
  - A reading counts only if exp/req matches its %.
  - Jumps over 15% of a level and level-ups must be confirmed.
  - A drop of 1–15% is a death: it is confirmed and not subtracted.
  - 30 misfits in a row re-learns the level.
  - `rate()` = gained / elapsed; `rolling_rate()` covers the last 300 s.
- **`MesoTracker`:**
  - A new amount needs 2 agreeing reads (3 for a big change).
  - First counts, digit-count changes and jumps need the same number 3 times (8 for a 10x change).
  - Changes at money windows are "left out".
  - A big rise is believed after `MESO_GAP` = 120 s with no look.
  - A snap-back (A→B→A) records B as a misread.
  - After pausing, the inventory "banks" what was earned before the pause.
- **`Session`:**
  - Auto-pauses after `gap_seconds` (default 15) without EXP, or on leaving the map.
  - Resumes at the next EXP gain, from zero if the map is different.
  - Pauses after the minimap name has been unseen for 45 s ("blind").

## Log and runs (`AutoLog`, `exp_log.json`, `LOG_VERSION` 4)

- **Log lines:** every 5 minutes (`LOG_BLOCK`) of non-stop gain adds to the day/map/level/party/class line.
  Lines are sealed with an HMAC (`_SEAL_KEY` is in the source, so the seal is a tamper sign, not security);
  greyed out = edited.
- **Runs:** `RUN_SECONDS` = 900 s, ended by `SITE_GAP` = 15 s without EXP.
  - Shared only if there was no money window during the run, the run isn't estimated, the levels are known
    and the seal is good.
  - Mesos are sent only with an inventory look at the start and within 30 s after the end (`END_LOOK`);
    otherwise the run goes with EXP only.
- **Saving:** every change re-reads the file first (`_change`) and writes atomically. A file that can't be
  read right now is never saved over (changes wait in memory, up to 2,000). Daily backups are kept 7 days.
  Notes stay local and are never shared.

## Network (all opt-in except the update check)

- **Update check:** GitHub `releases/latest` at start-up.
- **`POST {STATS_SITE}/api/runs`:** unshared sealed runs; retried every 30 min.
- **`/api/health`:** once a day.
- **`/api/report`:** 3 a day.
- The health ID and the runs' install ID are deliberately different, so the two can't be joined.

## Server (`server/src/index.js`)

- **Endpoints:** `POST /api/runs`; `GET /api/stats` (class, path, level, party), `/api/ladder`,
  `/api/options`, `/api/recent`; `/api/health` and `/api/report` (in `reports.js`).
- **Run checks (`checkRun`):**
  - The job must be a known job; web-address map names are refused; towns are refused.
  - The run must last 890–3720 s.
  - The EXP must be possible for those levels (`expPossible`), under the %/hr caps (`PCT_CAPS`) and
    `MAX_MESOS_HR`.
- **Limits:**
  - Per install: 70 runs/day, 12 maps/day.
  - Per connection: 400 runs/day, 6 installs/day; IPv6 counts by its /64.
  - Site-wide: 300 new installs/day; run caps of 3000/4500/6000 by how much an install has proved.
- **Trust:**
  - New installs count only after 24 h and 4 runs.
  - Per-player medians; runs outside 0.5–2x the median are dropped.
  - A map is ranked once 3 players have farmed it.
  - Level radius of 3, widened to 5.
  - Unlisted map names need 3 players on 2 different days.
- **Caching:** the edge cache (60 s) plus an `answers` table, with daily cache-miss caps.
- **Privacy:** `ip_hash` is a daily HMAC, blanked after 2 days; reports are kept 90 days.

## Kept in sync by hand (change both sides)

- `EXP_TABLE`: `maple_exp.py` and `server/src/index.js`.
- `JOBS` (overlay) and `CLASSES` / `KNOWN_JOBS` (server).
- Map-name cleanup: `_clean_map_name`/`_fix_roman`/`MapList` and `server/src/mapnames.js`; `assets/maps.txt`
  and `server/src/maps.js` (`server/tools/make_maps.py`).
- Health report format: `healthlog.py`, `server/src/reports.js` and `tests/health_contract_v2.json`.

## Tests and CI

- **Runner:** plain scripts with a `check()` helper (not pytest). Each sets `MAPLE_EXP_DATA` to a temp folder.
- **Scripts:** `tests/test_logic.py`, `test_screen.py` (real frames in `tests/frames/`), `test_ui.py`,
  `test_v2.py`, `test_health.py`, `test_ocr.py`, `test_report.py`; upgrade data for every past version in
  `tests/upgrade/`.
- **Server tests:** `server/run_tests.py` and `server/test_*.mjs`.
- **CI:** `.github/workflows/tests.yml` runs everything on Windows (exact hashed packages from
  `requirements-build.txt`) and on macOS. `build.yml` builds on `v*` tags (the tag must match `VERSION`),
  attests the zip and drafts the release.
- **Linux:** `import maple_exp` fails here, because `create_platform()` raises on Linux. Tests weren't tried
  in the cloud container.

## Pickup log reader (in progress)

Planned in `docs/pickup-log/` (PLAN.md, TICKETS.md, tickets/). So far: `pickup_types.py` (the shapes the parts
share, and the measured facts), `tools/capture_log.py` (records the game's bottom right as lossless PNGs; `--watch`
keeps only looks where a new line came in), `tools/pickup_probe.py` (rough measurements of a recording), and
`tests/run_pickup_tests.py` (runs every `tests/test_pickup_*.py`; on CI), `pickup_items.py` (pure: `ItemList`/`snap(text, tab)` puts an item name as read right against `assets/items.txt`, only OCR-style slips and only when one name fits; `assets/items.txt` is made by `tools/make_items.py` from a saved copy of meowdb's `item-db/all` page, 5,151 name+tab lines). Recordings and truth are in the private
repo `joosphotos/maple-captures`.

## Style

Comments and names are plain English, written for players, often with an aside in parentheses. Constants are in
CAPS near the top with a comment on each line. Prefer failing closed ("when in doubt, wait / send EXP only").
Match this when editing.
