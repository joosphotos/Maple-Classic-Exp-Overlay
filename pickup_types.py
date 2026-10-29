"""The pickup log reader's shared shapes and measured facts (docs/pickup-log/PLAN.md).

The pickup log is the stack of lines at the bottom right of the game ("You received EXP (+22)", "Bonus EXP for
PARTY (+7)", "You have gained mesos (+10)", "Stirge Wing x1 earned. (Etc)"). Its reader is built in parts by
separate tickets (docs/pickup-log/TICKETS.md); these are the shapes they hand each other, agreed before any part
was built, so the parts fit. A ticket that needs a change here says so in its Results and changes every user.

Rects and points are in the game window's own pixels (what platform.client_rect covers), like potion_bar's.
Pure: no screen, no files.
"""
from collections import namedtuple

# ---- measured on the Mac recordings of 2026-10-29 (tools/pickup_probe.py); tickets refine these in their Results
PITCH = 14                  # line pitch on the 1024 x 768 design area (UI scale 1): 14 px at Ideal 1x, ~19.7 at Default 1080
MAX_LINES = 6               # the game draws 6 lines at most: a 7th arrival drops the oldest at once, even while it fades (PL-02)
FADE_START = 250            # a new line's strength (fill minus shadow, brightest channel) on a dark scene...
FADE_PER_SECOND = 120       # ...falls 120 to 170 a second (12 to 17 a look, it varies), from the moment it shows (no hold): about 2 s to nothing
READABLE_SECONDS = 1.0      # a line is readable (strength above about 60) for about this long; 90% within 1.4 s
BUSIEST_LOOK = 4            # most new lines between two looks 0.1 s apart (6-person party, Kerning Subway, 30 s each: 3 in Ideal, 4 in Default)
RATE_MEASURED = 3.0         # new lines a second, average, from the hand-made truth (the probe said 2.7); the reader is built for 3x this

KINDS = ("exp", "party", "mesos", "item", "other")
# exp:   "You received EXP (+22)"            amount 22
# party: "Bonus EXP for PARTY (+7)"          amount 7
# mesos: "You have gained mesos (+10)"       amount 10
# item:  "Stirge Wing x1 earned. (Etc)"      item "Stirge Wing", qty 1, tab "Etc" (a long name is cut: "Halloween Can... x1 earned. (Etc)")
# other: a line the reader read but that fits none of these (kept so the stack still lines up); text says what

Anchor = namedtuple("Anchor", "right bottom pitch scale")
# Where the log is (pickup_find): right = the x just past the lines' right end, bottom = the y just under the newest
# line, pitch = the line pitch on screen (PITCH x scale), scale = the UI scale it was drawn at (ui_layout).

Line = namedtuple("Line", "kind text colour amount item qty tab")
# One line read for sure (pickup_read). kind: one of KINDS; text: the whole line as read; colour: the fill colour's
# name in the font asset ("white", "yellow", ...); amount: int for exp/party/mesos, else None; item, qty, tab: for
# item lines (item snapped to the item list when it matched one), else None.

StackLook = namedtuple("StackLook", "t new gap rows strengths")
# What one look at the log found (pickup_stack). t: the look's time (seconds, time.perf_counter);
# new: how many lines arrived since the last look (None when that can't be told: then gap is True);
# gap: True when lines may have been lost before this look (the stack moved as far as it holds, nothing lined up,
#      or the looks were too far apart); rows: the screen rows (y of each line's top, newest last) of the lines in
#      the picture; strengths: each of those lines' strength (fade), same order.

Event = namedtuple("Event", "t line row")
# One new line, as the live reader reports it (pickup_live). t: when it arrived (the look it was first seen at);
# line: a Line, or None when it never read for sure (covered, faded, unknown font): counted as unread, never guessed;
# row: its index in StackLook.rows at that look.
