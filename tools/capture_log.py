"""Records the game's pickup log (bottom right: EXP, mesos and items gained) for building a reader for it.

Takes the same screenshots the overlay takes (mss: the exact pixels, no video codec, no colour change) many times
a second and saves them as lossless PNGs, so the log's font, line height, how long a line stays and how fast lines
come in a busy party can be measured. One picture of the whole game window is saved at the start and the end, to
see where the log sits.

Usage (from the repo root, with the game open and the overlay's window moved off the bottom right):
    python tools/capture_log.py [--seconds 30] [--fps 10] [--part log | bottom-right | right-half | full]
  It waits 3 seconds, then records. Ctrl+C stops early (what was taken is kept).
  The pictures go to captures/log-<date>-<time>/ (captures/ is not committed): frame_00000.png, ...,
  game_start.png, game_end.png, and frames.json (each frame's time and where the game window was).
On macOS, Terminal (or Python) needs System Settings > Privacy & Security > Screen Recording; restart it after.
The pictures can show chat and names: look through them before sharing them.
"""
import argparse
import json
import queue
import sys
import threading
import time
from pathlib import Path

import cv2
import mss

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from capture import grab                               # noqa: E402
from platforms import create_platform                  # noqa: E402

PARTS = {                       # which part of the game window to record: (left, top, right, bottom) as shares of it
    "log": (0.75, 0.55, 1.0, 0.92),         # just the pickup log, at Default and Ideal UI (small: fast enough for --fps 30)
    "bottom-right": (0.55, 0.45, 1.0, 1.0),
    "right-half": (0.5, 0.0, 1.0, 1.0),
    "full": (0.0, 0.0, 1.0, 1.0),
}
PNG_LEVEL = 1                   # fast PNG compression (still lossless), so saving keeps up with the pictures
BACKLOG = 200                   # pictures waiting to be saved before new ones are dropped (and counted as dropped)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seconds", type=float, default=30)
    ap.add_argument("--fps", type=float, default=10)
    ap.add_argument("--part", choices=sorted(PARTS), default="bottom-right")
    args = ap.parse_args()

    plat = create_platform()
    plat.ask_permissions()
    if why := plat.missing_permission():
        sys.exit(why)
    hwnd = plat.find_game_window()
    if hwnd is None:
        sys.exit("Couldn't find the MapleStory window. Is the game open (and not minimized)?")
    out = ROOT / "captures" / time.strftime("log-%Y%m%d-%H%M%S")
    out.mkdir(parents=True)

    todo = queue.Queue(BACKLOG)

    def saver():
        while (job := todo.get()) is not None:
            cv2.imwrite(str(out / job[0]), job[1], [cv2.IMWRITE_PNG_COMPRESSION, PNG_LEVEL])

    worker = threading.Thread(target=saver, daemon=True)
    worker.start()
    frames, dropped, missed = [], 0, 0
    with mss.mss() as sct:
        def whole(name):
            rect = plat.client_rect(hwnd)
            shot = rect and grab(sct, *rect)
            if shot is not None:
                todo.put((name, shot[0]))

        print("Recording starts in 3 seconds: get the log busy (party, mobs, loot)...")
        time.sleep(3)
        whole("game_start.png")
        step, start = 1 / args.fps, time.perf_counter()
        print(f"Recording for {args.seconds:g} s at {args.fps:g} a second. Ctrl+C stops early.")
        try:
            while (now := time.perf_counter()) - start < args.seconds:
                rect = plat.client_rect(hwnd)
                if rect is None:                        # minimized or gone for a moment
                    missed += 1
                else:
                    gx, gy, gw, gh = rect
                    l, t, r, b = PARTS[args.part]
                    box = (gx + round(gw * l), gy + round(gh * t), round(gw * (r - l)), round(gh * (b - t)))
                    shot = grab(sct, *box)
                    if shot is None:
                        missed += 1
                    else:
                        name = f"frame_{len(frames):05d}.png"
                        try:
                            todo.put_nowait((name, shot[0]))
                            frames.append({"file": name, "t": round(now - start, 3), "game": list(rect),
                                           "box": [shot[1], shot[2], shot[0].shape[1], shot[0].shape[0]]})
                        except queue.Full:
                            dropped += 1
                    print(f"\r  {len(frames)} pictures", end="", flush=True)
                time.sleep(max(0.0, start + (len(frames) + dropped + missed + 1) * step - time.perf_counter()))
        except KeyboardInterrupt:
            pass
        whole("game_end.png")
    print("\nSaving the last pictures...")
    todo.put(None)
    worker.join()
    (out / "frames.json").write_text(json.dumps({
        "fps": args.fps, "part": args.part, "dropped": dropped, "missed": missed, "frames": frames},
        indent=1), encoding="utf-8")
    print(f"Saved {len(frames)} pictures to {out}" + (f" ({dropped} dropped: saving fell behind)" if dropped else ""))


if __name__ == "__main__":
    main()
