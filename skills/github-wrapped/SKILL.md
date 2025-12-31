---
name: github-wrapped
description: Generate a verifiable GitHub Wrapped year-in-review as a single-file HTML (raw gh API JSON saved, Python dataset build, embedded dataset), with a Bilibili-style narrative and smooth animations. Requires gh CLI to be authenticated.
---

# GitHub Wrapped (Single-file HTML, Verifiable Data)

This skill generates a GitHub “Year in Review / Wrapped” as a **single self-contained HTML file** with a **Bilibili-style narrative** (scroll/page scenes, cinematic transitions, share card). The non-negotiable requirement is **verifiability**: every number must be traceable to saved `gh api` raw responses.

## Non-negotiables

- **No fabricated data**: if GitHub APIs cannot provide a metric, show `—` and explain the limitation in-page.
- **Save raw API responses**: the report is invalid without a `raw/` folder containing the original JSON (and the GraphQL queries used).
- **Ship one `.html`**: no runtime `gh` calls; embed a dataset into the HTML.
- **External CDNs are optional** (fonts/icons/screenshot libs/music) but must never break core navigation/rendering if they fail to load.

## What to ask the user first

- `YEAR` (default: current year)
- `USER` (default: `gh api user --jq .login`)
- Output language for the page copy (Chinese is usually preferred for CN users; this doc stays English)
- Timezone (default: `Asia/Shanghai` for CN users)
- Whether to enable a music widget (autoplay may be blocked; must have a user-gesture fallback)

## Recommended layout

```
data/github-wrapped-$YEAR/
  raw/                  # verifiable gh API responses (JSON)
  processed/             # dataset.json derived from raw/
frontend/standalone/
  github-wrapped-$YEAR.html
```

## Pipeline (raw → dataset → single HTML)

### 1) Collect raw JSON with `gh api` (always paginate)

Pagination rules:

- GraphQL: `--paginate --slurp`
- REST: `--paginate`

Minimum raw set (recommended filenames):

- `raw/user.json` (profile, createdAt)
- `raw/contributions.json` (GraphQL `contributionsCollection(from,to)`)
- `raw/user_repos.json` (REST repos list; stars/forks are snapshots)
- `raw/starred_repos_pages.json` (GraphQL starred repos ordered by `STARRED_AT`, includes topics/language)
- `raw/prs_${YEAR}_pages.json` (GraphQL Search: merged PRs in the year; additions/deletions)
- `raw/contributed_repos_pages.json` (GraphQL `repositoriesContributedTo`)
- `raw/events_90d.json` (optional; REST events; **90-day limit**; only for best-effort easter eggs)

Bundled templates (open only what you need):

- `scripts/collect_raw.sh`
- `scripts/queries/*.graphql`
- `references/data_sources.md`
- `references/single_file_engineering.md`

### 2) Build a deterministic dataset (Python, no guessing)

Write a builder that reads only `raw/*.json` and outputs `processed/dataset.json`:

- Deterministic: same raw input → same dataset output.
- Transparent: write limitations into `meta.dataProvenance.notes[]`.
- Stable for rendering: keep optional fields nullable; avoid breaking changes.

Template: `scripts/build_dataset_template.py`
Schema guidance: `references/dataset_schema.md`

### 3) Embed `dataset.json` into the HTML (no runtime fetch)

Your HTML must contain a stable anchor:

```html
<script id="dataset" type="application/json">{}</script>
```

Embed rules:

- Always escape `<` as `\u003c` before writing into the HTML.
- If the dataset block is missing/corrupted, the embed script should fail loudly (or repair it).
- The page must show a visible overlay if dataset parsing fails (avoid “cover only, buttons dead”).

Template: `scripts/embed_dataset_into_html_template.py`

## Narrative + UI quality bar (Bilibili-style pacing)

Design as a storyboard: each scene answers **one** question, then transitions.

Suggested pacing:

1. Grand cover + “Start” (cinematic; optional fireworks)
2. “How long since we met GitHub” (account createdAt → years)
3. “Your 2025 pulse” (activity tier + distribution)
4. Heatmap/city + streak + craziest day
5. “Time Tower” (your key projects this year)
6. “Radar / hexagon” (categories; hover nodes should lift/glow)
7. “New interests unlocked” (2025 stars vs previous years)
8. “Extreme moments” (night-owl / holidays; clearly mark best-effort)
9. “Open Source Award” (external contribution highlight; award ceremony feel)
10. Finale share card (screenshot-friendly; optional fireworks)

Interaction rules:

- Every button/card should be clickable with feedback (links when available; otherwise micro-interaction/toast).
- “Free scroll” vs “Page mode” must behave differently (page mode should snap/lock navigation by wheel/keys).
- Unify motion tokens (duration/easing) across scenes; prefer `transform/opacity`.

## Known data limits (must disclose)

- Contribution calendar provides **day-level counts**, not a complete commit list per day.
- Events API keeps only **~90 days** of history.
- Repo `stargazers_count/forks_count` are **current snapshots**, not year-increment.
- Private contributions / hidden settings can skew the public view.

## Debug checklist

See `references/debug_checklist.md` for the full checklist. Common root causes:

- A JS parse error stops all handlers (duplicate `const`, missing `)`)
- A broken embedded dataset block breaks JSON parsing
- A blocked external script was treated as required instead of optional

## Bundled resources (progressive disclosure)

- `scripts/`: reusable collection/build/embed templates (execute without loading into context)
- `references/`: schema + storyboard + debugging notes (open only the specific file you need)
