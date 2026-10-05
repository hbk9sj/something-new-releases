"""The only way this repo talks to Buffer. One account, one X channel, checked on every call.

usage:
  python3 tools/buffer.py check                  # channel exists, right X account, connected, not locked
  python3 tools/buffer.py sync                   # pull every post on the channel into state/, with metrics
  python3 tools/buffer.py publish DRAFTS.json    # schedule drafts that pass the checker (see publish())

Auth: in the x-posting cloud environment the agent proxy adds the key for api.buffer.com, so no header is
sent. Elsewhere, set BUFFER_ACCESS_TOKEN. The key is never printed, logged or written to a file.
"""
import json, os, subprocess, sys, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HISTORY, METRICS = ROOT / "state/history.json", ROOT / "state/metrics.jsonl"
API = "https://api.buffer.com"
ORG = "6ab1784f47f0a36852f56465"
X_USER_ID = "2095836372565434368"   # @nueraviX; Buffer calls it serviceId
MAX_SCHEDULED = 10                  # Buffer free plan: 10 scheduled posts per channel
POST_FIELDS = ("id text status dueAt sentAt externalLink error { message } metricsUpdatedAt "
               "metrics { type value }")


class Unknown(Exception):
    """The request may or may not have reached Buffer."""


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def gql(query, variables=None):
    req = urllib.request.Request(API, json.dumps({"query": query, "variables": variables or {}}).encode(),
                                 {"Content-Type": "application/json"})
    if os.environ.get("BUFFER_ACCESS_TOKEN"):
        req.add_header("Authorization", "Bearer " + os.environ["BUFFER_ACCESS_TOKEN"])
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:   # the server answered: nothing ambiguous about it
        raise SystemExit(f"Buffer HTTP {e.code}: {e.read()[:300].decode(errors='replace')}")
    except Exception as e:                # timeout, reset: the request may have landed
        raise Unknown(type(e).__name__)
    if out.get("errors"):
        raise SystemExit("Buffer GraphQL error: " + "; ".join(x.get("message", "?") for x in out["errors"]))
    return out["data"]


def channel():
    chans = gql("query($o:OrganizationId!){channels(input:{organizationId:$o})"
                "{id name service serviceId isDisconnected isLocked}}", {"o": ORG})["channels"]
    mine = [c for c in chans if c["service"] == "twitter" and str(c["serviceId"]) == X_USER_ID]
    if len(mine) != 1:
        raise SystemExit(f"STOP: expected exactly one X channel with serviceId {X_USER_ID}, found {len(mine)}")
    c = mine[0]
    if c["isDisconnected"] or c["isLocked"]:
        raise SystemExit(f"STOP: channel {c['name']} is disconnected or locked")
    return c["id"]


def posts(cid, status=None):
    out, after = [], None
    flt = {"channelIds": [cid], **({"status": status} if status else {})}
    while True:
        d = gql("query($o:OrganizationId!,$f:PostsFiltersInput,$a:String){posts(first:50,after:$a,"
                "input:{organizationId:$o,filter:$f}){edges{node{" + POST_FIELDS + "}}pageInfo{hasNextPage endCursor}}}",
                {"o": ORG, "f": flt, "a": after})["posts"]
        out += [e["node"] for e in d["edges"] or []]
        if not d["pageInfo"]["hasNextPage"]:
            return out
        after = d["pageInfo"]["endCursor"]


def load():
    return json.loads(HISTORY.read_text())


def save(hist):
    HISTORY.write_text(json.dumps(hist, indent=1, ensure_ascii=False) + "\n")


