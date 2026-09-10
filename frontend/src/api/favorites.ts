import { apiRequest } from './client'
import type { FavoriteCreate, FavoriteStock } from '../types/api'

export function listFavorites(token: string): Promise<FavoriteStock[]> {
  return apiRequest<FavoriteStock[]>('/favorites', { token })
}

export function createFavorite(
  token: string,
  payload: FavoriteCreate,
): Promise<FavoriteStock> {
  return apiRequest<FavoriteStock>('/favorites', {
    method: 'POST',
    token,
    body: payload,
  })
}

export function deleteFavorite(token: string, symbol: string): Promise<void> {
  return apiRequest<void>(`/favorites/${encodeURIComponent(symbol)}`, {
    method: 'DELETE',
    token,
  })
}
