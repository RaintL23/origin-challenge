from app.integrations.twelvedata import Interval, Mode, TwelveDataClient
from app.schemas.stocks import StockInfo, StockSearchItem, TimeSeriesResponse


class StockService:
    def __init__(self, client: TwelveDataClient) -> None:
        self.client = client

    async def search(self, query: str) -> list[StockSearchItem]:
        return await self.client.search_stocks(query)

    async def get_stock(self, symbol: str) -> StockInfo:
        return await self.client.get_stock(symbol)

    async def get_timeseries(
        self,
        symbol: str,
        *,
        mode: Mode,
        interval: Interval,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> TimeSeriesResponse:
        return await self.client.get_timeseries(
            symbol,
            mode=mode,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )
