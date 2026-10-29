"""Tests for the pickup log's item names (pickup_items.py and assets/items.txt). No game or screen needed.

Run from the project folder:  python tests/test_pickup_items.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pickup_items as pi  # noqa: E402

failures = 0


def check(name, ok):
    global failures
    print(("PASS " if ok else "FAIL ") + name)
    failures += not ok


real = pi.ItemList.load()
SMALL = pi.ItemList([                                    # a small list of our own, for the cases the real one can't pin down
    ("Stirge Wing", "Etc"), ("Red Potion", "Use"), ("White Potion", "Use"), ("Lollipop", "Equip"), ("Lollipop", "Cash"),
    ("Dark Crystal Ore", "Etc"), ("Dark Crystal Orb", "Etc"), ("Warrior Scroll III", "Use"), ("Mushroom Cap", "Etc"),
    ("Blue Line Tank Top", "Cash"), ("Blue Line Tanktop", "Cash"), ("Hero's Gladius", "Equip"), ("Modern Hat", "Equip"),
    ("10,000 Meso Pouch", "Use"), ("50,000 Meso Pouch", "Use"), ("Moon Rock", "Etc"), ("Set Piece", "Set-up"),
    ("Heartstone", "Etc"), ("Heartstones", "Etc"), ("Orange Mushroom Invasion", "Use"), ("Orange Mushroom Invasion", "Cash"),
])

# ---- the shipped list
check("assets/items.txt is there and big (thousands of items)", len(real) > 4000)
check("every item is on one of the five tabs", {t for _, t in real.entries} <= set(pi.TABS))
check("the usual drops are on the list", all(real.snap(n) is not None for n in ("Stirge Wing", "Red Potion", "Orange Mushroom Cap")))
check("Stirge Wing is an Etc item", real.snap("Stirge Wing") == ("Stirge Wing", "Etc"))
check("the file has no pictures or stray lines: name, tab character, tab",
      all(re.fullmatch(r"[^\t]+\t(Equip|Use|Etc|Set-up|Cash)", l) for l in Path(pi.ITEMS_PATH).read_text(encoding="utf-8").splitlines()))
check("meowdb's '(Lv 10)' note is taken off equipment names", not any(re.search(r"\(Lv \d+\)$", n) for n, _ in real.entries))
check("every item on the list snaps to itself and its tab (nothing on it is confused with another)",
      all(real.snap(n, t) == (n, t) for n, t in real.entries))
check("a missing list snaps nothing (fail closed)", pi.ItemList.load(Path("no/such/items.txt")).snap("Stirge Wing") is None)

# ---- exact names and how they are tidied
check("exact name", SMALL.snap("Stirge Wing") == ("Stirge Wing", "Etc"))
check("exact name with the tab it was picked up into", SMALL.snap("Red Potion", "Use") == ("Red Potion", "Use"))
check("other capitals and spaces still give the list's spelling", SMALL.snap("stirge  WING") == ("Stirge Wing", "Etc"))
check("a curly apostrophe is the game's apostrophe", SMALL.snap("Hero’s Gladius") == ("Hero's Gladius", "Equip"))
check("a missing apostrophe is still the item", SMALL.snap("Heros Gladius") == ("Hero's Gladius", "Equip"))
check("the tab 'Setup' is the Set-up tab", SMALL.snap("Set Piece", "Setup") == ("Set Piece", "Set-up"))
check("a name on two tabs: the tab it was read with decides", SMALL.snap("Lollipop", "Cash") == ("Lollipop", "Cash"))
check("a name on two tabs and no tab read: the name is sure, the tab is not", SMALL.snap("Lollipop") == ("Lollipop", None))
check("a tab that isn't a tab gives nothing", SMALL.snap("Stirge Wing", "Quest") is None)
check("the wrong tab for the name gives nothing", SMALL.snap("Stirge Wing", "Use") is None)
check("names that differ only in punctuation: the exact spelling wins", SMALL.snap("Blue Line Tank Top") == ("Blue Line Tank Top", "Cash"))
check("...and a spelling that fits both equally is not guessed", SMALL.snap("blue line tank-top") is None)

# ---- slips of the font reader that must snap
check("l read for I and 1 read for l", SMALL.snap("St1rge Wlng") == ("Stirge Wing", "Etc"))
check("I read for l", SMALL.snap("Lo11ipop", "Cash") == ("Lollipop", "Cash"))
check("0 read for O", SMALL.snap("0range Mushroom Invasion", "Use") == ("Orange Mushroom Invasion", "Use"))
check("O read for 0 inside a number", SMALL.snap("1O,OOO Meso Pouch") == ("10,000 Meso Pouch", "Use"))
check("rn read for m", SMALL.snap("Mushroorn Cap") == ("Mushroom Cap", "Etc"))
check("m read for rn", SMALL.snap("Modem Hat") == ("Modern Hat", "Equip"))
check("| and ! read for I", SMALL.snap("Warrior Scroll |||") == ("Warrior Scroll III", "Use") and SMALL.snap("Warrior Scroll !!!") == ("Warrior Scroll III", "Use"))
check("Roman numeral misread (Il for II)", pi.ItemList([("Warrior Scroll II", "Use")]).snap("Warrior Scroll Il") == ("Warrior Scroll II", "Use"))
check("Roman numeral misread (Vl for VI)", pi.ItemList([("Dragon Scroll VI", "Use")]).snap("Dragon Scroll Vl") == ("Dragon Scroll VI", "Use"))
check("a dropped letter", SMALL.snap("Stirge Wng") == ("Stirge Wing", "Etc") and SMALL.snap("Mushroom Cp") == ("Mushroom Cap", "Etc"))
check("a doubled letter", SMALL.snap("Stirgee Wing") == ("Stirge Wing", "Etc") and SMALL.snap("Mushrooom Cap") == ("Mushroom Cap", "Etc"))
check("a dropped letter, with the tab", SMALL.snap("Whte Potion", "Use") == ("White Potion", "Use"))
check("the same slips on the real list", real.snap("Stirge Wng", "Etc") == ("Stirge Wing", "Etc") and real.snap("St1rge Wlng", "Etc") == ("Stirge Wing", "Etc"))

# ---- near-ties and other things that must NOT snap
check("two names fit about as well: Ore / Orb", SMALL.snap("Dark Crystal Or") is None and SMALL.snap("Dark Crystal Orx") is None)
check("a dropped letter that fits two names", pi.ItemList([("Red Potion", "Use"), ("Rod Potion", "Use")]).snap("Rd Potion") is None)
check("a read that is itself on the list is not pulled to a longer name", SMALL.snap("Heartstone") == ("Heartstone", "Etc"))
check("a doubled letter in a name with a digit is not a slip", pi.ItemList([("Scroll 60", "Use")]).snap("Scroll 600") is None)
check("a dropped digit is not a slip: 10,000 / 50,000", SMALL.snap("0,000 Meso Pouch") is None and SMALL.snap("1,000 Meso Pouch") is None)
check("a wrong digit is not a slip: 10,000 / 50,000", SMALL.snap("20,000 Meso Pouch") is None)
check("a different letter is not a slip", SMALL.snap("Stirge Wind") is None and SMALL.snap("Stirge Wlng Cap") is None)
check("an extra letter that is not a doubled one is not a slip", SMALL.snap("Stirge Wingx") is None)
check("short names allow no dropped or doubled letter", pi.ItemList([("Axe", "Equip"), ("Ice", "Etc")]).snap("Ax") is None)
check("a name not on the list", SMALL.snap("Dragon Slayer's Cloak") is None and real.snap("Zzyzx Blorp Glorp") is None)
check("nothing or junk", all(SMALL.snap(t) is None for t in ("", " ", "x", "!!", "..")))
check("a name already fine is not turned into a fix", pi.ItemList([("Elixir of Vi", "Use")]).snap("Elixir of Vi") == ("Elixir of Vi", "Use"))

# ---- never a wrong name, on every real item
dropped_wrong = doubled_wrong = dropped_ok = tried = 0
for name, tab in real.entries:
    letters = [i for i, c in enumerate(name) if c.isalpha()]
    if len(letters) < 8:
        continue
    for i in (letters[1], letters[len(letters) // 2], letters[-2]):
        for slipped in (name[:i] + name[i + 1:], name[:i] + name[i] + name[i:]):    # one dropped, one doubled
            tried += 1
            got = real.snap(slipped, tab)
            if got is not None and got[0] != name:
                # (another name on the list may be this very spelling bar its punctuation, "Skull Shirt" for "Skull T-Shirt" minus T; that one is then the right answer)
                if pi._plain_key(got[0]) != pi._plain_key(slipped):
                    dropped_wrong += 1
            dropped_ok += got == (name, tab)
check(f"a slip never gives another item ({tried} slips tried on the real list, {dropped_ok} snapped back)", dropped_wrong == 0 and tried > 1000)

print("ALL PASS" if not failures else f"{failures} FAILED")
sys.exit(1 if failures else 0)
