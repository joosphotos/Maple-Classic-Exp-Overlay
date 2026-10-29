"""The game's item names, to trust an item name the pickup log reader read letter by letter (PL-03).

"Stirge Wing x1 earned. (Etc)": the name is free text, so it is only believed when it is a real item, the way map
names are put right against assets/maps.txt (maple_exp.MapList). assets/items.txt (made by tools/make_items.py from
meowdb.com's item list, thank you) has one line per item: name, a tab, the inventory tab it is picked up into.

`snap` is strict, because a wrong name is worse than an unread one (the project fails closed):
  1. the exact name (also with other capitals or punctuation);
  2. the same name after only the slips a font reader makes: l / I / 1 / | / !, O / 0, and "rn" for "m";
  3. the same after one dropped or doubled letter (never in a name with a digit, and only in names of 6+ characters);
  4. in every step the name must be the ONLY one that fits. Two that fit about as well = None, never a guess.

Pure: no screen, no game. Nothing is downloaded: the list ships with the app."""
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ITEMS_PATH = Path(__file__).resolve().parent / "assets" / "items.txt"    # the game's item names (tools/make_items.py)

TABS = ("Equip", "Use", "Etc", "Set-up", "Cash")    # the five inventory tabs, as the pickup line names them
MIN_KEY = 3                                         # a name shorter than this (letters and digits) is never snapped
MIN_SLIP_KEY = 6                                    # a dropped or doubled letter is only allowed in names this long

_ROMAN = re.compile(r"^(?:X{0,2})(?:IX|IV|V?I{0,3})$")


def _fix_roman(name):
    """A last word that is a Roman numeral misread ("Vil" -> VII, "lV" -> IV, "il" -> II, "V1" -> VI). Plain numbers
    and ordinary words are left alone. Same rule as maple_exp._fix_roman (kept by hand: this file imports nothing
    from maple_exp so it runs anywhere)."""
    def fix(m):
        token = m.group(2)
        if not re.search(r"[IVXivxl|!]", token):
            return m.group(0)                          # only digits: a number
        numeral = re.sub(r"[li1|!]", "I", token, flags=re.I).upper()
        return m.group(1) + numeral if numeral and _ROMAN.match(numeral) else m.group(0)
    return re.sub(r"(\s)([IVXivxl1|!]{1,6})$", fix, name)


def _tidy(text):
    """Plain spaces, plain apostrophes, accents kept (the list's own spelling)."""
    text = re.sub(r"[’‘`´]", "'", text.replace("\xa0", " "))
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def _plain_key(text):
    """Only letters and digits, lower case, no accents: names that differ in capitals, spaces or punctuation match."""
    text = unicodedata.normalize("NFKD", _tidy(text))
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in text if not unicodedata.combining(c)).lower())


def _fold_key(text):
    """The plain key with the slips a font reader makes made the same: l, I, 1, | and ! are one letter, O and 0 are
    one, and "rn" is "m". Applied to the list's names and to the read alike, so they meet in the middle."""
    text = _tidy(text).replace("|", "i").replace("!", "i")
    key = _plain_key(text)
    return key.replace("l", "i").replace("1", "i").replace("0", "o").replace("rn", "m")


def _one_extra_letter(long, short, doubled):
    """True when `long` is `short` with one letter added (a letter, never a digit); with `doubled` only a letter
    that repeats the one before it."""
    if len(long) != len(short) + 1:
        return False
    i = 0
    while i < len(short) and long[i] == short[i]:
        i += 1
    if long[i + 1:] != short[i:] or not long[i].isalpha():
        return False
    return not doubled or (i > 0 and long[i] == long[i - 1])


def _tab_name(tab):
    """The canonical tab for a tab as read ("Set-up", "Setup" and "Set up" are one), or None."""
    key = _plain_key(tab or "")
    return next((t for t in TABS if _plain_key(t) == key), None)


