"""Smallest check that review.py's comparison points the right way. Run: python3 tools/tests/test_review.py"""
import random, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import review

now = datetime(2026, 10, 20, tzinfo=timezone.utc)
sent = (now - timedelta(days=3)).isoformat()
hist, metrics = [], {}
for i in range(6):
    for exp, likes in (("baseline", 1), ("short-hook", 6)):
        bid = f"{exp}{i}"
        hist.append({"kind": "original", "status": "sent", "buffer_id": bid, "sentAt": sent, "createdAt": sent,
                     "experiment": exp})
        metrics[bid] = {"reactions": likes, "impressions": 100}
hist.append({"kind": "original", "status": "sent", "buffer_id": "young", "sentAt": now.isoformat(),
             "createdAt": now.isoformat(), "experiment": "short-hook"})
metrics["young"] = {"reactions": 50, "impressions": 50}   # under 48 h old: must be left out

rows = {r["group"]: r for r in review.table(hist, metrics, "experiment", 48, now, random.Random(0))}
assert rows["short-hook"]["posts"] == 6, rows
assert rows["short-hook"]["like_rate"] == 0.06, rows
assert rows["short-hook"]["p_better_than_baseline"] > 0.99, rows
assert rows["baseline"]["p_better_than_baseline"] is None
assert rows["short-hook"]["enough"] and rows["baseline"]["enough"]
print("review tests pass")
