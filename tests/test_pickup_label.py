"""Tests for tools/pickup_label.py: the labelling tool for the pickup log recordings (docs/pickup-log/tickets/PL-02.md).

Run from the project folder:  py -3 tests/test_pickup_label.py   (no screen needed; made-up pictures and a made-up truth
file, nothing from the private recordings). When MAPLE_CAPTURES points at the private repo, the real truth files are
checked too.
"""
import copy
import json
import os
import re
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import pickup_label as L  # noqa: E402

failures = 0


def check(name, ok):
    global failures
    print(("PASS " if ok else "FAIL ") + name)
    failures += not ok


# ---- a made-up recording: a stack of lines drawn as bright text with a dark shadow, fading like the game's

GRID = dict(ui="ideal", bottom=459.0, pitch=14.0, right=858, scale=1.0, start=250)
LOOKS = 30
FADE_PER_LOOK = 12                                      # strength lost a look (0.1 s)
ARRIVALS = {2: 1, 5: 2, 6: 1}                           # look -> new lines (a bit of everything, one of them in a pair)


def draw_line(img, slot, strength, seed):
    """One line in a slot: bright squiggles (a different pattern per line) with their shadow one pixel down and right."""
    y0, y1 = L.slot_rows(GRID, slot)
    rng = np.random.RandomState(seed)
    for x in range(GRID["right"] - 150, GRID["right"] - 6, 3):
        h = int(rng.randint(4, 9))
        top = y1 - 3 - h
        cv2.rectangle(img, (x + 1, top + 1), (x + 1, y1 - 3 + 1), (0, 0, 0), -1)       # shadow
        cv2.rectangle(img, (x, top), (x, y1 - 3), (strength, strength, strength), -1)  # fill


def make_recording(folder):
    """Writes frames.json and the frames; returns the truth lines (id order) that match them."""
    stack, lines, frames = [], [], []                   # stack: (id, arrival look), oldest first
    for look in range(LOOKS):
        for _ in range(ARRIVALS.get(look, 0)):
            lines.append({"id": len(lines), "look": look, "text": f"You received EXP (+{len(lines) + 1})",
                          "colour": "yellow", "note": ""})
            stack.append(len(lines) - 1)
        img = np.full((609, 864, 3), 40, np.uint8)
        for slot, line_id in enumerate(reversed(stack[-6:])):
            age = look - lines[line_id]["look"]
            strength = 250 - FADE_PER_LOOK * age
            if strength > 70:
                draw_line(img, slot, strength, line_id)
        cv2.imwrite(str(folder / f"frame_{look:05d}.png"), img)
        frames.append({"file": f"frame_{look:05d}.png", "t": look * 0.1, "game": [14, 25, 1920, 1108],
                       "box": [1070, 524, 864, 609]})
    (folder / "frames.json").write_text(json.dumps({"fps": 10, "frames": frames}), encoding="utf-8")
    return lines


def good_truth(lines):
    return {"recording": "synthetic", "ui": "ideal", "scale": 1.0, "anchor": {"right": 1914, "bottom": 958, "pitch": 14},
            "exp_bar": {"start": 100, "end": 110}, "lines": copy.deepcopy(lines)}


