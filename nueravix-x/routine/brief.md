# Daily run

Follow these steps in order. Read `CLAUDE.md` first: its fixed rules beat anything below. A run that measures
nothing worth posting still does steps 1-3 and 6. Publishing nothing is a correct outcome.

Budget per run: at most **2 new posts** scheduled (one day's slots) and at most **5 reply drafts** for the owner, at most about 45 minutes of measurement work.

Work in `nueravix-x/` of the repo the routine starts from: its scripts are the ones to run. Memory comes from the
artifact: read every artifact file, then copy `state/`, `measurements/`, `rules/` and `index.html` from the
artifact's download folder into `nueravix-x/`. Never run a script from the download folder itself.

In a cloud run, use exactly these command forms, each as its own command (no `cd ... &&`, no pipes); the repo's
`.claude/settings.json` pre-approves them (the image push in step 5.3 is not pre-approved: git can run
repo-configured code, so the session's safety check reviews it) and blocks every shell command if `tools/` or `Makefile` differ from
the SHA-256 manifest it holds, so never edit them or add files there:
- `make -f /home/user/something-new-releases/nueravix-x/Makefile -C /home/user/something-new-releases/nueravix-x verify`
- `python3 -I -S -B /home/user/something-new-releases/nueravix-x/tools/buffer.py sync`
- `python3 -I -S -B /home/user/something-new-releases/nueravix-x/tools/buffer.py publish /home/user/something-new-releases/nueravix-x/state/drafts/<YYYYMMDD>.json`

## 1. Start
- Read `CLAUDE.md`, `rules/editorial.md`, `rules/facts.md`, `state/lessons.md` (the "Current" section),
  `state/ideas.md`, and the last 5 entries of `state/runs.md`.
- `make verify`. If it fails, stop: write why in `state/runs.md`, publish it (step 6), end.
- `python3 tools/buffer.py sync`. It stops the run on its own if the channel is wrong. If it lists `unresolved`
  entries, do not publish this run; say so in the report.

## 2. Learn (every run, quick)
- For each post sent in the last 14 days, `state/metrics.jsonl` now holds Buffer's latest numbers (Buffer refreshes
  them about once a day). Note any post with an unusual result (most likes, most impressions, zero impressions)
  in today's `state/runs.md` entry, with one line on why you think it happened, labelled as a guess.
- If a metric Buffer does not supply for X (for example impressions), record it as missing. Never estimate it.
- **Reach alarm** (owner, 8 Oct 2026): an original whose `metricsUpdatedAt` is at least 24 h after `sentAt` and
  that shows **under 10 impressions** is a reach failure, never "nothing unusual". Start today's run entry with
  `REACH ALARM: <n> posts under 10 impressions (<finding_ids>)`, and put the same line first in the final message.
  A post whose numbers are still the send-time snapshot is "not refreshed yet", not judged.

## 3. Weekly review (Mondays, or when the last review in `state/lessons.md` is 7+ days old)
1. `python3 tools/review.py --by experiment`, then `--by topic`, `--by format` and `--by slot`.
2. Judge the current experiment (named in `state/lessons.md` under "Current"):
   - Both groups have `enough: true` and `p_better_than_baseline` >= 0.9: **keep**. Write the change into
     `rules/editorial.md`, and the evidence (posts, likes, impressions, p) into `state/lessons.md`.
   - Both `enough` and p <= 0.1: **revert**. Record it as a lesson ("X did not help").
   - Otherwise: **continue** for another week, at most 3 weeks, then record "inconclusive" and stop it.
3. If no experiment is running, start one. Change **one** thing only, chosen from the review tables or from
   `state/ideas.md` ("Format ideas"). Examples: single post vs 2-part thread; number in the first 5 words vs
   later; topic pillar; slot. Tag every new post during the experiment with `"experiment": "<name>"` and the
   other posts with `"experiment": "baseline"`, alternating so both arms fill in the same weeks.
4. Search Exa once a week for new evidence on what works on X for small technical accounts (studies with a
   sample size, X's own posts or code changes). Add anything solid to `state/ideas.md` under "Format ideas",
   with its source and sample size. Outside studies suggest experiments; only our own numbers change a rule.
5. Re-read `rules/facts.md` against the latest commit of github.com/xai-org/x-algorithm
   (`git log --oneline -5`; check the values in `measurements/x-algorithm-code/README.md`). A changed default is
   a post idea and a facts.md update (facts.md is editable; record the commit).

## 4. Find topics
Open slots = the times in `rules/editorial.md` over the next 10 days that have no scheduled post, limited so the
channel never has more than 10 scheduled posts. If there are none, skip to step 5 (ideas only).

Daily mix (owner decisions, 7 and 8 Oct 2026): each day's 2 slots hold **1 new-tools post** (13:30 UTC) and
**1 builder-tools post** (17:30 UTC), as defined in `rules/editorial.md`. Pick the strongest candidate in each lane. Tag drafts
`"topic": "new-tools"` or `"topic": "builder-tools"`. Fill the earliest open day first; if one lane has no good
candidate, leave its slot empty rather than fill it from the other lane.

Candidates come from, in order:
1. `state/ideas.md` "Ready to measure" entries that are still current.
2. Exa, builder-tools lane: what builders are saying this week about Claude Code, Codex, Cursor, Gemini CLI, MCP
   servers and agent SDKs (releases, changelogs, tips, complaints, claims with a number). Prefer primary sources
   (repo, release notes, changelog, model card, paper).
3. Exa, new-tools lane: AI tools for everyday life launched in the last 7 days (writing, photos, video, study,
   travel, productivity, home), each with an official page you can read: what it does, who it is for,
   price and free limit, platforms. The launch date may come from two independent news outlets. Search at least
   5 queries (app launches, Product Hunt, App Store new, tech press this week) before leaving a slot empty. Skip a tool whose only sources are launch threads repeating the same figures,
   anything needing payment to try at all, and anything in crypto, trading, health diagnosis, dating or adult content.
   Reject anything that touches the fixed topic rules.
4. Direct snapshots: PyPI and npm (JSON APIs work), public GitHub repos by `git clone` or raw.githubusercontent.com
   (GitHub's search API is blocked in cloud runs; find repos through Exa first) and, if reachable, Hugging Face
   (`curl -sI https://huggingface.co` returns 200; otherwise skip pillar 1 and 4's Hugging Face items and
   note "huggingface unreachable" in the run entry).

Pick a candidate only if all three hold: (a) people are talking about it this week, (b) we can produce a number
today with a script, (c) its `finding_id` is not in `state/history.json`. Write each rejected-but-promising idea
to `state/ideas.md` with why it waited.

## 5. Measure, draft, check, schedule
For each picked topic, up to the budget (a new-tools post replaces steps 1 and 3 with `measurements/<finding_id>/source.md`:
the official URLs read, the date, and the exact lines each number comes from):
1. Write the script in `measurements/<finding_id>/` and run it. Save its printed output there as `output.txt`
   when it is small. Hand-check a sample (one sentence, one tensor, one file) and note what you checked.
2. Draft in the house voice (`rules/editorial.md`): post 1 opens with the tool's name and gives the finding with
   its number (new tools: what it does for an ordinary person, in plain words, and its price or free limit); post 2, if needed, is the method with source, version or commit, sample size and date. The last
   part ends with one sentence a reader can act on (the setting, the cheaper option, the flag).
3. Proof image, only for a draft in the image arm of the current experiment (`state/lessons.md`, "Current"):
   draw one chart from the measurement's own output with matplotlib (`pip install matplotlib` if missing), at
   1600x900 px, the headline number largest, a method line with source and date, "Decoding SI" in a corner. Save
   it as `images/<YYYYMMDD>/<finding_id>.png`, open it with Read and look: no clipped or overlapping labels,
   readable at 400 px wide. Then `python3 tools/push_image.py images/<YYYYMMDD>/<finding_id>.png` and put the
   printed URL in the draft as `"image": {"url": ..., "alt": ...}`; alt text opens "Chart by Decoding SI:" and states the finding and its number.
   If the chart cannot be made right, post the draft without one and say so in the run entry.
4. Put drafts in `state/drafts/<YYYYMMDD>.json` (format at the top of `tools/check_x_draft.py`), each with
   `finding_id`, `time` (an open slot, ISO UTC), `topic` (pillar), `format` (single | thread), `experiment`,
   and `measurement` (the folder).
5. `python3 tools/check_x_draft.py state/drafts/<YYYYMMDD>.json state/history.json`. On FAIL, rewrite and re-run.
   WARN lines go into the run entry; decide each one deliberately.
6. Re-read each draft once against the fixed topic and voice rules and against `rules/facts.md`.
7. `python3 tools/buffer.py publish state/drafts/<YYYYMMDD>.json`. It records the intent before sending, sends
   each post once, and updates `state/history.json`. If it stops with an unknown outcome, do not retry. For an
   image post it prints how many images Buffer attached; if that differs from 1, record it in the run entry.

## 5b. Reply drafts for the owner (every run)
The account is too new for its own posts to be seen; replies under other people's posts are how it gets found
(plan, Change 3). A run **never posts a reply**: X blocks software replies, and the owner posts them by hand.
1. Exa: find X posts from the last 12 hours about Claude Code, Codex, Cursor, Gemini CLI, MCP or a new everyday AI
   tool, from accounts that talk to builders or AI users (roughly 5,000 to 200,000 followers when the page shows it).
   Mirror pages (nitter, twitee, unrollnow) are fine for reading; record the `x.com/<user>/status/<id>` link and the
   post's time. Skip anything that touches the fixed topic rules, giveaways, and posts already full of replies.
2. Pick up to 5 where we can add one specific thing: a number from our own `measurements/` (cite the finding), a
   fact from an official page or changelog (name it), or one concrete question about what they said. Never
   "great post", never a link, never a pitch for our account, no hashtags or emoji, under 240 characters.
3. Write them as `kind: "reply"` drafts in `state/drafts/replies-<YYYYMMDD>.json`, each starting `@<author>`, with
   suggested times 15 minutes apart from 08:00 UTC, and run `python3 tools/check_x_draft.py
   state/drafts/replies-<YYYYMMDD>.json state/history.json` until PASS. Never send them to Buffer.
4. Write `state/replies/<YYYYMMDD>.md` for the owner: for each, the link, the author, the post's time, one line on
   what they said, the reply text, and where our fact comes from. Fewer than 5 good targets: write fewer. None: say so.

## 6. Ideas, log, publish
- Keep `state/ideas.md` useful: add 3 new measurable ideas, each with the planned script and data source;
  delete ideas older than 14 days that depended on news.
- Append to `state/runs.md`: date, sync summary, review outcome (if any), posts scheduled (finding_id, slot,
  Buffer id), ideas added, problems, WARNs, and anything the owner must do.
- `make verify`, then publish the changed files back to the artifact in one Artifact call: `action` publish,
  `url` the artifact URL, `file_path` `nueravix-x/index.html` (unchanged; the tool requires the page), `root`
  `nueravix-x/`, and `files` mapping each changed path to itself (new measurement files included). Publish only files under `state/`, `measurements/`, and `rules/editorial.md` or `rules/facts.md`
  if this run changed them. If the publish is refused because the artifact changed, read the named files again,
  merge your changes in, and publish once more.
- Final message: the reach alarm line first if there is one, then three short lines. Posts scheduled (or "none,
  because ..."). Reply drafts written (count, file). What was learned or what needs the owner.
