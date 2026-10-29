"""Rough measurements of the pickup log in a recording made by tools/capture_log.py (not a reader: no text is read).

It finds text by its shadow (a bright pixel over a dark pixel one down and right), so it is fooled now and then by
the scene behind the log; use it for numbers about the log (line height, how fast lines come, how they fade), never
as an answer for a test. These are the numbers in docs/pickup-log/PLAN.md, "What the recordings show".

Usage (from the repo root):
    python -I tools/pickup_probe.py grid <recording folder> <x0>
        rows with the most text and the line pitch (autocorrelation), from column x0 rightwards
    python -I tools/pickup_probe.py arrivals <recording folder> <x0> <bottom> <pitch>
        new lines per look (how far the stack moved), the busiest second, the busiest look, and how long a line
        stays readable; bottom: the row just under the newest line, pitch: the line height (both in the frames)
    python -I tools/pickup_probe.py fade <recording folder> <x0> <band top> <right>
        the strength of the newest line, look by look, while no new line comes (how a line fades)
  For the Mac recordings of 2026-10-29: Ideal UI (log-20261029-131006): x0 560, bottom 461, pitch 14, band top 446,
  right 858. Default UI (log-20261029-130655): pitch about 19.7 (14 x 1080 / 768).
"""
import json
import sys
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

LINES = 7                   # lines looked at, newest at the bottom
EDGE = 80                   # a shadow pixel is darker than this (brightest channel)
BRIGHT = 150                # a text pixel's red and green are above this (white or yellow)
MIN_INK = 20                # a line with fewer text pixels is empty


def frames(folder):
    return json.loads((folder / "frames.json").read_text(encoding="utf-8"))["frames"]


def text_mask(img):
    """Bright pixels with a dark pixel one down and right of them."""
    im = img.astype(np.int16)
    bright = (im[..., 2] > BRIGHT) & (im[..., 1] > BRIGHT)
    dark = im.max(axis=2) < EDGE
    shadow = np.zeros_like(dark)
    shadow[:-1, :-1] = dark[1:, 1:]
    return bright & shadow


def grid(folder, x0):
    total = None
    for f in frames(folder):
        rows = text_mask(cv2.imread(str(folder / f["file"]))[:, x0:]).sum(axis=1)
        total = rows if total is None else total + rows
    print("rows with the most text:", sorted(np.argsort(total)[::-1][:40].tolist()))
    a = total - total.mean()
    ac = np.correlate(a, a, "full")[len(a) - 1:]
    print("line pitch candidates:", [int(v) for v in np.argsort(ac[6:60])[::-1][:5] + 6])


def arrivals(folder, x0, bottom, pitch):
    fr = frames(folder)

    def lines(i):
        m = text_mask(cv2.imread(str(folder / fr[i]["file"]))[bottom - LINES * pitch: bottom, x0:])
        return [m[k * pitch:(k + 1) * pitch] for k in range(LINES)]

    prev, steps, inks = lines(0), [], []
    for i in range(1, len(fr)):
        cur = lines(i)
        best = (0.0, 0, 0)
        for s in range(LINES):                      # cur line k is the last look's line k + s
            score, n = 0.0, 0
            for k in range(LINES - s):
                a, b = cur[k], prev[k + s]
                if a.sum() + b.sum() < MIN_INK:
                    continue
                score += (a & b).sum() / max(1, (a | b).sum())
                n += 1
            score = score / n if n else 0.0
            if score > best[0] + 0.02:
                best = (score, s, n)
        score, s, n = best
        if n == 0 or score < 0.3:                   # nothing lines up: all new if the last look was empty, else unsure
            s = sum(int(l.sum() >= MIN_INK) for l in cur) if all(l.sum() < MIN_INK for l in prev) else -1
        steps.append(s)
        inks.append([int(l.sum()) for l in cur])
        prev = cur
    a = np.array(steps)
    ok = np.where(a < 0, 0, a)
    secs = len(a) / 10
    print(f"looks {len(a)}, unsure {int((a < 0).sum())}, new lines {int(ok.sum())} ({ok.sum() / secs:.2f} a second)")
    print("busiest second:", int(np.convolve(ok, np.ones(10), "valid").max()), " busiest look:", int(ok.max()))
    print("new lines per look:", sorted(Counter(a.tolist()).items()))
    print("most lines with text at once:", max(sum(v >= MIN_INK for v in x) for x in inks))
    life = []
    for i, s in enumerate(steps):                   # follow each new line up the stack until it fades
        for j in range(max(s, 0)):
            row, t = LINES - 1 - j, i
            while t + 1 < len(steps) and steps[t + 1] >= 0:
                t += 1
                row -= steps[t]
                if row < 0 or inks[t][row] < MIN_INK:
                    break
            if row >= 0 and t + 1 < len(steps):
                life.append(t - i)
    if life:
        print(f"looks a line stays readable: median {np.median(life):g}, 90% within {np.percentile(life, 90):g}")


def fade(folder, x0, top, right):
    fr = frames(folder)

    def strength(i):
        g = cv2.imread(str(folder / fr[i]["file"]))[top:top + 12, x0:right].astype(np.float32).max(axis=2)
        return float(np.percentile(g[:-1, :-1] - g[1:, 1:], 99))

    s = [strength(i) for i in range(len(fr))]
    for i in range(1, len(s)):
        if s[i] > 100 and s[i] > s[i - 1] + 25:     # a new line at the bottom
            run, j = [s[i]], i + 1
            while j < len(s) and s[j] <= s[j - 1] + 10 and len(run) < 30:
                run.append(s[j])
                j += 1
            if len(run) >= 12:
                print(f"look {i}:", [int(v) for v in run])


def main():
    cmd, folder, *nums = sys.argv[1:]
    folder, nums = Path(folder), [int(n) for n in nums]
    {"grid": grid, "arrivals": arrivals, "fade": fade}[cmd](folder, *nums)


if __name__ == "__main__":
    main()
