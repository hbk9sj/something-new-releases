# Repo-hosted tools and proof images for @nueraviX

Asked for by the owner, 5 Oct 2026: "go ahead and do it, fix both" (accepted as the intent and this plan).

## Problem
1. The daily routine (trig_013Qo3dtwovuMzMuxNTpaKwN) downloads its scripts from the private artifact
   JPLTn6jLgRZgBkvGYKiwRN. On 5 Oct the auto-mode classifier refused `make verify` and `tools/buffer.py sync`
   as "Code from External" (session cse_01KKkdpLV9owvNrhYqq7U9Zi). Nothing can be scheduled after 13 Oct.
2. Posts are text only because Buffer needs a public image URL and we had none.

## Change
- The fixed files (CLAUDE.md, Makefile, routine/brief.md, tools/) move into `nueravix-x/` on the default
  branch of this repo, the routine's own source. The artifact keeps only memory (state/, measurements/,
  rules/) and the desk page.
- `tools/push_image.py` commits one PNG under `nueravix-x/images/`, pushes it to the session's working
  branch, and prints its raw.githubusercontent.com URL pinned to the commit SHA. It refuses any staged path
  outside `nueravix-x/images/` and refuses to push `bootstrap` or `main`.
- `check_x_draft.py` accepts an optional `image: {url, alt}` on originals and checks the URL shape and alt text.
- `buffer.py publish` attaches the image (top level, and on thread part 1) with its alt text.
- Images run as one experiment, `proof-image` vs `baseline` (text only), judged by `tools/review.py`.

## Checks
- `make verify` passes with new fixtures: image_ok (PASS) and image_bad (FAIL).
- `push_image.py` tested once from this machine on a throwaway `claude/` branch: URL returns 200 image/png.
- One routine run: sync no longer refused.

## Known risk
The repo holds GitHub Actions secrets for the Instagram worker. A routine that can push could, if misled by a
web page, add a workflow on its branch. Guard: the fixed rules and `push_image.py` allow only image paths. A
dedicated repo without secrets would remove the risk; it needs the owner to grant the Claude GitHub App access.
