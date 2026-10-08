# Measure the tools builders use every day

Asked for by the owner, 6 Oct 2026: "lets plan for that" (content that actually spreads), then "go ahead and fix,
and also give me the whole plan, i will review with hermes too". Accepted as intent and plan in one step, as with
`2026-10-05-repo-tools-proof-images`.

## Problem

Every post reaches the same small test audience and stops there. X's public counts on 6 Oct 2026:

| Post | Type | Views | Likes, replies, reposts |
|---|---|---|---|
| 13 Sep, lm-eval revision pins | original | 27 | 0 |
| 5 Oct, @modelcontextprotocol/sdk size (with chart) | original | 22 (Buffer: 20) | 0 |
| 6 Oct 13:30 UTC, X new-author boost limits | original | 3 after 2 hours | 0 |
| 12 Sep, reply under a large account | reply | 7 | 0 |
| 13 Sep and 8 Sep, replies | reply | 3 each | 0 |
| 23 Sep, two-part MCP thread | original | gone (X returns "not found"; owner to confirm whether deleted) | n/a |

The account has 0 followers, is about 4 weeks old, and its Premium check is "Under review" after the rename. A
0-follower account gets a small test audience per post; with no reaction the post stops there. Account size is not
the whole story, though (next section).

## Evidence

**Our own sample.** Apify search (data-slayer/twitter-search), 6 Oct 2026: English posts since 6 Sep with 300+
likes, not replies, matching Claude Code, Codex, MCP, LLM, open-source model, tokenizer, Hugging Face or benchmark.
100 posts.
- 28 of the 100 came from accounts under 5,000 followers; their median was 68,103 views. Several came from
  accounts under 1,000 followers (83, 154, 551, 712 followers) at 72k to 418k views.
- Topic: 39 mention Claude Code, 33 Codex, 21 MCP, 20 open models or Hugging Face, 15 benchmarks. **Biased**: the
  query contained these words, so the counts show what wins among them, not across all of AI.
- In 15 of the 28 small-account posts, bookmarks exceeded likes: tips, checklists, "do this instead",
  ranked lists, timestamped guides to a long video.
- 57 of 100 have a number in the first 120 characters; median length 290 characters; 3 of 100 end with a question.
- Media type could not be read reliably from this actor's output (every row came back "text"), so this sample
  says nothing about images or video.

**Outside studies** (correlation only, used to choose what to try, not as rules):
- PromptsLove, 21,864 AI posts, Jan-Aug 2026, split by follower count. Under 25K followers: naming a specific tool
  in the opening line +27.9% median likes (n=2,471); screen-recorded demonstration +58.2% likes and +290%
  bookmarks (n=201; the like result did not hold under a broader label); real outside links -32.7% likes;
  hashtags -35% likes and -76% bookmarks (n=529); carousels -17%. Builder posts collect far more bookmarks per
  like than mass-audience posts (845 vs 218 median bookmarks).
- Doomers, 592 AI launches: accounts with 1K-10K followers had a higher median (258,841 views) than accounts over
  1M (102,955). 17% of launches from accounts under 10K passed a million views.
- Ordinal, 87,528 posts: threads 1.89% engagement vs 0.67% for single text posts.

**X's ranking code** (xai-org/x-algorithm, b412112): a post is scored on each viewer's predicted actions; copying
the link weighs 20, a reply 5, a like 0.5. Hashtags carry no boost and a "hashtag abuse" spam label exists. A post
is understood from its own text, so a clear tool name in the words is what places it.

**X's API rules**: since 23 Feb 2026 software may reply only when the other author mentioned or quoted us
(X API changelog, quoted by four sources). Replies must be posted by a person.

## What changes