def problems_of(truth, folder):
    looks = L.read_recording(folder, GRID)
    return L.check_truth(truth, looks, [f["t"] for f in L.load_frames(folder)])


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    rec = tmp / "captures" / "synthetic"
    rec.mkdir(parents=True)
    lines = make_recording(rec)

    # the proposer follows the stack
    props = L.propose(rec, GRID)
    found = {p["look"]: p["new"] for p in props if p["new"] and p["look"]}
    check("proposer finds each arrival and how many lines came", found == ARRIVALS)
    check("proposer: nothing new on a quiet look", props[3]["new"] == 0 and props[4]["new"] == 0)

    # a truth file that matches the frames is consistent
    truth = good_truth(lines)
    check("a matching truth file has no problems", problems_of(truth, rec) == [])

    # each kind of mistake is found
    t = good_truth(lines)
    t["lines"][1]["id"] = 5
    check("ids out of order are found", any("ids must run" in p for p in problems_of(t, rec)))
    t = good_truth(lines)
    t["lines"][0]["colour"] = "pink"
    check("an unknown colour is found", any("colour" in p for p in problems_of(t, rec)))
    t = good_truth(lines)
    t["lines"][0]["text"] = None
    check("an unreadable line needs a note", any("needs a note" in p for p in problems_of(t, rec)))
    t["lines"][0]["note"] = "covered by a name tag"
    check("an unreadable line with a note is fine", problems_of(t, rec) == [])
    t = good_truth(lines)
    t["lines"][2]["look"] = 99
    check("a look outside the recording is found", any("outside the recording" in p for p in problems_of(t, rec)))
    t = good_truth(lines)
    t["lines"][3], t["lines"][0] = t["lines"][0], t["lines"][3]
    check("lines arriving out of order are found", any("before an earlier line" in p for p in problems_of(t, rec)))
    t = good_truth(lines)
    t["lines"][0]["look"] = 0
    check("a line at look 0 needs before_start", any("before_start" in p for p in problems_of(t, rec)))
    t = good_truth(lines)
    del t["anchor"]
    check("a missing key is found", any("missing key" in p for p in problems_of(t, rec)))

    # the frames against the truth
    t = good_truth(lines)
    t["lines"].append({"id": 4, "look": 28, "text": "You received EXP (+5)", "colour": "yellow", "note": ""})
    check("a line the frames do not show is found", any("do not show" in p for p in problems_of(t, rec)))
    t = good_truth(lines)
    del t["lines"][3]
    check("a line the truth lacks (the frames show it fresh) is found", any("truth lacks" in p for p in problems_of(t, rec)))
    t2 = copy.deepcopy(t)
    t2["scenery"] = [[int(m[1]), int(m[2])] for m in (re.match(r"look (\d+): .* in slot (\d+) ", p) for p in problems_of(t, rec)) if m]
    check("scenery marks the looks and slots to skip", t2["scenery"] != [] and problems_of(t2, rec) == [])
    t = good_truth(lines)
    t["lines"].append({"id": 4, "look": 28, "text": "You received EXP (+5)", "colour": "yellow", "note": ""})
    t["covered"] = [[28, 29]]
    check("covered looks are skipped", problems_of(t, rec) == [])
    t["covered"] = [[28, 40]]
    check("a covered range outside the recording is found", any("covered range" in p for p in problems_of(t, rec)))

    # lines from before the recording began
    t = good_truth(lines)
    t["lines"].insert(0, {"id": 0, "look": 0, "text": "Bonus EXP for PARTY (+2)", "colour": "yellow", "note": "",
                          "before_start": True})
    for n, ln in enumerate(t["lines"]):
        ln["id"] = n
    check("a before_start line may be faded or gone at look 0", problems_of(t, rec) == [])

    # the stack of every look, as text
    text = L.stacks_text(truth, L.read_recording(rec, GRID), [f["t"] for f in L.load_frames(rec)])
    check("one text line per look", len(text) == LOOKS)
    check("the stack text shows the frames and the truth agreeing", "frames ##" in text[6] and "truth ##" in text[6])

    # contact sheets go only under truth/work
    old_env, old_grids = os.environ.get("MAPLE_CAPTURES"), dict(L.GRIDS)
    os.environ["MAPLE_CAPTURES"] = str(tmp)
    L.GRIDS["synthetic"] = GRID
    try:
        work = tmp / "truth" / "work"
        work.mkdir(parents=True)
        (work / "synthetic.proposed.json").write_text(json.dumps(props), encoding="utf-8")
        sheets = L.write_sheets("synthetic")
        check("sheets are written", bool(sheets) and all(Path(s).exists() for s in sheets))
        check("sheets are only under truth/work", all(Path(s).parent == work for s in sheets))
        pics = L.write_sheets("synthetic", truth)
        check("sheets with the transcription are written", bool(pics) and all("truth-sheet" in Path(s).name for s in pics))
        check("a sheet is a picture", cv2.imread(sheets[0]) is not None and cv2.imread(sheets[0]).shape[2] == 3)
        reads = "# covered 28-29\n2 | E1/w\n5 | E2/w E3/w\n6 | E4/w\n"
        built, warnings = L.build_truth("synthetic", reads, 100, 110, ["1.00", "1.10"])
        check("build: the reads file gives a truth file that validates", warnings == [] and problems_of(built, rec) == [])
        check("build: ids, texts, anchor and covered looks", [ln["id"] for ln in built["lines"]] == [0, 1, 2, 3]
              and built["lines"][1]["text"] == "You received EXP (+2)" and built["anchor"]["right"] == 1914
              and built["covered"] == [[28, 29]] and built["exp_bar"]["start_percent"] == "1.00")
        _, warnings = L.build_truth("synthetic", reads.replace("E1/w", "E1/y"), 100, 110)
        check("build: a typed colour the picture disagrees with is warned about", any("typed yellow" in w for w in warnings))
        missing, _ = L.build_truth("synthetic", "2 | E1/w\n5 | E2/w\n6 | E4/w\n", 100, 110)
        check("build: a line left out shows up in the scenery list to check by eye", missing["scenery"] != [])
        check("build: nothing is listed as scenery when the transcription is complete", built["scenery"] == [])
    finally:
        L.GRIDS.clear()
        L.GRIDS.update(old_grids)
        if old_env is None:
            os.environ.pop("MAPLE_CAPTURES", None)
        else:
            os.environ["MAPLE_CAPTURES"] = old_env

