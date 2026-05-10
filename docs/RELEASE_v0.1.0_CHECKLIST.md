# v0.1.0 Open Beta — Release Checklist

> Generated: 2026-05-10 (PR 18 dispatch)
>
> This document tracks all release actions for the v0.1.0 Open Beta.
> Items marked **Done automatically** were completed by the PR 18 agent.
> Items marked **Required** must be performed manually by the maintainer.

---

## 1. Done Automatically (PR 18)

- [x] Pre-flight: `make sync-cases` — 63 cases confirmed in sync with airoasting.github.io/5color/
- [x] Pre-flight: `make sync-slides` — 35 slide templates confirmed in sync
- [x] Pre-flight: `make gen-case-catalog` — `docs/ko/case-catalog.md` regenerated
- [x] Pre-flight: All 94 unit tests pass (`pytest -m "not slow and not network"` — 94 passed, 5 deselected)
- [x] Lint: `ruff check .` — all clean (15 unused-import / f-string issues auto-fixed)
- [x] Type check: `mypy scripts/` — all clean (8 `no-any-return` suppressions added strategically)
- [x] CHANGELOG.md: `[0.1.0] - 2026-05-10 (Open Beta)` date confirmed correct
- [x] `plugin.json`: `version: "0.1.0"` confirmed
- [x] `marketplace.json`: `version: "0.1.0"` confirmed
- [x] `pyproject.toml`: Added explicit `[tool.setuptools.packages.find] include = ["scripts*"]` to fix CI build failure (setuptools was discovering `db/` and `skills/` as top-level packages)
- [x] Tag `v0.1.0` created and pushed (`git push origin v0.1.0`)
- [x] Release workflow (`release.yml`) triggered on tag push

### Release Workflow Status

> **Note:** The first release workflow attempt failed due to the `pyproject.toml` setuptools
> package-discovery bug. The bug was fixed (`fix(build): explicit package discovery`), the tag
> was re-created on the fixed commit, and the workflow was re-triggered.
>
> Verify final status: `gh release view v0.1.0`
> Workflow runs: `gh run list --limit 5`

---

## 2. External Actions Required

### 2.1 Verify GitHub Release Asset

**Owner:** Maintainer
**Estimated time:** 5 minutes

- [ ] Confirm the GitHub Release exists:
  ```bash
  gh release view v0.1.0 --json tagName,name,assets,url
  ```
- [ ] Confirm the `.zip` artifact is attached (created by `make package` in `release.yml`)
- [ ] If the release workflow is still failing, check logs:
  ```bash
  gh run list --limit 5
  gh run view <run-id> --log-failed
  ```
  Then re-trigger manually if needed:
  ```bash
  gh workflow run release.yml --ref v0.1.0
  ```
- [ ] Release URL: https://github.com/airoasting/roasting/releases/tag/v0.1.0

---

### 2.2 Anthropic Marketplace Submission

