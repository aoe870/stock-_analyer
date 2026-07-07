# Company Detail Data Display Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the enterprise detail data display described in `docs/superpowers/specs/2026-07-06-company-detail-data-display-design.md`.

**Architecture:** Reuse the existing FastAPI, MySQL repository, and static Vue app. The backend will expand local read shapes for already-ingested Miana enterprise data, and the frontend will render those shapes in stock detail tabs without adding click-time Miana requests.

**Tech Stack:** Python 3.12, FastAPI, PyMySQL, MySQL 8, pytest, Vue 3, Element Plus, Docker Compose.

---

## File Structure

- Modify `stock_analyzer_app/storage/mysql.py`: add enterprise module status metadata, officer rewards in stock overview, financial summary, capital-flow summary, and expanded coverage counts.
- Modify `stock_analyzer_app/api/app.py`: preserve stable fallback response shapes for the expanded overview, financials, and capital-flow APIs.
- Modify `public/app.js`: replace the compact enterprise section with stock detail tabs for financials, company profile, holders/officers/rewards, corporate actions/share capital, capital flow, and data status.
- Modify `tests/test_mysql_repositories.py`: lock repository read shapes and coverage.
- Modify `tests/test_api.py`: lock API response shapes for empty and populated enterprise data.
- Modify `tests/test_frontend_workspace.py`: lock frontend tab labels and state references.

## Task 1: Backend Enterprise Read Shape

- [ ] Write failing repository/API tests that expect `officer_rewards`, `enterprise_modules`, financial summary, capital-flow summary, and expanded data-center coverage.
- [ ] Run the focused tests and verify the failures are due to missing fields.
- [ ] Implement repository helper methods for row counts, newest dates, and module statuses.
- [ ] Include `stock_officer_rewards` in `stock_research_snapshot`.
- [ ] Add `summary` to `stock_financials` and `stock_capital_flow`.
- [ ] Extend `data_center_coverage()["research"]` with corporate actions, share capital, officers, and officer rewards.
- [ ] Run focused backend tests and verify they pass.

## Task 2: API Fallback Shapes

- [ ] Write failing API tests for stable empty shapes when optional enterprise data is missing.
- [ ] Update FastAPI fallback responses so `overview`, `financials`, and `capital-flow` expose the same keys as MySQL-backed responses.
- [ ] Run API tests and verify they pass.

## Task 3: Frontend Enterprise Tabs

- [ ] Write failing frontend static tests for stock detail tab labels, `officer_rewards`, financial summary, capital-flow summary, and enterprise module status references.
- [ ] Update `public/app.js` stock detail template to use major enterprise tabs.
- [ ] Add state defaults for summaries and enterprise module metadata.
- [ ] Add helper methods for module status labels and row count display if needed.
- [ ] Run frontend tests and verify they pass.

## Task 4: Verification

- [ ] Run backend unit/API/provider tests:

```powershell
docker run --rm -v "${PWD}:/work" -w /work stock_analyer-app python -m pytest tests/test_api.py tests/test_frontend_workspace.py tests/test_miana_provider.py -q
```

- [ ] Run MySQL repository tests:

```powershell
docker compose run --rm -v "${PWD}:/work" -w /work app python -m pytest tests/test_mysql_repositories.py -q
```

- [ ] Run `git diff --check`.
- [ ] Report changed files, test results, and any remaining gaps.

## Notes

- Do not commit unless the user explicitly asks.
- Do not add new Miana live calls to ordinary page click paths.
- Do not add new database tables unless the existing Miana field mapping is insufficient for the planned UI.
