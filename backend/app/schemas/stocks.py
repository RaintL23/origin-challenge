from typing import Literal

from pydantic import BaseModel, Field


class StockSearchItem(BaseModel):
    symbol: str
    name: str
    currency: str
    exchange: str | None = None
    country: str | None = None


class StockInfo(BaseModel):
    symbol: str
    name: str
    currency: str
    exchange: str | None = None
    country: str | None = None
    type: str | None = None


class TimeSeriesPoint(BaseModel):
    datetime: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None


class TimeSeriesResponse(BaseModel):
    symbol: str
    interval: Literal["1min", "5min", "15min"]
    mode: Literal["realtime", "historical"]
    values: list[TimeSeriesPoint] = Field(default_factory=list)