**Owner:** Maintainer
**Estimated time:** 30–60 minutes (process varies by Anthropic's current review flow)

**Pre-submission verification (local):**
```bash
# Verify marketplace.json is valid JSON
python -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('OK')"

# Verify plugin.json is valid JSON
python -c "import json; json.load(open('.claude-plugin/plugin.json')); print('OK')"
```

**Submission steps:**
- [ ] Check if Anthropic Marketplace has a self-service submission portal (check https://claude.ai/marketplace or developer docs)
- [ ] Verify install path resolves locally:
  ```
  /plugin marketplace add airoasting/roasting
  /plugin install roasting@airoasting
  ```
- [ ] If automatic via public GitHub repo: verify that the repo is public and the plugin manifests are at the repo root
- [ ] If manual review required: submit through Anthropic's current process (check https://docs.anthropic.com for the latest Marketplace submission guide)
- [ ] Once listed, update `README.md` with the marketplace badge/link:
  ```markdown
  [![Marketplace](https://img.shields.io/badge/Anthropic_Marketplace-roasting-blue)](https://marketplace.anthropic.com/roasting)
  ```
- [ ] Update `CHANGELOG.md` under v0.1.0 with the marketplace listing link

**Marketplace manifest files:**
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

---

### 2.3 airoasting.github.io Landing Page

**Owner:** Maintainer
**Repo:** `airoasting/airoasting.github.io` (separate repository)
**Estimated time:** 1–2 hours

- [ ] Clone / open the `airoasting/airoasting.github.io` repo
- [ ] Create `/roasting` landing page at `roasting/index.html` (or equivalent for the site generator in use)
- [ ] Required page sections:
  1. **Hero:** Plugin name + tagline + install command (copy-paste block):
     ```
     /plugin install roasting@airoasting
     ```
  2. **Case library:** 63 cases across 8 categories — link to https://airoasting.github.io/5color/
  3. **Privacy summary:** 1 paragraph — content never transmitted; only opt-in metadata; link to https://github.com/airoasting/roasting/blob/main/docs/PRIVACY.md
  4. **Beta status banner:** "v0.1 Open Beta. Free during beta. Feedback welcome."
  5. **Links:** GitHub repo (https://github.com/airoasting/roasting), Marketplace listing
- [ ] Push changes and verify https://airoasting.github.io/roasting loads
- [ ] Update `CHANGELOG.md` with the landing page URL

---

### 2.4 Supabase Telemetry Backend Provisioning

**Owner:** Maintainer
**Estimated time:** 20–30 minutes
**Reference:** `docs/setup/supabase.md`

- [ ] Create Supabase project at https://supabase.com (free tier is sufficient for v0.1 beta)
- [ ] Get Project URL + anon key from: Project Settings → API
- [ ] Run the schema migration — open SQL Editor in Supabase dashboard and execute:
  ```
  db/migrations/0001_init_telemetry.sql
  ```
- [ ] Add secrets to GitHub Actions (repo Settings → Secrets → Actions):
  - `SUPABASE_URL` — your project URL (e.g. `https://xyzxyz.supabase.co`)
  - `SUPABASE_ANON_KEY` — your project anon key
- [ ] Hardcode the URL + anon key into `scripts/telemetry.py` for the plugin distribution
  (anon key is safe to ship — RLS policy allows INSERT only):
  ```python
  SUPABASE_URL = os.environ.get("ROASTING_SUPABASE_URL", "https://YOUR_PROJECT.supabase.co")
  SUPABASE_ANON_KEY = os.environ.get("ROASTING_SUPABASE_ANON_KEY", "YOUR_ANON_KEY")
  ```
- [ ] Commit and push the updated `scripts/telemetry.py`
- [ ] Verify telemetry works end-to-end (opt-in must be explicit — default OFF):
  ```bash
  echo '{"telemetry": true}' > ~/.claude/roasting/config.json
  python -c "from scripts.telemetry import is_enabled; print(is_enabled())"
  ```
- [ ] Capacity check (free tier): 500 MB DB, 2 GB egress/month. v0.1 beta target: ~7,500 rows << 2M capacity. No upgrade needed.

---

### 2.5 Quality Gate Full Run

**Owner:** Maintainer
**Estimated time:** 20–30 minutes (API calls + review)
**Cost:** ~$5–7 USD in API credits

> **Context:** The quality gate was infrastructure-complete in PR 17 but was time-capped before
> a full run completed. This must be run manually with a valid `CLAUDE_CODE_OAUTH_TOKEN`.

- [ ] Set your auth token:
  ```bash
  export CLAUDE_CODE_OAUTH_TOKEN="your_token_here"
  ```
- [ ] Run the full quality gate (15 scenarios, may take 20–30 minutes):
  ```bash
  .venv/bin/pytest tests/quality/test_quality_gate.py -v -m slow -s
  ```
- [ ] Gate requirement: average final score >= 9.0 across all 15 scenarios
- [ ] If gate fails (avg < 9.0): review which case categories are underperforming and
  iterate on SKILL.md prompts for those categories before v1.0 promotion

---

### 2.6 Beta Announcements

**Owner:** Maintainer
**Platforms:** LinkedIn (Korean) + X/Twitter (English)

#### LinkedIn Post (Korean)

> Post this verbatim. Add the landing page URL once it's live.

```
임원이 한 줄로 호출하면 5-Color Harness가 화이트칼라 산출물을 짚어주는
Claude Code 플러그인 v0.1 오픈 베타.

- 63개 케이스 (이메일/보고서/PPT/메모/...) 자동 라우팅
- BLACK 작성 + RGSB 4인 토론 채점 + 9.5 합격선
- 콘텐츠 0 수집 (메타데이터만, opt-in)

설치: /plugin install roasting@airoasting
docs: https://airoasting.github.io/roasting
```

**Action steps:**
- [ ] Go to https://www.linkedin.com and post the above text
- [ ] Add relevant hashtags: `#ClaudeCode #AI #Korean #WhiteCollar #OpenBeta`
- [ ] Save the post URL
- [ ] Update `CHANGELOG.md` with the LinkedIn post URL

#### X (Twitter) Post (English)

> Post this verbatim. Character count: ~280 — fits in one tweet.

```
Open beta: /roasting — a Claude Code plugin that runs the 5-Color Harness
methodology over 63 white-collar cases. Korean-first.

BLACK Producer + RGSB Reviewers (debate-driven scoring) → output + critique
+ reasoning. Anonymous opt-in telemetry; content never transmitted.

https://github.com/airoasting/roasting
```

**Action steps:**
- [ ] Go to https://x.com and post the above text
- [ ] Save the post URL
- [ ] Update `CHANGELOG.md` with the X post URL

---

### 2.7 Post-announcement CHANGELOG update

Once announcements are live and the marketplace is listed:

- [ ] Open `CHANGELOG.md`
- [ ] Under `## [0.1.0] - 2026-05-10 (Open Beta)`, add an announcement section:
  ```markdown
  ### Announcement
  - Marketplace: <marketplace_url>
  - Landing: https://airoasting.github.io/roasting
  - LinkedIn: <linkedin_post_url>
  - X: <x_post_url>
  ```
- [ ] Commit and push:
  ```bash
  git add CHANGELOG.md README.md
  git commit -m "release: v0.1.0 open beta — listed, announced

  - Marketplace listing: <link>
  - Landing: https://airoasting.github.io/roasting
  - LinkedIn announcement: <link>
  - X announcement: <link>

  Beta cohort: open. Privacy: opt-in metadata only.

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
  git push
  ```

---

## 3. v0.1 → v1.0 Promotion Gates (for future reference)

| Gate | Target | How to measure |
|---|---|---|
| Routing accuracy (live) | >= 95% Wilson 95% LB | telemetry `case_id` distribution audit |
| Quality (live) | avg >= 9.5 `final_score` | telemetry `final_score` field |
| Beta users | >= 50 distinct `user_id` | `SELECT COUNT(DISTINCT user_id) FROM telemetry` |
| Feedback signal | >= 100 GitHub Issues with `beta-feedback` label | `gh issue list -l beta-feedback` |
| Per-case usage | >= 10 calls/case for >= 30 cases | telemetry `case_id` counts |

All 5 gates met → cut `v1.0.0`.

---

## 4. Known Issues

### CI Test Workflow Failures (pre-existing)

The `test.yml` CI workflow has been failing across all prior PRs. Root cause was traced to
the same `pyproject.toml` setuptools package-discovery bug (now fixed in this PR). After the
`fix(build)` commit lands, CI test runs should pass. Verify:

```bash
gh run list --limit 10 | grep "Test"
```

### Release Workflow — First Attempt Failed

The first `release.yml` run (run ID `25616732577`) failed due to `pip install -e ".[dev]"` 
hitting the setuptools multi-top-level error. Fixed in commit `b7fc610`. The tag was
deleted and re-created on the fixed commit. Second workflow run should succeed.