# the reads file's words
parsed, cov = L.parse_reads("# covered 64-73\n0* | P2/y U:E:faded_to_nothing/y M9/w\n24 | I:Stirge Wing:1:Etc/w M10/w\n")
check("parse_reads: lines, colours, before_start and covered looks",
      cov == [[64, 73]] and [ln["text"] for ln in parsed] == ["Bonus EXP for PARTY (+2)", None, "You have gained mesos (+9)",
      "Stirge Wing x1 earned. (Etc)", "You have gained mesos (+10)"] and parsed[0]["before_start"] and not parsed[3]["before_start"]
      and parsed[1]["note"] == "faded to nothing" and parsed[2]["colour"] == "white")

# the slot reader on its own
img = np.full((609, 864, 3), 40, np.uint8)
draw_line(img, 0, 240, 1)
slots = L.read_slots(img, GRID)
check("read_slots finds the line in its slot", L.occupied(slots[0]) and not L.occupied(slots[1]))
check("read_slots measures the strength about right", 190 <= slots[0][1] <= 250)
check("an empty picture has no lines", not any(L.occupied(s) for s in L.read_slots(np.full((609, 864, 3), 40, np.uint8), GRID)))

# the real recordings' truth, when the private repo is there
root = os.environ.get("MAPLE_CAPTURES")
if not root:
    print("skipped: the real truth files (MAPLE_CAPTURES is not set)")
else:
    for name, grid in L.GRIDS.items():
        truth_file = Path(root) / "truth" / f"{name}.json"
        folder = Path(root) / "captures" / name
        if not truth_file.exists() or not folder.exists():
            print(f"skipped: {name} (no truth file or recording in MAPLE_CAPTURES)")
            continue
        real = json.loads(truth_file.read_text(encoding="utf-8"))
        times = [f["t"] for f in L.load_frames(folder)]
        check(f"{name}: the truth file is consistent with its frames",
              L.check_truth(real, L.read_recording(folder, grid), times) == [])

print(f"{failures} failure(s)" if failures else "all passed")
sys.exit(1 if failures else 0)
