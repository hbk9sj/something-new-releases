"""Mechanical gate for @nueraviX drafts. Prints FAIL / WARN lines, then PASS (exit 0) or a count (exit 1).

usage: python3 tools/check_x_draft.py drafts.json state/history.json [--max-chars 280]

drafts.json:  {"drafts": [{"id": "orig", "kind": "original", "finding_id": "kolibri-tokens-de",
                           "parts": ["post 1", "post 2"], "time": "2026-10-05T13:30:00+00:00"},
                          {"id": "A", "kind": "reply", "parts": ["@name reply text"], "time": "..."}]}
              kind "original" = a new post or thread (parts 2+ are its own thread); kind "reply" = a reply to
              someone else. Every original needs a finding_id: a short stable name for what was measured.
              An original may carry "image": {"url": <printed by tools/push_image.py>, "alt": <what it shows>}.
history.json: a list of the account's own posts (published and scheduled), each with "text", "createdAt"
              (ISO, or X's "Wed Sep 09 13:17:26 +0000 2026"), "kind" (original | reply | thread) and, for
              originals, "finding_id". Required: a missing history file fails, because an empty history would
              let a reply burst through one draft at a time.
FAIL blocks publishing. WARN is printed for the run's report and does not block.
Times without a timezone are read as UTC. Thresholds are house rules set 5 Oct 2026 from this account's
9 Sep reply burst; X's own thresholds are not published.
"""
import json, re, sys, unicodedata
from datetime import datetime, timedelta, timezone

URL_CHARS = 23
REPLY_DUP, ANY_DUP = 0.25, 0.35   # shared-word overlap (Jaccard): reply vs reply, and any other pair
REPLY_GAP_MIN, MAX_REPLIES_24H = 10, 5
OPENER_WORDS, OPENER_DAYS, HISTORY_DAYS = 3, 14, 30
STOP = set("the a an of to in on and or is are was it its that this for with as at by be we our you your".split())
ONE = ((0, 0x10FF), (0x2000, 0x200D), (0x2010, 0x201F), (0x2032, 0x2037))  # twitter-text config v3: weight 1
KINDS = {"original", "reply", "thread"}
IMAGE_URL = re.compile(r"https://raw\.githubusercontent\.com/hbk9sj/something-new-releases/[0-9a-f]{40}"
                       r"/nueravix-x/images/[\w./-]+\.png")   # pinned to a commit, so it never changes
ALT_MAX = 1000   # X's alt-text limit


def when(s):
    if not s:
        raise SystemExit("FAIL every draft and history item needs a time")
    for f in ("%a %b %d %H:%M:%S %z %Y", None):
        try:
            t = datetime.strptime(s, f) if f else datetime.fromisoformat(s)
            return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            pass
    raise SystemExit(f"FAIL unreadable time: {s!r}")


def body(t, reply=True):  # drop URLs, and a reply's leading @names
    t = re.sub(r"https?://\S+", " ", t)
    return (re.sub(r"^(\s*@\w+)+", " ", t) if reply else t).strip()


def words(t):  # trailing punctuation dropped, so "servers," matches "servers"
    return [w.rstrip(".,'-") for w in re.findall(r"[a-z0-9][a-z0-9.,%$'-]*", body(t).lower())]


def overlap(a, b):
    a, b = ({w for w in words(t) if w not in STOP} for t in (a, b))
    return len(a & b) / len(a | b) if a and b else 0.0


def figures(t):
    """Distinctive figures: not glued to letters (o200k), not a bare year; 3+ digits, or any % or $ figure.
    Normalised so 36,320 = 36320 and 5.0% = 5%."""
    out = set()
    for n in re.findall(r"(?<![A-Za-z\d])\$?\d[\d,]*(?:\.\d+)?%?(?![A-Za-z])", body(t)):
        n = n.rstrip(".,")
        if re.fullmatch(r"(19|20)\d\d", n):  # before dropping commas: "2,094" is a count, not a year
            continue
        n = n.replace(",", "")
        num = re.sub(r"[^\d.]", "", n)
        if "." in num:
            num = num.rstrip("0").rstrip(".")
        n = ("$" if "$" in n else "") + num + ("%" if "%" in n else "")
        if len(re.sub(r"\D", "", num)) >= 3 or "%" in n or "$" in n:
            out.add(n)
    return out


