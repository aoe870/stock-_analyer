# EXPMA Stock Analysis Web Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local FastAPI Web stock analysis app that screens stocks and backtests the EXPMA17/50 trend pullback strategy.

**Architecture:** Keep domain logic independent from Web/API code. The core package calculates indicators, strategy signals, screening results, and next-day-open backtests; FastAPI exposes those capabilities to a browser UI served from static files.

**Tech Stack:** Python 3.12 virtual environment, FastAPI, Uvicorn, pytest, vanilla browser HTML/CSS/JS.

---

## File Structure

- Create `requirements.txt`: runtime and test dependencies.
- Create `.gitignore`: ignore `.venv`, caches, and generated outputs.
- Create `stock_analyzer_app/indicators.py`: EMA, REF, CROSS helpers.
- Create `stock_analyzer_app/strategy.py`: EXPMA17/50 signal generation and priority.
- Create `stock_analyzer_app/backtest.py`: next-day-open 0/50/100 position backtest.
- Create `stock_analyzer_app/screening.py`: batch latest-signal screening.
- Create `stock_analyzer_app/data/csv_loader.py`: CSV OHLCV parser.
- Create `stock_analyzer_app/data/sample.py`: deterministic sample symbols for the UI.
- Create `stock_analyzer_app/api.py`: FastAPI app and JSON endpoints.
- Create `stock_analyzer_app/__main__.py`: `python -m stock_analyzer_app` server entry.
- Create `public/index.html`, `public/styles.css`, `public/app.js`: local Web UI.
- Create `tests/test_indicators.py`, `tests/test_strategy.py`, `tests/test_backtest.py`, `tests/test_csv_loader.py`, `tests/test_api.py`.

## Tasks

### Task 1: Project Setup and Indicators

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `stock_analyzer_app/indicators.py`
- Create: `tests/test_indicators.py`

- [ ] **Step 1: Write failing indicator tests**

Tests must verify `ref`, `cross`, and `ema` behavior using simple numeric lists.

- [ ] **Step 2: Run red test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_indicators.py -q`
Expected: FAIL because the package does not exist.

- [ ] **Step 3: Implement minimal indicator helpers**

Implement pure functions:
- `ref(values, periods=1)`
- `cross(left, right)`
- `ema(values, period)`

- [ ] **Step 4: Run green test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_indicators.py -q`
Expected: PASS.

### Task 2: EXPMA Strategy

**Files:**
- Create: `stock_analyzer_app/strategy.py`
- Create: `tests/test_strategy.py`

- [ ] **Step 1: Write failing strategy tests**

Tests must verify signal priority and explicit formulas for `BUY`, `HALF_SELL`, `RE_BUY`, `CLEAR_1`, `CLEAR_2`, and `RE_BUY_50`.

- [ ] **Step 2: Run red test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_strategy.py -q`
Expected: FAIL because the strategy module does not exist.

- [ ] **Step 3: Implement strategy**

Implement `compute_expma_signals(bars, short=17, long=50, warmup=60)` and `select_signal(flags)`.

- [ ] **Step 4: Run green test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_strategy.py -q`
Expected: PASS.

### Task 3: Backtest Engine

**Files:**
- Create: `stock_analyzer_app/backtest.py`
- Create: `tests/test_backtest.py`

- [ ] **Step 1: Write failing backtest tests**

Tests must verify next-day-open execution, 0/50/100 position transitions, unfilled final signal, and summary metrics.

- [ ] **Step 2: Run red test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_backtest.py -q`
Expected: FAIL because the backtest module does not exist.

- [ ] **Step 3: Implement backtest**

Implement `run_backtest(symbol_bars, initial_capital=100000, fee_rate=0.0003, slippage_rate=0.0005)`.

- [ ] **Step 4: Run green test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_backtest.py -q`
Expected: PASS.

### Task 4: CSV Loader and Screening

**Files:**
- Create: `stock_analyzer_app/data/csv_loader.py`
- Create: `stock_analyzer_app/data/sample.py`
- Create: `stock_analyzer_app/screening.py`
- Create: `tests/test_csv_loader.py`

- [ ] **Step 1: Write failing CSV tests**

Tests must verify English and Chinese headers normalize to `symbol`, `trade_date`, `open`, `high`, `low`, `close`, `volume`, and `amount`.

- [ ] **Step 2: Run red test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_csv_loader.py -q`
Expected: FAIL because the loader does not exist.

- [ ] **Step 3: Implement CSV parsing and screening**

Implement `parse_ohlcv_csv(text, default_symbol=None)` and `screen_latest(symbol_bars, trade_date=None)`.

- [ ] **Step 4: Run green test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_csv_loader.py -q`
Expected: PASS.

### Task 5: FastAPI and Browser UI

**Files:**
- Create: `stock_analyzer_app/api.py`
- Create: `stock_analyzer_app/__main__.py`
- Create: `tests/test_api.py`
- Create: `public/index.html`
- Create: `public/styles.css`
- Create: `public/app.js`

- [ ] **Step 1: Write failing API tests**

Tests must verify `GET /api/health`, `GET /api/sample`, `POST /api/screen`, and `POST /api/backtest`.

- [ ] **Step 2: Run red test**

Run: `.venv\Scripts\python.exe -m pytest tests/test_api.py -q`
Expected: FAIL because the API module does not exist.

- [ ] **Step 3: Implement API and UI**

Implement static UI serving and JSON endpoints backed by the core modules.

- [ ] **Step 4: Run full verification**

Run: `.venv\Scripts\python.exe -m pytest -q`
Expected: PASS.

- [ ] **Step 5: Start server**

Run: `.venv\Scripts\python.exe -m stock_analyzer_app`
Expected: server available at `http://127.0.0.1:8000`.

## Self-Review

- Covers local Web app, indicator screening, EXPMA17/50 strategy, next-day-open backtest, metrics, and signal details.
- Keeps data source abstraction simple for version 1 by supporting CSV/sample data first; AkShare/Tushare adapters remain the next increment after the Web and core engine are stable.
- No placeholders remain in the implementation tasks.
