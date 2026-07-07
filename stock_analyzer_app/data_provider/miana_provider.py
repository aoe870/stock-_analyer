import json
import threading
import time
from collections import deque
from datetime import date, timedelta
from typing import Callable
from urllib.parse import urlencode
from urllib.request import urlopen


class _SlidingWindowRateLimiter:
    def __init__(self, max_requests_per_minute: int) -> None:
        self.max_requests_per_minute = max(1, int(max_requests_per_minute))
        self.window_seconds = 60.0
        self._timestamps: deque[float] = deque()
        self._condition = threading.Condition()

    def acquire(self) -> None:
        with self._condition:
            while True:
                now = time.monotonic()
                while self._timestamps and now - self._timestamps[0] >= self.window_seconds:
                    self._timestamps.popleft()
                if len(self._timestamps) < self.max_requests_per_minute:
                    self._timestamps.append(now)
                    self._condition.notify_all()
                    return
                wait_seconds = self.window_seconds - (now - self._timestamps[0])
                self._condition.wait(timeout=max(wait_seconds, 0.01))


class MianaProvider:
    name = "miana"

    def __init__(
        self,
        token: str,
        base_url: str = "https://miana.com.cn/api",
        http_get: Callable[[str, dict], dict] | None = None,
        max_requests_per_minute: int = 500,
    ) -> None:
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.http_get = http_get
        self.max_requests_per_minute = max(1, int(max_requests_per_minute))
        self._rate_limiter = _SlidingWindowRateLimiter(self.max_requests_per_minute)
        self._thread_local = threading.local()

    def fetch_stock_universe(self) -> list[dict]:
        payload = self._request("/stock/v1/stockList", {"market": "cn_hsj"})
        rows = _data(payload)
        output = []
        for row in rows:
            symbol = normalized_symbol(row)
            name = row.get("name") or symbol
            output.append(
                {
                    "symbol": symbol,
                    "exchange": _exchange_from_symbol(symbol),
                    "name": name,
                    "industry": row.get("industry"),
                    "is_active": True,
                    "is_st": "ST" in str(name).upper(),
                    "source": self.name,
                    "provider": self.name,
                    "provider_symbol": miana_symbol(symbol),
                    "country_code": row.get("countryCode"),
                    "exchange_code": row.get("exchangeCode"),
                    "market": row.get("market"),
                    "type": row.get("type"),
                    "raw_json": dict(row),
                }
            )
        return output

    def fetch_trading_calendar(self, exchange: str, start_date: str, end_date: str) -> list[dict]:
        return []

    def fetch_daily_bars(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        return self._fetch_kline(symbol, start_date, end_date, fq="bfq", is_adjusted=False)

    def fetch_adjusted_daily_bars(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        return self._fetch_kline(symbol, start_date, end_date, fq="qfq", is_adjusted=True)

    def fetch_adjustment_factors(self, symbol: str, start_date: str, end_date: str) -> list[dict]:
        raw_by_date = {row["trade_date"]: row for row in self._fetch_kline(symbol, start_date, end_date, fq="bfq", is_adjusted=False)}
        adjusted_by_date = {row["trade_date"]: row for row in self._fetch_kline(symbol, start_date, end_date, fq="qfq", is_adjusted=True)}
        return self._build_adjustment_factors(symbol, raw_by_date, adjusted_by_date)

    def fetch_daily_bar_bundle(self, symbol: str, start_date: str, end_date: str) -> dict[str, list[dict]]:
        bars = self._fetch_kline(symbol, start_date, end_date, fq="bfq", is_adjusted=False)
        adjusted_bars = self._fetch_kline(symbol, start_date, end_date, fq="qfq", is_adjusted=True)
        factors = self._build_adjustment_factors(
            symbol,
            {row["trade_date"]: row for row in bars},
            {row["trade_date"]: row for row in adjusted_bars},
        )
        return {"bars": bars, "adjusted_bars": adjusted_bars, "factors": factors}

    def _build_adjustment_factors(self, symbol: str, raw_by_date: dict[str, dict], adjusted_by_date: dict[str, dict]) -> list[dict]:
        factors = []
        for trade_date, raw in raw_by_date.items():
            adjusted = adjusted_by_date.get(trade_date)
            raw_close = raw.get("close")
            adjusted_close = adjusted.get("close") if adjusted else None
            if raw_close in (None, 0) or adjusted_close is None:
                continue
            factors.append(
                {
                    "symbol": symbol,
                    "trade_date": trade_date,
                    "adj_factor": adjusted_close / raw_close,
                    "source": self.name,
                }
            )
        return factors

    def fetch_stock_status(self, symbols: list[str], trade_date: str) -> list[dict]:
        return [{"symbol": symbol, "trade_date": trade_date, "is_st": False, "is_suspended": False, "source": self.name} for symbol in symbols]

    def fetch_stock_rankings(self, sort: str = "changeRate", order: str = "DESC", page: int = 1) -> list[dict]:
        payload = self._request(
            "/stock/v1/sort",
            {"market": "cn_hsj", "sort": sort, "order": order, "page": str(page)},
        )
        return [_normalize_quote_row(row) for row in _list_data(payload) if normalized_symbol(row)]

    def fetch_index_rankings(self, sort: str = "changeRate", order: str = "DESC", page: int = 1) -> list[dict]:
        payload = self._request(
            "/index/v1/sort",
            {"countryCode": "CHN", "sort": sort, "order": order, "page": str(page)},
        )
        return [_normalize_market_quote_row(row, code_key="index_code") for row in _list_data(payload) if _market_symbol(row)]

    def fetch_sector_rankings(self, sort: str = "changeRate", order: str = "DESC", page: int = 1, sector_type: str = "all") -> list[dict]:
        payload = self._request(
            "/sector/v1/sort",
            {"market": "cn_hs", "type": sector_type, "sort": sort, "order": order, "page": str(page)},
        )
        return [_normalize_market_quote_row(row, code_key="sector_code") for row in _list_data(payload) if row.get("code") or row.get("symbol")]

    def fetch_company_profiles(self, symbol: str) -> list[dict]:
        payload = self._request("/stock/v1/companyInfo", {"symbol": miana_symbol(symbol)}, symbol=symbol)
        rows = _company_profile_rows(payload)
        output = []
        for row in rows:
            concepts = row.get("concepts")
            found_date = _date(row.get("foundDate")) or (_date(concepts) if _looks_like_date(concepts) else None)
            output.append(
                {
                "symbol": symbol,
                "provider": self.name,
                "company_name": row.get("orgName") or row.get("nameA") or row.get("name"),
                "industry": row.get("industry"),
                "region": row.get("regionBK"),
                "concepts": None if found_date and _looks_like_date(concepts) else concepts,
                "address": row.get("address") or row.get("regAddress"),
                "legal_person": row.get("legalPerson"),
                "chairman": row.get("chairman"),
                "president": row.get("president"),
                "secretary": row.get("secretary"),
                "found_date": found_date,
                "registered_capital": row.get("regCapital"),
                "employee_count": row.get("totalNum") or row.get("tatolNumber"),
                "accounting_firm": row.get("accountFirm"),
                "legal_adviser": row.get("legalAdviser"),
                "org_tel": row.get("orgTel"),
                "org_email": row.get("orgEmail"),
                "org_web": row.get("orgWeb"),
                "org_profile": row.get("orgProfile"),
                "company_profile": row.get("profile"),
                "main_business": row.get("mainBusiness"),
                "raw_json": dict(row),
            }
            )
        return output

    def fetch_corporate_actions(self, symbol: str) -> list[dict]:
        payload = self._request_first(["/stock/v1/distribution", "/stock/v1/distribute"], {"symbol": miana_symbol(symbol)}, symbol=symbol)
        return [
            {
                "symbol": symbol,
                "provider": self.name,
                "action_type": row.get("dividendType") or row.get("type", "unknown"),
                "currency": row.get("currency"),
                "dividend": _first_value(row, "cashAmount", "cashPerShare", "dividend"),
                "split_factor": _first_value(row, "stockRatio", "splitFactor"),
                "notice_date": _date(row.get("announcementDate") or row.get("noticeDate")),
                "report_date": str(row.get("fiscalYear") or row.get("reportDate") or ""),
                "equity_record_date": _date(row.get("recordDate") or row.get("equityRecordDate")),
                "ex_dividend_date": _date(row.get("exDividendDate")),
                "pay_cash_date": _date(row.get("paymentDate") or row.get("payCashDate")),
                "raw_json": dict(row),
            }
            for row in _data(payload)
        ]

    def fetch_share_capital_history(self, symbol: str) -> list[dict]:
        payload = self._request("/stock/v1/shares", {"symbol": miana_symbol(symbol)}, symbol=symbol)
        return [
            {
                "symbol": symbol,
                "provider": self.name,
                "end_date": _date(row.get("endDate")),
                "total_shares": row.get("totalShares"),
                "floating_shares": row.get("floatingShares"),
                "limited_shares": row.get("limitedShares"),
                "change_reason": row.get("changeReason"),
                "raw_json": dict(row),
            }
            for row in _data(payload)
            if _date(row.get("endDate"))
        ]

    def fetch_daily_money_flow(self, symbol: str, trade_date: str) -> list[dict]:
        payload = self._request("/stock/v1/dailyMoneyflow", {"symbol": miana_symbol(symbol)}, symbol=symbol, date_start=trade_date, date_end=trade_date)
        data = payload.get("data") or {}
        if not data:
            return []
        return [
            {
                "symbol": symbol,
                "provider": self.name,
                "trade_date": trade_date,
                "amount": data.get("amount"),
                "main_net_inflow_amount": data.get("mianNetInflowAmount") or data.get("mainNetInflowAmount"),
                "main_net_ratio": data.get("mainNetRatio"),
                "super_large_inflow": data.get("superLargeInflow"),
                "super_large_outflow": data.get("superLargeOutflow"),
                "raw_json": data,
            }
        ]

    def fetch_income_statements(self, symbol: str) -> list[dict]:
        payload = self._request_first(["/stock/v1/incomeStatement", "/stock/v1/incomeSheet"], {"symbol": miana_symbol(symbol)}, symbol=symbol)
        return [
            {
                "symbol": symbol,
                "provider": self.name,
                "report_date": _date(row.get("reportDate") or row.get("date") or row.get("endDate")),
                "notice_date": _date(row.get("announcementDate") or row.get("noticeDate")),
                "report_period": _report_period(row),
                "currency": row.get("currency"),
                "revenue": _first_value(row, "totalRevenue", "revenue"),
                "operating_revenue": _first_value(row, "operatingRevenue", "operateRevenue", "businessIncome"),
                "operating_profit": _first_value(row, "operatingProfit", "operateProfit"),
                "total_profit": _first_value(row, "totalProfit"),
                "net_profit": _first_value(row, "netProfit"),
                "net_profit_parent": _first_value(row, "netProfitToParent", "netProfitParent", "parentNetProfit"),
                "eps": _first_value(row, "basicEps", "eps"),
                "raw_json": dict(row),
            }
            for row in _data(payload)
            if _date(row.get("reportDate") or row.get("date") or row.get("endDate"))
        ]

    def fetch_balance_sheets(self, symbol: str) -> list[dict]:
        payload = self._request("/stock/v1/balanceSheet", {"symbol": miana_symbol(symbol)}, symbol=symbol)
        return [
            {
                "symbol": symbol,
                "provider": self.name,
                "report_date": _date(row.get("reportDate") or row.get("date") or row.get("endDate")),
                "notice_date": _date(row.get("noticeDate")),
                "report_period": row.get("reportPeriod") or row.get("reportDate") or "",
                "currency": row.get("currency"),
                "total_assets": _first_value(row, "totalAssets"),
                "total_liabilities": _first_value(row, "totalLiabilities"),
                "total_equity": _first_value(row, "totalEquity", "shareholderEquity"),
                "monetary_funds": _first_value(row, "monetaryFunds", "cash"),
                "accounts_receivable": _first_value(row, "accountsReceivable"),
                "inventory": _first_value(row, "inventory"),
                "raw_json": dict(row),
            }
            for row in _data(payload)
            if _date(row.get("reportDate") or row.get("date") or row.get("endDate"))
        ]

    def fetch_cashflow_statements(self, symbol: str) -> list[dict]:
        payload = self._request_first(["/stock/v1/cashFlowStatement", "/stock/v1/cashflow"], {"symbol": miana_symbol(symbol)}, symbol=symbol)
        return [
            {
                "symbol": symbol,
                "provider": self.name,
                "report_date": _date(row.get("reportDate") or row.get("date") or row.get("endDate")),
                "notice_date": _date(row.get("announcementDate") or row.get("noticeDate")),
                "report_period": _report_period(row),
                "currency": row.get("currency"),
                "net_operating_cashflow": _first_value(row, "netCashFromOperating", "netOperatingCashflow", "netOperateCashflow"),
                "net_investing_cashflow": _first_value(row, "netCashFromInvesting", "netInvestingCashflow", "netInvestCashflow"),
                "net_financing_cashflow": _first_value(row, "netCashFromFinancing", "netFinancingCashflow", "netFinanceCashflow"),
                "cash_and_equivalents": _first_value(row, "cashClosingBalance", "cashAndEquivalents", "cashEquivalent"),
                "raw_json": dict(row),
            }
            for row in _data(payload)
            if _date(row.get("reportDate") or row.get("date") or row.get("endDate"))
        ]

    def fetch_top10_holders(self, symbol: str) -> list[dict]:
        payload = self._request_first(["/stock/v1/top10Shareholders", "/stock/v1/top10holders"], {"symbol": miana_symbol(symbol)}, symbol=symbol)
        rows = _shareholder_rows(payload)
        return [
            {
                "symbol": symbol,
                "provider": self.name,
                "report_date": _date(row.get("reportDate") or row.get("date") or row.get("endDate")),
                "holder_name": row.get("holderName") or row.get("name") or "",
                "holder_rank": index,
                "hold_volume": _first_value(row, "holdAmount", "shareCount", "holdVol", "holdVolume"),
                "hold_ratio": _first_value(row, "holdRatio", "ratio", "shareholdingRatio"),
                "share_type": row.get("holderType") or row.get("shareType"),
                "raw_json": dict(row),
            }
            for index, row in enumerate(rows, start=1)
            if _date(row.get("reportDate") or row.get("date") or row.get("endDate")) and (row.get("holderName") or row.get("name"))
        ]

    def fetch_company_officers(self, symbol: str) -> list[dict]:
        payload = self._request("/stock/v1/companyOfficers", {"symbol": miana_symbol(symbol)}, symbol=symbol)
        return [
            {
                "symbol": symbol,
                "provider": self.name,
                "officer_name": row.get("name") or "",
                "title": row.get("title") or "",
                "start_date": _date(row.get("appointmentDate") or row.get("startDate")),
                "end_date": _date(row.get("resignationDate") or row.get("endDate")),
                "raw_json": dict(row),
            }
            for row in _data(payload)
            if row.get("name")
        ]

    def fetch_officer_rewards(self, symbol: str) -> list[dict]:
        payload = self._request("/stock/v1/rewards", {"symbol": miana_symbol(symbol)}, symbol=symbol)
        return [
            {
                "symbol": symbol,
                "provider": self.name,
                "report_date": _date(row.get("date") or row.get("reportDate") or row.get("endDate")),
                "officer_name": row.get("name") or "",
                "title": row.get("title"),
                "reward": _number_value(_first_value(row, "compensation", "reward")),
                "hold_volume": _number_value(_first_value(row, "shareholding", "sharesHeld", "holdVol", "holdVolume")),
                "raw_json": dict(row),
            }
            for row in _data(payload)
            if _date(row.get("date") or row.get("reportDate") or row.get("endDate")) and row.get("name")
        ]

    def fetch_index_list(self) -> list[dict]:
        payload = self._request("/index/v1/indexList", {"countryCode": "CHN"})
        return [
            {
                "index_code": _market_symbol(row),
                "provider": self.name,
                "name": row.get("name") or _market_symbol(row),
                "exchange_code": row.get("exchangeCode"),
                "country_code": row.get("countryCode"),
                "raw_json": dict(row),
            }
            for row in _data(payload)
            if _market_symbol(row)
        ]

    def fetch_index_constituents(self, index_code: str) -> list[dict]:
        payload = self._request("/index/v1/constituent", {"symbol": index_code})
        return [
            {
                "index_code": index_code,
                "provider": self.name,
                "symbol": normalized_symbol(row),
                "weight": row.get("weight"),
                "raw_json": dict(row),
            }
            for row in _data(payload)
            if normalized_symbol(row)
        ]

    def fetch_sector_list(self) -> list[dict]:
        payload = self._request("/sector/v1/sectorList", {"market": "cn_hs"})
        return [
            {
                "sector_code": str(row.get("code") or row.get("symbol") or ""),
                "provider": self.name,
                "name": row.get("name") or str(row.get("code") or row.get("symbol") or ""),
                "market": row.get("market"),
                "raw_json": dict(row),
            }
            for row in _data(payload)
            if row.get("code") or row.get("symbol")
        ]

    def fetch_sector_constituents(self, sector_code: str) -> list[dict]:
        payload = self._request("/sector/v1/constituent", {"symbol": sector_code})
        return [
            {
                "sector_code": sector_code,
                "provider": self.name,
                "symbol": normalized_symbol(row),
                "weight": row.get("weight"),
                "raw_json": dict(row),
            }
            for row in _data(payload)
            if normalized_symbol(row)
        ]

    def drain_raw_payloads(self) -> list[dict]:
        payloads = getattr(self._thread_local, "raw_payloads", [])
        self._thread_local.raw_payloads = []
        return list(payloads)

    def _fetch_kline(self, symbol: str, start_date: str, end_date: str, fq: str, is_adjusted: bool) -> list[dict]:
        rows = []
        for segment_start, segment_end in _date_segments(start_date, end_date):
            payload = self._request(
                "/stock/v2/kline",
                {
                    "symbol": miana_symbol(symbol),
                    "type": "d1",
                    "beginDate": f"{segment_start} 00:00:00",
                    "endDate": f"{segment_end} 23:59:59",
                    "order": "ASC",
                    "limit": "2000",
                    "fq": fq,
                },
                symbol=symbol,
                date_start=segment_start,
                date_end=segment_end,
            )
            rows.extend(
                {
                    "symbol": symbol,
                    "trade_date": _date(row.get("date")),
                    "open": _number_value(row.get("open")),
                    "high": _number_value(row.get("high")),
                    "low": _number_value(row.get("low")),
                    "close": _number_value(_first_value(row, "close", "price")),
                    "volume": _number_value(row.get("volume", 0)),
                    "amount": _number_value(row.get("amount", 0)),
                    "source": self.name,
                    "is_adjusted": is_adjusted,
                }
                for row in _data(payload)
                if _date(row.get("date"))
            )
        return sorted(rows, key=lambda row: row["trade_date"])

    def _request(
        self,
        endpoint: str,
        params: dict,
        symbol: str | None = None,
        date_start: str | None = None,
        date_end: str | None = None,
    ) -> dict:
        self._rate_limiter.acquire()
        request_params = {"token": self.token, **params}
        if self.http_get:
            payload = self.http_get(endpoint, params)
        else:
            url = f"{self.base_url}{endpoint}?{urlencode(request_params)}"
            with urlopen(url, timeout=30) as response:  # noqa: S310 - URL is configured data provider endpoint.
                payload = json.loads(response.read().decode("utf-8"))
        self._append_raw_payload(
            {
                "provider": self.name,
                "endpoint": endpoint,
                "symbol": symbol,
                "date_start": date_start,
                "date_end": date_end,
                "request_params": dict(params),
                "payload": payload,
            }
        )
        if payload.get("code") not in (None, 0, 200):
            raise RuntimeError(f"Miana {endpoint} returned code={payload.get('code')} msg={payload.get('msg')}")
        return payload

    def _request_first(
        self,
        endpoints: list[str],
        params: dict,
        symbol: str | None = None,
        date_start: str | None = None,
        date_end: str | None = None,
    ) -> dict:
        last_error: Exception | None = None
        for endpoint in endpoints:
            try:
                return self._request(endpoint, params, symbol=symbol, date_start=date_start, date_end=date_end)
            except Exception as exc:  # noqa: BLE001 - fallback endpoint compatibility for provider API drift.
                last_error = exc
                continue
        if last_error:
            raise last_error
        raise RuntimeError("Miana endpoint list is empty")

    def _append_raw_payload(self, payload: dict) -> None:
        if not hasattr(self._thread_local, "raw_payloads"):
            self._thread_local.raw_payloads = []
        self._thread_local.raw_payloads.append(payload)


def miana_symbol(symbol: str) -> str:
    code, _, suffix = symbol.partition(".")
    suffix = suffix.upper()
    if suffix == "SH":
        return f"sh{code}"
    if suffix == "SZ":
        return f"sz{code}"
    if suffix == "BJ":
        return f"bj{code}"
    if symbol.startswith(("sh", "sz", "bj", "hk", "us")):
        return symbol
    if code.startswith("6"):
        return f"sh{code}"
    if code.startswith(("0", "3")):
        return f"sz{code}"
    return code


def normalized_symbol(row: dict) -> str:
    code = str(row.get("code") or "")
    exchange_code = row.get("exchangeCode")
    suffix = {"XSHG": "SH", "XSHE": "SZ", "BJSE": "BJ"}.get(exchange_code)
    if suffix:
        return f"{code}.{suffix}"
    if code.startswith("6"):
        return f"{code}.SH"
    if code.startswith(("0", "3")):
        return f"{code}.SZ"
    if code.startswith(("4", "8")):
        return f"{code}.BJ"
    return code


def _market_symbol(row: dict) -> str:
    code = str(row.get("code") or row.get("symbol") or "")
    exchange_code = row.get("exchangeCode")
    if not code:
        return ""
    if code.startswith(("sh", "sz", "bj", "hk", "us")):
        return code
    prefix = {"XSHG": "sh", "XSHE": "sz", "BJSE": "bj", "XHKG": "hk"}.get(exchange_code, "")
    return f"{prefix}{code}" if prefix else code


def _first_value(row: dict, *keys: str):
    for key in keys:
        value = row.get(key)
        if value is not None:
            return value
    return None


def _data(payload: dict) -> list[dict]:
    data = payload.get("data") or []
    return data if isinstance(data, list) else []


def _company_profile_rows(payload: dict) -> list[dict]:
    data = payload.get("data") or []
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _shareholder_rows(payload: dict) -> list[dict]:
    data = payload.get("data") or {}
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if not isinstance(data, dict):
        return []
    rows = data.get("shareholders") or data.get("holders") or []
    return [row for row in rows if isinstance(row, dict)]


def _list_data(payload: dict) -> list[dict]:
    data = payload.get("data") or []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        rows = data.get("list") or data.get("items") or data.get("data") or []
        return rows if isinstance(rows, list) else []
    return []


def _normalize_quote_row(row: dict) -> dict:
    return {
        "symbol": normalized_symbol(row),
        "name": row.get("name") or normalized_symbol(row),
        "exchange": _exchange_from_symbol(normalized_symbol(row)),
        "trade_date": _date(row.get("localDate") or row.get("date")),
        "price": _number_value(_first_value(row, "price", "close")),
        "close": _number_value(_first_value(row, "price", "close")),
        "pre_close": _number_value(row.get("preClose")),
        "open": _number_value(row.get("open")),
        "high": _number_value(row.get("high")),
        "low": _number_value(row.get("low")),
        "change": _number_value(row.get("change")),
        "change_rate": _ratio_value(row.get("changeRate")),
        "volume": _number_value(row.get("volume")),
        "amount": _number_value(row.get("amount")),
        "turnover": _number_value(row.get("turnover")),
        "market_value": _first_value(row, "mktCap", "marketValue"),
        "circulation_value": _first_value(row, "floatCap", "circulationValue"),
        "total_shares": _first_value(row, "totShr", "totalShares"),
        "circulation_shares": _first_value(row, "floatShr", "circulationShares"),
        "source": "miana",
        "raw_json": dict(row),
    }


def _normalize_market_quote_row(row: dict, code_key: str) -> dict:
    code = _market_symbol(row) if code_key == "index_code" else str(row.get("code") or row.get("symbol") or "")
    return {
        code_key: code,
        "name": row.get("name") or code,
        "trade_date": _date(row.get("date")),
        "price": _first_value(row, "price", "close"),
        "pre_close": row.get("preClose"),
        "open": row.get("open"),
        "high": row.get("high"),
        "low": row.get("low"),
        "change": row.get("change"),
        "change_rate": _ratio_value(row.get("changeRate")),
        "volume": row.get("volume"),
        "amount": row.get("amount"),
        "source": "miana",
        "raw_json": dict(row),
    }


def _ratio_value(value):
    if value in (None, ""):
        return None
    try:
        return float(value) / 100
    except (TypeError, ValueError):
        return value


def _number_value(value):
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return value
    return int(number) if number.is_integer() else number


def _report_period(row: dict) -> str:
    explicit = row.get("reportPeriod")
    if explicit:
        return str(explicit)
    fiscal_year = row.get("fiscalYear")
    fiscal_period = row.get("fiscalPeriod")
    if fiscal_year and fiscal_period:
        return f"{fiscal_year}{fiscal_period}"
    return str(row.get("reportDate") or "")


def _date(value) -> str | None:
    if value in (None, ""):
        return None
    return str(value)[:10]


def _looks_like_date(value) -> bool:
    if value in (None, ""):
        return False
    text = str(value)
    if len(text) < 10:
        return False
    try:
        date.fromisoformat(text[:10])
        return True
    except ValueError:
        return False


def _date_segments(start_date: str, end_date: str, max_days: int = 700) -> list[tuple[str, str]]:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    segments = []
    current = start
    while current <= end:
        segment_end = min(current + timedelta(days=max_days - 1), end)
        segments.append((current.isoformat(), segment_end.isoformat()))
        current = segment_end + timedelta(days=1)
    return segments


def _exchange_from_symbol(symbol: str) -> str:
    if symbol.endswith(".SH"):
        return "SH"
    if symbol.endswith(".SZ"):
        return "SZ"
    if symbol.endswith(".BJ"):
        return "BJ"
    return "UNKNOWN"
