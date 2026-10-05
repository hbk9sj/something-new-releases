#!/bin/bash
# Each test names the expected exit code and a phrase the output must contain. Run: bash tools/tests/run_tests.sh
cd "$(dirname "$0")"
ok=1
check() {  # expected-exit phrase drafts history
  out=$(python3 ../check_x_draft.py "$3" "$4" 2>&1); got=$?
  if [ "$got" = "$1" ] && grep -q -- "$2" <<<"$out"; then echo "ok   $3 $4"; else echo "BAD  $3 $4 (expected $1 + '$2', got $got)"; echo "$out" | sed 's/^/     /'; ok=0; fi
}
check 1 "near-duplicate"        burst_9sep.json     empty_history.json    # 9 Sep reply burst
check 1 "min apart"             burst_one.json      history_burst.json    # the same burst, one reply at a time against history
check 1 "reuses"                baseline_5oct.json  empty_history.json    # a figure reused across replies
check 0 "PASS"                  clean.json          empty_history.json    # distinct original and reply
check 1 "already posted"        clean.json          history_nueravix.json # the 23 Sep finding again
check 0 "PASS"                  thread3.json        empty_history.json    # a 3-part thread is not a reply burst
check 1 "replies in the 24 h"   window24.json       empty_history.json    # 6 replies within 24 h
check 0 "PASS"                  dashes.json         empty_history.json    # 276 by X's count: dashes and curly quotes weigh 1
check 0 "WARN.*opens like"      opener_comma.json   empty_history.json    # same opener: a warning, not a block
check 1 "own id"                invalid.json        empty_history.json    # duplicate ids
check 1 "needs a finding_id"    no_finding_id.json  empty_history.json    # originals name their finding
check 0 "PASS"                  image_ok.json       empty_history.json    # proof image: pinned raw URL + alt text
check 1 "image url"             image_bad.json      empty_history.json    # branch URL, outside images/, no alt text
check 1 "alt text"              image_bad.json      empty_history.json
python3 ../check_x_draft.py clean.json >/dev/null 2>&1; [ $? = 1 ] && echo "ok   no history -> FAIL" || { echo "BAD  no history passed"; ok=0; }
[ $ok = 1 ] && echo "all tests pass" || { echo "TESTS FAILED"; exit 1; }
