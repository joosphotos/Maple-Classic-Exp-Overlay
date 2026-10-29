"""A stand-in OS for running the overlay's tests on Linux (a cloud container, say). It has no game
window, no hotkeys and no real screen, so nothing can be read from a game. create_platform() hands it
out on Linux only when MAPLE_EXP_PLATFORM=headless is set; the app itself never asks for it."""
import os
import platform
import tempfile
from pathlib import Path

from .base import Hotkeys, Platform


class HeadlessHotkeys(Hotkeys):
    """No hotkeys: there is no keyboard to watch."""

    supported = False

    def set(self, keys, on=True):
        pass

    def pause(self, paused):
        pass


class HeadlessPlatform(Platform):
    name = "headless"

    def version(self):
        return f"Headless test platform ({platform.system()} {platform.release()})"

    def data_root(self):
        # The tests always set MAPLE_EXP_DATA; if one didn't, a new temp folder keeps real data out of reach.
        return Path(os.environ.get("MAPLE_EXP_DATA") or tempfile.mkdtemp(prefix="MapleEXP-headless-"))

    def tesseract_candidates(self, home_dir, app_dir):
        on_path = [Path(d) / "tesseract" for d in os.environ.get("PATH", "").split(os.pathsep)
                   if d.strip() and os.path.isabs(d.strip())]
        return [home_dir / "tesseract" / "tesseract", app_dir / "tesseract" / "tesseract", *on_path]

    def tessdata_candidates(self, exe):
        return [exe.parent.parent / "share" / "tessdata", Path("/usr/share/tesseract-ocr/5/tessdata"),
                Path("/usr/share/tesseract-ocr/4.00/tessdata"), Path("/usr/share/tessdata")]

    def tessdata_arg(self, exe, folder):
        return "" if folder == exe.parent.parent / "share" / "tessdata" else str(folder)

    def claim_single_instance(self, key, title, old_titles=()):
        return True

    def find_game_window(self):
        return None

    def window_exists(self, handle):
        return False

    def client_rect(self, handle):
        return None

    def own_window_rect(self, root):
        return None

    def screen_dpi(self, x, y):
        return 96

    def create_hotkeys(self, on_press):
        return HeadlessHotkeys(on_press)

    def open_folder(self, path):
        pass

    def show_file(self, path):
        pass
