import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createFavorite, deleteFavorite, listFavorites } from '../api/favorites'
import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { Autocomplete } from '../components/Autocomplete'
import { Header } from '../components/Header'
import { StockGrid } from '../components/StockGrid'
import type { StockSearchItem } from '../types/api'

export function FavoritesPage() {
  const { token } = useAuth()
  const queryClient = useQueryClient()
  const [selected, setSelected] = useState<StockSearchItem | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  const favoritesQuery = useQuery({
    queryKey: ['favorites'],
    queryFn: () => listFavorites(token!),
    enabled: Boolean(token),
  })

  const addMutation = useMutation({
    mutationFn: (item: StockSearchItem) =>
      createFavorite(token!, {
        symbol: item.symbol,
        name: item.name,
        currency: item.currency,
      }),
    onSuccess: async () => {
      setSelected(null)
      setActionError(null)
      await queryClient.invalidateQueries({ queryKey: ['favorites'] })
    },
    onError: (err: unknown) => {
      setActionError(err instanceof ApiError ? err.message : 'No se pudo agregar el símbolo')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (symbol: string) => deleteFavorite(token!, symbol),
    onSuccess: async () => {
      setActionError(null)
      await queryClient.invalidateQueries({ queryKey: ['favorites'] })
    },
    onError: (err: unknown) => {
      setActionError(err instanceof ApiError ? err.message : 'No se pudo eliminar el símbolo')
    },
  })

  function handleAdd() {
    if (!selected) {
      setActionError('Seleccioná un símbolo del autocomplete')
      return
    }
    addMutation.mutate(selected)
  }

  return (
    <div className="page">
      <Header title="Mis Acciones" />
      <main className="page__content">
        <section className="panel">
          <h2>Agregar símbolo</h2>
          <div className="add-row">
            <Autocomplete selected={selected} onSelect={setSelected} />
            <button
              type="button"
              className="btn btn--primary"
              onClick={handleAdd}
              disabled={addMutation.isPending}
            >
              {addMutation.isPending ? 'Agregando...' : 'Agregar símbolo'}
            </button>
          </div>
          {actionError && <p className="form-error">{actionError}</p>}
        </section>

        <section className="panel">
          <h2>Preferidas</h2>
          {favoritesQuery.isLoading && <p className="muted">Cargando...</p>}
          {favoritesQuery.isError && (
            <p className="form-error">
              {favoritesQuery.error instanceof ApiError
                ? favoritesQuery.error.message
                : 'No se pudieron cargar las preferidas'}
            </p>
          )}
          {favoritesQuery.data && (
            <StockGrid
              items={favoritesQuery.data}
              onDelete={(symbol) => deleteMutation.mutate(symbol)}
              deletingSymbol={deleteMutation.isPending ? deleteMutation.variables : null}
            />
          )}
        </section>
      </main>
    </div>
  )
}