1. **Topic mix** (`rules/editorial.md`, artifact). New pillar 0, *Builder tools*: Claude Code, Codex, Cursor, Gemini
   CLI, MCP servers, agent SDKs: anything a developer opens every day. At least 3 of every 4 new originals come
   from it. The old pillars (model files, X's algorithm, ecosystem counts) share the remaining quarter.
2. **Open with the tool's name.** The first words of post 1 name the tool (Claude Code, an MCP server's name), not
   the category ("AI agents").
3. **End with what to do.** Post 1 (or post 2 of a thread) closes with one sentence a reader can act on: the
   setting, the cheaper option, the flag. A number without a use is the post nobody saves.
4. **Daily brief, step 4** (`routine/brief.md`, repo): topic search starts from what builders are discussing about
   those tools this week, and the 3-in-4 rule is checked before drafting.
5. **Replies stay manual.** After the Premium check clears, the owner posts 3-5 replies a day under builder-tool
   posts. Drafting them in the routine is a separate later change, not part of this one.

Unchanged: the measurement identity (every number comes from a script we ran), the fixed safety rules, no
hashtags, no links in post 1, the slots, the `proof-image` experiment (both arms follow the new topic mix, so the
image is still the only difference between them).

## What this does not fix

- ~~The 8 posts already queued stay~~. **Changed 6 Oct, owner:** "delete the queue posts, and lets start from now
  only". All 8 (7-13 Oct) were deleted in Buffer by hand and marked `"status": "deleted"` in history; the checker
  now skips deleted posts (PR #12). The "before" for comparison is every earlier original (3-27 views each).
- **Images from the cloud run**: `push_image.py` gets HTTP 403 there, so the image arm still waits.
- **Bookmarks are not measurable by the routine.** Buffer's API returns reactions, comments, reposts, impressions,
  clicks and engagement rate, not bookmarks. The weekly review keeps judging on likes, replies and reposts per
  impression; the owner can read bookmarks in X's own analytics.

## How we judge it

- Before: every original up to 6 Oct, 3-27 views, 0 reactions.
- After: originals scheduled from 7 Oct onward. At the review of 19 Oct (about 8 new-topic posts at least 48 h
  old): median impressions and reactions per impression, new topic mix vs the 6-13 Oct posts.
- Keep if the median impressions at least double, or any post earns a reply or a follow. Otherwise record it as
  "did not help" in `state/lessons.md` and try the next idea (tool name first is already in; next is a 2-part
  thread with the takeaway in part 2).

## Risks

- The topic counts are biased by the search words; the real reason small accounts win may be usefulness, not the
  tool names. That is why rule 3 (end with what to do) ships alongside rule 1.
- Builder-tool news moves fast and is crowded; a measurement takes hours, so we will often be second. The angle
  is the measured number nobody else posted, not speed.
- Two changes at once (topic and closing line) cannot be separated in the results. Accepted: the goal now is to get
  off zero, not to attribute.

## Checks

- `make verify` passes.
- The next routine run (7 Oct 03:00 UTC) reads the new rules: its run entry should name pillar 0 for any post it
  schedules, or say why none qualified.

## Change 2 (7 Oct 2026, owner): four a day, two lanes

Owner: "two daily new tools and 2 dev tools ... do it right now, delete all other scheduled". The owner chose this
over "we tried it" (hands-on testing by the owner) and over developer tools alone, knowing the trade-off below.

- **Mix**: each day 2 *new-tools* posts (AI tools for everyday life, launched in the last 7 days) and 2
  *builder-tools* posts, alternating, in 4 daily slots (`rules/editorial.md`). Budget per run: 4 posts.
- **Numbers in the new-tools lane** come from the tool's official page, app listing or repo, attributed in the post
  ("its pricing page lists ..."), with the source saved in `measurements/<finding_id>/source.md`. Never "we tested".
  The fixed Numbers rule in `CLAUDE.md` carries this exception.
- **Queue**: the 2 builder-tools posts scheduled for 7 Oct were deleted by hand at the owner's request.
- **Evidence and trade-off**: everyday-user AI posts collect about 3x the likes of builder posts but a quarter of the
  bookmarks (PromptsLove, 21,864 posts); "new AI tool" posts are the most crowded and most AI-written corner of X
  (Originality.ai, July 2026: about 80% likely AI in tech and AI), and many launch waves are paid and repeated word for
  word (Lenk, 21 Sep 2026). The routine cannot try consumer apps (no logins, no phone), so these posts are read, not
  measured. Risk: they look like everyone else's. The 19 Oct review compares the two lanes on impressions and reactions
  per impression; a lane that trails clearly is dropped.

## Change 3 (8 Oct 2026, owner): reach first, replies drafted for the owner

Owner, 8 Oct: "we are not getting any views or engagements ... search web exa and fix all gaps", after the
recommendation below. Supersedes the "four a day" part of Change 2; the two lanes stay.

**Problem.** 9 originals sent 5-8 Oct. Buffer, 8 Oct 03:04 UTC: 24, 5 and 2 impressions on the posts old enough to
count, 0 reactions on all. The 8 Oct run logged this as "nothing unusual". X search returns none of our posts
(Apify `from:decodingsi`, 0 rows; control account 5 rows; 7 Oct). The weekly review cannot learn from zero reactions.

**Evidence** (Exa, 8 Oct 2026; outside reports, correlation or anecdote unless stated):
- Accounts that grew from near zero got most early reach from replies under bigger accounts, with 2-3 originals a
  day on the side: 0 to 560K impressions in 10 days, about 80% from replies (Indie Hackers, Apr 2026); 857 to 1,400
  followers with 15-25 replies a day (bookmark.build, Apr 2026); 35 replies, 7,847 impressions, 2 of them half the
  total (rakeshreddy.dev, Jan 2026, raw data).
- Quality beats volume: 5-8 specific, early replies a day (reachmore.co, May 2026); 8-12 a day at the start
  (xpert.so). Generic replies are filtered; X removed about 42,000 chatbot reply accounts in July 2026 (Nikita Bier,
  quoted by futuretweets.com, 6 Oct 2026).
- X blocks programmatic replies unless the author mentioned or quoted us (since 23 Feb 2026). Replies must be posted
  by a person.
- New accounts: 1-3 posts a day for the first two weeks (opentweet.io, Feb 2026). Search limits usually lift in 2-7
  days once the trigger stops (notpeople.ai, ~2,000 test accounts; ipme.co).
- Scheduling through an authorised app carries no ranking penalty in X's published code (sent2x.com, futuretweets.com).
- Premium (the account now has the blue check) ranks the account's replies higher in conversations (fireply.ai,
  conbersa.ai). It does not lift its originals much.

**What changes**
1. **Two originals a day**, 13:30 UTC new tool, 17:30 UTC builder tool (`rules/editorial.md`, `routine/brief.md`).
2. **Reply drafts for the owner.** Each run writes up to 5 reply drafts under fresh X posts from accounts in the
   niche, in `state/replies/<YYYYMMDD>.md`, checked by `tools/check_x_draft.py` (its house limits: 5 a day, 10 min
   apart, no near-copies, one figure per day). The owner reads, edits and posts them by hand. A run never posts,
   likes or follows. Added to the fixed rules in `CLAUDE.md`.
3. **Reach alarm.** Step 2 flags any original under 10 impressions once Buffer's numbers are at least 24 h past
   sending, and puts it first in the run entry and the final message. "Nothing unusual" is not allowed for it.

**Limit.** The run starts at 03:00 UTC, so a target post is 5-17 h old when the owner reads the drafts. Reports say
posts now peak 6-24 h in (bookmark.build), so this is workable but not the 15-minute window most guides advise.

**How we judge it** (19 Oct review, unchanged date): impressions on originals sent from 9 Oct vs the 5-8 Oct posts;
whether `from:decodingsi` returns our posts; the owner's count of replies posted and followers gained (X's own
analytics; the routine cannot read them).
