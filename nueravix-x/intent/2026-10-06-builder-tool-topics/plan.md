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

- **The 8 posts already queued (6-13 Oct)** are on the old topics. They stay: the rules forbid editing or deleting
  Buffer posts, and they are the "before" for comparison. The owner may cancel them in Buffer.
- **Images from the cloud run**: `push_image.py` gets HTTP 403 there, so the image arm still waits.
- **Bookmarks are not measurable by the routine.** Buffer's API returns reactions, comments, reposts, impressions,
  clicks and engagement rate, not bookmarks. The weekly review keeps judging on likes, replies and reposts per
  impression; the owner can read bookmarks in X's own analytics.

## How we judge it

- Before: every original so far, 3-27 views, 0 reactions.
- After: originals scheduled from 14 Oct onward. At the review of 26 Oct (about 8 new-topic posts at least 48 h
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
