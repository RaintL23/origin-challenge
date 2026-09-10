from __future__ import annotations

from datetime import date
from typing import Any, Literal

import httpx
from fastapi import HTTPException, status

from app.config import Settings
from app.schemas.stocks import StockInfo, StockSearchItem, TimeSeriesPoint, TimeSeriesResponse

Interval = Literal["1min", "5min", "15min"]
Mode = Literal["realtime", "historical"]


class TwelveDataClient:
    BASE_URL = "https://api.twelvedata.com"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _ensure_api_key(self) -> str:
        api_key = self.settings.twelve_data_api_key.strip()
        if not api_key or api_key == "your_api_key_here":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="TWELVE_DATA_API_KEY no configurada",
            )
        return api_key

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        api_key = self._ensure_api_key()
        query = {**params, "apikey": api_key}
        async with httpx.AsyncClient(base_url=self.BASE_URL, timeout=30.0) as client:
            response = await client.get(path, params=query)
            response.raise_for_status()
            payload = response.json()

        if isinstance(payload, dict) and payload.get("status") == "error":
            message = payload.get("message") or "Error en Twelve Data"
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=message,
            )
        return payload

    async def search_stocks(self, query: str, limit: int = 20) -> list[StockSearchItem]:
        payload = await self._get("/stocks", {"exchange": "NYSE", "source": "docs"})
        data = payload.get("data", []) if isinstance(payload, dict) else []
        needle = query.strip().lower()
        matches: list[StockSearchItem] = []

        for item in data:
            symbol = str(item.get("symbol") or "")
            name = str(item.get("name") or "")
            if needle and needle not in symbol.lower() and needle not in name.lower():
                continue
            matches.append(
                StockSearchItem(
                    symbol=symbol,
                    name=name,
                    currency=str(item.get("currency") or "USD"),
                    exchange=item.get("exchange"),
                    country=item.get("country"),
                )
            )
            if len(matches) >= limit:
                break

        return matches

    async def get_stock(self, symbol: str) -> StockInfo:
        payload = await self._get(
            "/stocks",
            {"symbol": symbol.upper(), "source": "docs"},
        )
        data = payload.get("data", []) if isinstance(payload, dict) else []
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Símbolo no encontrado: {symbol}",
            )

        item = data[0]
        return StockInfo(
            symbol=str(item.get("symbol") or symbol.upper()),
            name=str(item.get("name") or symbol.upper()),
            currency=str(item.get("currency") or "USD"),
            exchange=item.get("exchange"),
            country=item.get("country"),
            type=item.get("type"),
        )

    async def get_timeseries(
        self,
        symbol: str,
        *,
        mode: Mode,
        interval: Interval,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> TimeSeriesResponse:
        params: dict[str, Any] = {
            "symbol": symbol.upper(),
            "interval": interval,
        }

        if mode == "realtime":
            today = date.today().isoformat()
            params["start_date"] = f"{today} 00:00:00"
            params["end_date"] = f"{today} 23:59:59"
        else:
            if not start_date or not end_date:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="start_date y end_date son requeridos en modo historical",
                )
            params["start_date"] = start_date
            params["end_date"] = end_date

        payload = await self._get("/time_series", params)
        raw_values = payload.get("values", []) if isinstance(payload, dict) else []
        points: list[TimeSeriesPoint] = []

        for row in raw_values:
            points.append(
                TimeSeriesPoint(
                    datetime=str(row.get("datetime") or ""),
                    open=_to_float(row.get("open")),
                    high=_to_float(row.get("high")),
                    low=_to_float(row.get("low")),
                    close=_to_float(row.get("close")),
                    volume=_to_float(row.get("volume")),
                )
            )

        # Twelve Data returns newest first; chart UIs usually prefer chronological order.
        points.reverse()

        return TimeSeriesResponse(
            symbol=symbol.upper(),
            interval=interval,
            mode=mode,
            values=points,
        )


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
