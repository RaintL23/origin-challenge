export type Interval = '1min' | '5min' | '15min'
export type ChartMode = 'realtime' | 'historical'

export interface UserPublic {
  id: number
  username: string
  display_name: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserPublic
}

export interface FavoriteStock {
  id: number
  user_id: number
  symbol: string
  name: string
  currency: string
  created_at: string
}

export interface FavoriteCreate {
  symbol: string
  name: string
  currency: string
}

export interface StockSearchItem {
  symbol: string
  name: string
  currency: string
  exchange?: string | null
  country?: string | null
}

export interface StockInfo {
  symbol: string
  name: string
  currency: string
  exchange?: string | null
  country?: string | null
  type?: string | null
}

export interface TimeSeriesPoint {
  datetime: string
  open?: number | null
  high?: number | null
  low?: number | null
  close?: number | null
  volume?: number | null
}

export interface TimeSeriesResponse {
  symbol: string
  interval: Interval
  mode: ChartMode
  values: TimeSeriesPoint[]
}
