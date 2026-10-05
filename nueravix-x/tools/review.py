"""Weekly numbers for the self-improvement review. Reads state/history.json and state/metrics.jsonl.

usage: python3 tools/review.py [--by experiment|topic|format|slot] [--min-age-hours 48]

For each group: posts with metrics, impressions (median), likes (sum), like rate (sum of likes / sum of
impressions), and P(better than baseline): the chance the group's true like rate beats the "baseline" group,
from Beta(1 + likes, 1 + impressions - likes) draws. A group with fewer than MIN_POSTS posts is reported but
marked "too few"; no rule may change on it.
"""
import json, random, statistics, sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_POSTS, DRAWS = 6, 20000


def latest_metrics(path):
    out = {}
    for line in path.read_text().splitlines():
        if line.strip():
            m = json.loads(line)
            out[m["buffer_id"]] = m   # file is append-only, so the last line per post is the newest
    return out


def slot(h):
    t = datetime.fromisoformat(h["createdAt"].replace("Z", "+00:00"))
    return f"{t:%a} {t:%H:%M}Z"


def p_better(a, b, rng):
    """P(rate A > rate B) under independent Beta posteriors; a and b are (likes, impressions)."""
    win = 0
    for _ in range(DRAWS):
        x = rng.betavariate(1 + a[0], 1 + max(a[1] - a[0], 0))
        y = rng.betavariate(1 + b[0], 1 + max(b[1] - b[0], 0))
        win += x > y
    return win / DRAWS


def table(hist, metrics, by, min_age, now, rng):
    groups = defaultdict(list)
    for h in hist:
        m = metrics.get(h.get("buffer_id"))
        if h.get("kind") != "original" or h.get("status") != "sent" or not m or not h.get("sentAt"):
            continue
        if now - datetime.fromisoformat(h["sentAt"].replace("Z", "+00:00")) < timedelta(hours=min_age):
            continue
        key = slot(h) if by == "slot" else h.get(by, "unknown")
        groups[key].append((m.get("reactions", 0), m.get("impressions", 0)))
    totals = {k: (sum(x[0] for x in v), sum(x[1] for x in v)) for k, v in groups.items()}
    base = totals.get("baseline") if by == "experiment" else None
    rows = []
    for k, v in sorted(groups.items()):
        likes, imps = totals[k]
        rows.append({"group": k, "posts": len(v), "median_impressions": statistics.median(x[1] for x in v),
                     "likes": likes, "like_rate": round(likes / imps, 4) if imps else None,
                     "p_better_than_baseline": round(p_better(totals[k], base, rng), 3) if base and k != "baseline" else None,
                     "enough": len(v) >= MIN_POSTS})
    return rows


def main(argv):
    by = argv[argv.index("--by") + 1] if "--by" in argv else "experiment"
    min_age = float(argv[argv.index("--min-age-hours") + 1]) if "--min-age-hours" in argv else 48
    hist = json.loads((ROOT / "state/history.json").read_text())
    rows = table(hist, latest_metrics(ROOT / "state/metrics.jsonl"), by, min_age, datetime.now(timezone.utc),
                 random.Random(0))
    print(json.dumps(rows, indent=1) if rows else "no sent originals with metrics yet")


if __name__ == "__main__":
    main(sys.argv[1:])
