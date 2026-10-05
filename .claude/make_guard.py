"""Rewrite .claude/settings.json: allow rules for the nueravix-x routine plus a hook that blocks every Bash command
unless nueravix-x/tools and nueravix-x/Makefile match the SHA-256 manifest embedded here (no extra files, no
__pycache__). Run from the repo root after any change to those files: python3 .claude/make_guard.py"""
import hashlib, json
from pathlib import Path
R = "/home/user/something-new-releases/nueravix-x"
PY = "python3 -I -S -B"
files = sorted([p for p in Path("nueravix-x/tools").rglob("*") if p.is_file()] + [Path("nueravix-x/Makefile")],
               key=lambda p: p.as_posix().encode())
assert not any("__pycache__" in p.parts for p in files), "remove __pycache__ first"
manifest = "\n".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.as_posix()}" for p in files)
guard = ('cd "$CLAUDE_PROJECT_DIR" || exit 2; H=sha256sum; command -v sha256sum >/dev/null 2>&1 || H="shasum -a 256"; '
         'got=$(find nueravix-x/tools nueravix-x/Makefile -type f | LC_ALL=C sort | while IFS= read -r f; do $H "$f"; done); '
         f"want='{manifest}'; "
         '[ "$got" = "$want" ] || { echo "blocked: nueravix-x/tools or nueravix-x/Makefile differ from the manifest in .claude/settings.json" >&2; exit 2; }')
s = {"permissions": {"allow": [
        f"Bash(make -C {R} verify)",
        f"Bash({PY} {R}/tools/buffer.py check)",
        f"Bash({PY} {R}/tools/buffer.py sync)",
        f"Bash({PY} {R}/tools/buffer.py publish {R}/state/drafts/*)",
        f"Bash({PY} {R}/tools/push_image.py images/*)"]},
     "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": guard}]}]}}
Path(".claude/settings.json").write_text(json.dumps(s, indent=2) + "\n")
print(len(files), "files in manifest")