def x_len(t, reply):  # X: NFC, URL = 23, characters outside ONE (emoji, CJK, "…") weigh 2, not a reply's @names
    t = unicodedata.normalize("NFC", t)
    t = re.sub(r"https?://\S+", "x" * URL_CHARS, t)
    if reply:
        t = re.sub(r"^(\s*@\w+)+\s*", "", t)
    t = re.sub(r"‍|[︎️]|[\U0001F3FB-\U0001F3FF]", "", t)  # joined emoji count once, roughly
    return sum(1 if any(a <= ord(ch) <= b for a, b in ONE) else 2 for ch in t)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    max_chars = int(sys.argv[sys.argv.index("--max-chars") + 1]) if "--max-chars" in sys.argv else 280
    if "--max-chars" in sys.argv:
        args.remove(str(max_chars))
    if len(args) < 2:
        print("FAIL history is required: pass the drafts file and state/history.json")
        sys.exit(1)
    drafts = json.load(open(args[0])).get("drafts") or []
    hist = json.load(open(args[1]))
    fails, warns = [], []
    ids = [d.get("id") for d in drafts]
    if not drafts:
        fails.append("no drafts")
    if len(set(ids)) != len(ids) or None in ids:
        fails.append("every draft needs its own id")
    for d in drafts:
        if d.get("kind") not in ("original", "reply"):
            fails.append(f"draft {d.get('id')}: kind must be original or reply")
        parts = d.get("parts") or []
        if not parts or any(not isinstance(p, str) or not body(p, d.get("kind") == "reply") for p in parts):
            fails.append(f"draft {d.get('id')}: every part needs text")
        if d.get("kind") == "reply" and len(parts) != 1:
            fails.append(f"draft {d.get('id')}: a reply has exactly one part")
        if d.get("kind") == "original" and not d.get("finding_id"):
            fails.append(f"draft {d.get('id')}: an original needs a finding_id")
        if "image" in d:
            img = d["image"] if isinstance(d["image"], dict) else {}
            if d.get("kind") != "original" or not IMAGE_URL.fullmatch(img.get("url") or ""):
                fails.append(f"draft {d.get('id')}: image url must be an original's PNG pushed by tools/push_image.py")
            alt = (img.get("alt") or "").strip()
            if not alt or len(alt) > ALT_MAX:
                fails.append(f"draft {d.get('id')}: image needs alt text, 1 to {ALT_MAX} characters")
    if fails:
        for f in fails:
            print("FAIL", f)
        sys.exit(1)

    # item: label, group, role (original | reply | thread), time, text, is_new
    items = []
    for d in drafts:
        for i, p in enumerate(d["parts"]):
            role = "reply" if d["kind"] == "reply" else ("original" if i == 0 else "thread")
            items.append((f"draft {d['id']} part {i+1}", f"d:{d['id']}", role, when(d["time"]), p, True))
    hist = [h for h in hist if h.get("status") != "rejected"]   # Buffer refused it: it never went out
    for n, h in enumerate(hist):
        role = h.get("kind") or ("reply" if h.get("isReply") else "original")
        if role not in KINDS:
            print(f"FAIL history item {h.get('id', n)}: kind must be one of {sorted(KINDS)}")
            sys.exit(1)
        t = when(h.get("createdAt"))
        texts = h.get("parts") or [h.get("text", "")]
        for i, p in enumerate(texts):   # a stored thread's later parts are compared too
            items.append((f"history {h.get('id', n)}" + (f" part {i+1}" if i else ""), f"h:{h.get('id', n)}:{n}",
                          role if i == 0 else "thread", t, p, False))
    start = min(x[3] for x in items if x[5])
    recent = [x for x in items if x[5] or start - x[3] <= timedelta(days=HISTORY_DAYS)]
    new = [x for x in recent if x[5]]

    # a finding is posted once, ever (not only in the last 30 days)
    posted = {h.get("finding_id") for h in hist if h.get("finding_id")}
    seen = set()
    for d in drafts:
        f = d.get("finding_id")
        if f and (f in posted or f in seen):
            fails.append(f"draft {d['id']}: finding {f!r} was already posted or queued. A posted finding is not posted again")
        seen.add(f)

    for x in new:
        n = x_len(x[4], x[2] == "reply")
        if n > max_chars:
            fails.append(f"{x[0]}: {n} characters, limit {max_chars}")
    for x in (x for x in new if x[2] == "original"):
        if not re.search(r"(?<![A-Za-z])\d", body(x[4], reply=False)):
            fails.append(f"{x[0]}: post 1 contains no numeral. The finding goes in post 1")
        for h in (h for h in recent if not h[5]):
            shared = figures(x[4]) & figures(h[4])
            if len(shared) >= 2:
                warns.append(f"{x[0]} shares figures with {h[0]} ({', '.join(sorted(shared))}): confirm it is a new finding")

    for i, a in enumerate(new):
        for b in recent:
            if b[1] == a[1] or (b[5] and new.index(b) < i):
                continue
            j = overlap(a[4], b[4])
            if j >= (REPLY_DUP if a[2] == b[2] == "reply" else ANY_DUP):
                fails.append(f"{a[0]} is a near-duplicate of {b[0]} (overlap {j:.2f})")
            oa, ob = ([w for w in words(t) if w not in STOP][:OPENER_WORDS] for t in (a[4], b[4]))
            if len(oa) == OPENER_WORDS and oa == ob and abs(a[3] - b[3]) <= timedelta(days=OPENER_DAYS):
                warns.append(f"{a[0]} opens like {b[0]}: \"{' '.join(oa)}\"")

    replies = sorted((x for x in recent if x[2] == "reply"), key=lambda x: x[3])
    for a, b in zip(replies, replies[1:]):
        if (a[5] or b[5]) and b[3] - a[3] < timedelta(minutes=REPLY_GAP_MIN):
            fails.append(f"{a[0]} and {b[0]} are {int((b[3] - a[3]).total_seconds() // 60)} min apart, "
                         f"minimum {REPLY_GAP_MIN}")
    for a in (x for x in replies if x[5]):
        window = [x for x in replies if timedelta(0) <= a[3] - x[3] < timedelta(hours=24)]
        if len(window) > MAX_REPLIES_24H:
            fails.append(f"{a[0]}: {len(window)} replies in the 24 h up to it, maximum {MAX_REPLIES_24H}")
        for n in sorted(figures(a[4])):
            same = [x[0] for x in replies if x is not a and abs(a[3] - x[3]) < timedelta(hours=24) and n in figures(x[4])]
            if same:
                fails.append(f"{a[0]} reuses {n}, also in {same[0]} within 24 h. One reply per figure per day")

    for w in dict.fromkeys(warns):
        print("WARN", w)
    fails = list(dict.fromkeys(fails))
    for f in fails:
        print("FAIL", f)
    print("PASS" if not fails else f"{len(fails)} problem(s). Rewrite, then run again.")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
