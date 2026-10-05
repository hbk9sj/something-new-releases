"""Rewrite .claude/settings.json: allow rules for the nueravix-x routine plus a hook that blocks every Bash command
unless (1) nueravix-x/tools and nueravix-x/Makefile match the SHA-256 manifest embedded here (no extra files, no
__pycache__), (2) no GNUmakefile or makefile sits beside the Makefile, and (3) the allow rules are still exactly
these. Run from the repo root after any change to those files: python3 .claude/make_guard.py"""
import hashlib, json
from pathlib import Path

R = "/home/user/something-new-releases/nueravix-x"
PY = "python3 -I -S -B"
ALLOW = [
    f"Bash(make -f {R}/Makefile -C {R} verify)",
    f"Bash({PY} {R}/tools/buffer.py check)",
    f"Bash({PY} {R}/tools/buffer.py sync)",
    f"Bash({PY} {R}/tools/buffer.py publish {R}/state/drafts/*)",
]

assert not any(p.is_symlink() for p in Path("nueravix-x").rglob("*")), "no symlinks"
files = sorted([p for p in Path("nueravix-x/tools").rglob("*") if p.is_file()] + [Path("nueravix-x/Makefile")],
               key=lambda p: p.as_posix().encode())
assert not any("__pycache__" in p.parts for p in files), "remove __pycache__ first"
manifest = "\n".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.as_posix()}" for p in files)
allow_hash = hashlib.sha256(json.dumps(ALLOW, sort_keys=True).encode()).hexdigest()
read_allow_hash = ("import json, hashlib; s = json.load(open('.claude/settings.json')); "
                   "print(hashlib.sha256(json.dumps(s['permissions']['allow'], sort_keys=True).encode()).hexdigest())")

guard = "; ".join([
    'cd "$CLAUDE_PROJECT_DIR" || exit 2',
    'H=sha256sum; command -v sha256sum >/dev/null 2>&1 || H="shasum -a 256"',
    'got=$(find nueravix-x/tools nueravix-x/Makefile ! -type d | LC_ALL=C sort | while IFS= read -r f; do $H "$f" 2>/dev/null || echo "unreadable  $f"; done)',
    f"want='{manifest}'",
    '[ "$got" = "$want" ] || { echo "blocked: nueravix-x/tools or nueravix-x/Makefile differ from the manifest" >&2; exit 2; }',
    'l=$(find nueravix-x -type l) || { echo "blocked: cannot list nueravix-x" >&2; exit 2; }',
    '[ -z "$l" ] || { echo "blocked: symlink inside nueravix-x" >&2; exit 2; }',
    'e=$(ls -A nueravix-x) || { echo "blocked: cannot list nueravix-x" >&2; exit 2; }',
    '! printf "%s\\n" "$e" | grep -qFx -e GNUmakefile -e makefile || { echo "blocked: unexpected GNUmakefile or makefile in nueravix-x" >&2; exit 2; }',
    f'a=$(python3 -I -S -B -c "{read_allow_hash}" 2>/dev/null)',
    f'[ "$a" = "{allow_hash}" ] || {{ echo "blocked: the allow rules in .claude/settings.json changed" >&2; exit 2; }}',
])
settings = {"permissions": {"allow": ALLOW},
            "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": guard}]}]}}
Path(".claude/settings.json").write_text(json.dumps(settings, indent=2) + "\n")
print(len(files), "files in manifest")
