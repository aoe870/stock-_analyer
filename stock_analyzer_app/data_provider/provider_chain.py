from dataclasses import dataclass

from stock_analyzer_app.config.settings import AppSettings
from stock_analyzer_app.data_provider.akshare_provider import AkShareProvider
from stock_analyzer_app.data_provider.base import StockDataProvider
from stock_analyzer_app.data_provider.eastmoney_provider import EastmoneyProvider
from stock_analyzer_app.data_provider.tushare_provider import TushareProvider


@dataclass(frozen=True)
class ProviderChain:
    providers: list[StockDataProvider]


def build_provider_chain(settings: AppSettings) -> ProviderChain:
    providers: list[StockDataProvider] = []
    for name in settings.provider_priority:
        if name == "tushare" and not settings.tushare_token:
            continue
        if name == "tushare":
            providers.append(TushareProvider(settings.tushare_token))
        elif name == "akshare":
            providers.append(AkShareProvider())
        elif name == "eastmoney":
            providers.append(EastmoneyProvider())
    return ProviderChain(providers)