class ItemList:
    """The game's item names with their tabs. Missing or damaged list = empty: nothing snaps (fail closed)."""

    def __init__(self, entries=()):
        self.entries = sorted({(_tidy(n), t) for n, t in entries if _tidy(n) and t in TABS})
        self.tabs_of = defaultdict(set)                 # name -> the tabs it is picked up into
        for name, tab in self.entries:
            self.tabs_of[name].add(tab)
        self.by_plain = defaultdict(set)                # plain key -> names
        self.by_fold = defaultdict(set)                 # fold key -> names
        for name in self.tabs_of:
            self.by_plain[_plain_key(name)].add(name)
            self.by_fold[_fold_key(name)].add(name)

    @classmethod
    def load(cls, path=ITEMS_PATH):
        try:
            lines = Path(path).read_text(encoding="utf-8").splitlines()
        except (OSError, ValueError):                   # (a missing file, or one damaged into bytes that aren't text)
            lines = []
        entries = []
        for line in lines:
            name, _, tab = line.partition("\t")
            if name.strip() and tab.strip() in TABS:
                entries.append((name, tab.strip()))
        return cls(entries)

    def __len__(self):
        return len(self.entries)

    def snap(self, text, tab=None):
        """(name, tab) for an item name as read, or None when it is not clearly one item on the list.
        `tab` is the tab the line named ("Etc" in "... earned. (Etc)"), when it was read: it narrows the list, so
        fewer names can be mistaken for each other; one that isn't a tab at all gives None. Without it, a name picked
        up into several tabs ("Lollipop") comes back with tab None: the name is sure, the tab is not."""
        if tab is not None:
            tab = _tab_name(tab)
            if tab is None:
                return None
        for read in dict.fromkeys((_tidy(text), _fix_roman(_tidy(text)))):     # as read first, then with a numeral put right
            name = self._snap_one(read, tab)
            if name == "":
                return None                             # two names fit: stop here, a looser look would only fit more
            if name:
                tabs = self.tabs_of[name] if tab is None else {tab}
                return name, (next(iter(tabs)) if len(tabs) == 1 else None)
        return None

    def _usable(self, names, tab):
        """The names of `names` that are picked up into `tab` (all of them without a tab)."""
        return {n for n in names if tab is None or tab in self.tabs_of[n]}

    def _snap_one(self, read, tab):
        """The one name that fits `read`, "" when more than one fits, None when none does."""
        plain, fold = _plain_key(read), _fold_key(read)
        if len(plain) < MIN_KEY:
            return None
        exact = self._usable(self.by_plain.get(plain, ()), tab)
        if read in exact:
            return read                                 # the very same spelling beats a name that differs in punctuation only
        for found in (exact, self._usable(self.by_fold.get(fold, ()), tab)):
            if found:
                return next(iter(found)) if len(found) == 1 else ""
        if len(fold) < MIN_SLIP_KEY or re.search(r"\d", plain):
            return None                                 # (a name with a digit: a missing or extra letter could hide a wrong number)
        near = set()
        for key, names in self.by_fold.items():         # (a few thousand short compares; only for the rare line that got this far)
            if abs(len(key) - len(fold)) != 1 or min(len(key), len(fold)) < MIN_SLIP_KEY:
                continue
            if (_one_extra_letter(key, fold, doubled=False) if len(key) > len(fold)       # the read lost a letter
                    else _one_extra_letter(fold, key, doubled=True)):                      # the read doubled a letter
                near |= {n for n in self._usable(names, tab) if not re.search(r"\d", n)}
        return next(iter(near)) if len(near) == 1 else ("" if near else None)


_ITEM_LIST = None


def item_list():
    global _ITEM_LIST
    if _ITEM_LIST is None:
        _ITEM_LIST = ItemList.load()
    return _ITEM_LIST


def snap(text, tab=None):
    """(name, tab) for an item name as read, or None (see ItemList.snap), against the list that ships with the app."""
    return item_list().snap(text, tab)
