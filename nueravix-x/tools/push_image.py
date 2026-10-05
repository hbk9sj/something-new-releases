"""Publish one proof image so Buffer can fetch it. The only way a run commits or pushes anything.

usage: python3 tools/push_image.py images/<YYYYMMDD>/<finding_id>.png

Checks the file (PNG, at most 5 MB and 8192 px a side: Buffer's limits for X), commits it alone on the
session's working branch, pushes, and prints its raw.githubusercontent.com URL pinned to the commit, so the
URL stays valid until the post goes out even if the branch moves. Refuses anything staged outside
nueravix-x/images/, and refuses to push bootstrap or main.
"""
import struct, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
RAW = "https://raw.githubusercontent.com/hbk9sj/something-new-releases"
AUTHOR = ["-c", "user.name=Hbk9SJ", "-c", "user.email=64429985+hbk9sj@users.noreply.github.com"]
SAFE = ["-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false"]   # no repo-configured code runs


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *SAFE, *args], check=True, capture_output=True, text=True).stdout.strip()


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    f = (ROOT / sys.argv[1]).resolve()
    if IMAGES not in f.parents or f.suffix != ".png" or not f.is_file():
        raise SystemExit(f"STOP: {sys.argv[1]} must be an existing .png under {IMAGES}")
    head = f.read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("STOP: not a PNG file")
    w, h = struct.unpack(">II", head[16:24])
    if f.stat().st_size > 5 * 1024 * 1024 or max(w, h) > 8192:
        raise SystemExit(f"STOP: {f.stat().st_size} bytes, {w}x{h} px; limits 5 MB and 8192 px")
    branch = git("branch", "--show-current")
    if branch in ("", "bootstrap", "main"):
        raise SystemExit(f"STOP: on {branch or 'a detached HEAD'}; push only from the session's working branch")
    top = Path(git("rev-parse", "--show-toplevel")).resolve()
    git("add", "--", str(f))
    staged = git("diff", "--cached", "--name-only").splitlines()
    outside = [p for p in staged if not p.startswith("nueravix-x/images/")]
    if outside:
        raise SystemExit(f"STOP: staged files outside nueravix-x/images/: {outside}. Nothing committed")
    rel = f.relative_to(top).as_posix()
    git(*AUTHOR, "commit", "-q", "--no-verify", "-m", f"nueravix-x: proof image {f.name}")
    git("push", "-q", "-u", "origin", f"HEAD:refs/heads/{branch}")
    url = f"{RAW}/{git('rev-parse', 'HEAD')}/{rel}"
    for _ in range(12):   # the raw host can lag a push by a few seconds
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                if r.status == 200 and r.headers.get("Content-Type") == "image/png":
                    print(url)
                    return
        except Exception:
            pass
        time.sleep(10)
    raise SystemExit(f"STOP: pushed, but {url} did not return image/png within 2 minutes")


if __name__ == "__main__":
    main()
