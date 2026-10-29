"""Makes the item-name list used by the pickup log reader (assets/items.txt) from a saved copy of
https://meowdb.com/msclassic/item-db/all (a fan-made MapleStory Classic database; thank you to its makers, who
agreed to this use). The list lets the reader trust a name it read letter by letter only when it is a real item
(pickup_items.py), the same way map names are put right against assets/maps.txt (server/tools/make_maps.py).

  py -3 tools/make_items.py <saved item-db/all html page>

It never goes online: save the page in a browser (or with a polite one-off download), then run this. Run it again
when the game adds items. One line per item: name, a tab character, the inventory tab it is picked up into.

The page groups every item under a tab heading (Equip, Use, Setup, Cash, Cash Equip, Etc). The game has five
inventory tabs; cash equipment lives in the Cash tab, so "Cash Equip" becomes "Cash" here."""
import html
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# meowdb's heading for each group of items -> the tab the game names in the pickup line ("(Etc)").
# Anything else is refused (the page changed: look before trusting it).
TABS = {"Equip": "Equip", "Use": "Use", "Setup": "Set-up", "Etc": "Etc", "Cash": "Cash", "Cash Equip": "Cash"}

# meowdb adds a note to names it would otherwise show twice: "Black Cloth Pants (Lv 10)" and "(Lv 30)", or
# "Cake (Alt)". The game's own name has no such note, so it is taken off (assumed: PL-02's truth confirms or
# corrects this with real item lines).
LISTING_NOTE = re.compile(r"\s*\((?:Lv\s*\d+|Alt(?:\s*\d+)?)\)$")

# Fewest items a good page has (the page said 5,515 when this was written); fewer means the layout changed.
MIN_ITEMS = 4000


def clean(name):
    """One item name as the game writes it: tidy spaces, no listing note, plain apostrophes."""
    name = html.unescape(re.sub(r"<[^>]+>", "", name)).replace("\xa0", " ")
    name = name.replace("’", "'").replace("‘", "'")
    name = LISTING_NOTE.sub("", re.sub(r"\s+", " ", name).strip())
    return name


def parse(page):
    """[(name, tab), ...] sorted, from the saved page; a name picked up in two tabs is listed once for each."""
    found = set()
    unknown = set()
    start = page.find("All Items A-Z")                 # the menus before it have <h2> headings of their own
    if start < 0:
        sys.exit("no 'All Items A-Z' heading: this is not the item-db/all page")
    for group in re.split(r"<h2[^>]*>", page[start:])[1:]:
        heading, _, body = group.partition("</h2>")
        heading = html.unescape(re.sub(r"<[^>]+>", "", heading)).strip()
        if heading not in TABS:
            unknown.add(heading)
            continue
        for _, inner in re.findall(r'<a[^>]*href="/msclassic/item-db/(\d+)"[^>]*>(.*?)</a>', body, re.S):
            name = clean(inner)
            if 2 <= len(name) <= 80:
                found.add((unicodedata.normalize("NFC", name), TABS[heading]))
    if unknown:
        sys.exit(f"unknown item groups on the page: {sorted(unknown)}: the layout may have changed")
    return sorted(found)


def main(path):
    items = parse(Path(path).read_text(encoding="utf-8"))
    if len(items) < MIN_ITEMS:
        sys.exit(f"only {len(items)} items found: the page layout may have changed")
    (ROOT / "assets" / "items.txt").write_text("".join(f"{n}\t{t}\n" for n, t in items), encoding="utf-8", newline="\n")
    tabs = {}
    for _, t in items:
        tabs[t] = tabs.get(t, 0) + 1
    print(f"{len(items)} items: " + ", ".join(f"{t} {c}" for t, c in sorted(tabs.items())))


if __name__ == "__main__":
    main(sys.argv[1])
