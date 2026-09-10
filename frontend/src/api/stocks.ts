import { apiRequest } from './client'
import type {
  ChartMode,
  Interval,
  StockInfo,
  StockSearchItem,
  TimeSeriesResponse,
} from '../types/api'

export function searchStocks(token: string, q: string): Promise<StockSearchItem[]> {
  const params = new URLSearchParams({ q })
  return apiRequest<StockSearchItem[]>(`/stocks/search?${params}`, { token })
}

export function getStock(token: string, symbol: string): Promise<StockInfo> {
  return apiRequest<StockInfo>(`/stocks/${encodeURIComponent(symbol)}`, { token })
}

export function getTimeseries(
  token: string,
  symbol: string,
  params: {
    mode: ChartMode
    interval: Interval
    start_date?: string
    end_date?: string
  },
): Promise<TimeSeriesResponse> {
  const query = new URLSearchParams({
    mode: params.mode,
    interval: params.interval,
  })
  if (params.start_date) query.set('start_date', params.start_date)
  if (params.end_date) query.set('end_date', params.end_date)

  return apiRequest<TimeSeriesResponse>(
    `/stocks/${encodeURIComponent(symbol)}/timeseries?${query}`,
    { token },
  )
}