def sync():
    """Match Buffer's posts to history by id, or by text for entries whose create outcome was unknown."""
    cid = channel()
    remote = posts(cid)
    by_id = {p["id"]: p for p in remote}
    by_text = {p["text"]: p for p in remote}
    hist, snaps = load(), []
    for h in hist:
        if h.get("status") in ("intent", "unknown") and h["text"] in by_text:
            h["buffer_id"] = by_text[h["text"]]["id"]
        p = by_id.get(h.get("buffer_id"))
        if not p:
            continue
        h["status"] = p["status"]
        for k in ("dueAt", "sentAt", "externalLink"):
            if p.get(k):
                h[k] = p[k]
        if p["status"] == "sent" and p.get("sentAt"):
            h["createdAt"] = p["sentAt"]
        if p.get("error"):
            h["error"] = p["error"]["message"]
        if p.get("metrics") and p["status"] == "sent":   # unsent posts report all zeros
            snaps.append({"at": now(), "buffer_id": p["id"], "finding_id": h.get("finding_id"),
                          "sentAt": p.get("sentAt"), "metricsUpdatedAt": p.get("metricsUpdatedAt"),
                          "source": "buffer", **{m["type"]: m["value"] for m in p["metrics"]}})
    known = {h.get("buffer_id") for h in hist}
    stray = [p["id"] for p in remote if p["id"] not in known]
    save(hist)
    with METRICS.open("a") as f:
        for s in snaps:
            f.write(json.dumps(s) + "\n")
    unresolved = [h["finding_id"] for h in hist if h.get("status") in ("intent", "unknown")]
    print(json.dumps({"channel": cid, "buffer_posts": len(remote), "scheduled": sum(p["status"] == "scheduled" for p in remote),
                      "metric_snapshots": len(snaps), "not_in_history": stray, "unresolved": unresolved}, indent=1))
    return cid, remote, unresolved


def publish(path):
    """Schedule each draft once. Order: checker -> sync -> room check -> write intent -> create -> record."""
    chk = subprocess.run([sys.executable, str(ROOT / "tools/check_x_draft.py"), path, str(HISTORY)])
    if chk.returncode:
        raise SystemExit("STOP: checker did not pass")
    cid, remote, unresolved = sync()
    if unresolved:
        raise SystemExit(f"STOP: earlier creates with unknown outcome {unresolved}. Check Buffer by hand; never resend")
    room = MAX_SCHEDULED - sum(p["status"] == "scheduled" for p in remote)
    texts = {p["text"] for p in remote}
    for d in json.loads(Path(path).read_text())["drafts"]:
        if d["kind"] != "original":
            print(f"skip {d['id']}: replies are posted in Chrome, not Buffer")
            continue
        if d["parts"][0] in texts:
            print(f"skip {d['id']}: already in Buffer")
            continue
        if room <= 0:
            print(f"skip {d['id']}: queue full ({MAX_SCHEDULED})")
            continue
        hist = load()
        entry = {"id": d["id"], "finding_id": d["finding_id"], "kind": "original", "text": d["parts"][0],
                 "parts": d["parts"], "createdAt": d["time"], "status": "intent", "intent_at": now(),
                 **{k: d[k] for k in ("experiment", "topic", "format", "measurement", "image") if k in d}}
        hist.append(entry)
        save(hist)   # the intent is on disk before the request leaves
        inp = {"channelId": cid, "text": d["parts"][0], "schedulingType": "automatic",
               "mode": "customScheduled", "dueAt": d["time"]}
        assets = ([{"image": {"url": d["image"]["url"], "metadata": {"altText": d["image"]["alt"]}}}]
                  if d.get("image") else [])
        inp["assets"] = assets
        if len(d["parts"]) > 1:   # Buffer: every part, post 1 included, goes in the thread list
            inp["metadata"] = {"twitter": {"thread": [{"text": p, "assets": assets if i == 0 else []}
                                                      for i, p in enumerate(d["parts"])]}}
        try:
            r = gql("mutation($i:CreatePostInput!){createPost(input:$i){... on PostActionSuccess{post{id status dueAt "
                    "assets{source}}}... on MutationError{message}}}", {"i": inp})["createPost"]
        except Unknown as e:
            entry["status"] = "unknown"
            save(hist)
            raise SystemExit(f"STOP: create for {d['id']} ended without an answer ({e}). Run sync later; never resend")
        if "post" in r:
            entry.update(status=r["post"]["status"], buffer_id=r["post"]["id"], dueAt=r["post"]["dueAt"])
            room -= 1
            print(f"scheduled {d['id']} -> {r['post']['id']} at {r['post']['dueAt']}, "
                  f"{len(r['post'].get('assets') or [])} image(s) attached (expected {len(assets)})")
        else:
            entry.update(status="rejected", error=r.get("message"))
            print(f"rejected {d['id']}: {r.get('message')}")
        save(hist)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        print(channel())
    elif cmd == "sync":
        sync()
    elif cmd == "publish" and len(sys.argv) > 2:
        publish(sys.argv[2])
    else:
        raise SystemExit(__doc__)
