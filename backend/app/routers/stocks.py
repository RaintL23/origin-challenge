from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.auth import get_current_user
from app.dependencies import get_stock_service
from app.schemas.auth import UserPublic
from app.schemas.stocks import StockInfo, StockSearchItem, TimeSeriesResponse
from app.services import StockService

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/search", response_model=list[StockSearchItem])
async def search_stocks(
    q: str = Query(min_length=1),
    current_user: UserPublic = Depends(get_current_user),
    service: StockService = Depends(get_stock_service),
) -> list[StockSearchItem]:
    _ = current_user
    return await service.search(q)


@router.get("/{symbol}", response_model=StockInfo)
async def get_stock(
    symbol: str,
    current_user: UserPublic = Depends(get_current_user),
    service: StockService = Depends(get_stock_service),
) -> StockInfo:
    _ = current_user
    return await service.get_stock(symbol)


@router.get("/{symbol}/timeseries", response_model=TimeSeriesResponse)
async def get_timeseries(
    symbol: str,
    mode: Literal["realtime", "historical"] = Query(...),
    interval: Literal["1min", "5min", "15min"] = Query(...),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    current_user: UserPublic = Depends(get_current_user),
    service: StockService = Depends(get_stock_service),
) -> TimeSeriesResponse:
    _ = current_user
    return await service.get_timeseries(
        symbol,
        mode=mode,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
    )
