import { useEffect, useId, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { searchStocks } from '../api/stocks'
import { useAuth } from '../auth/AuthContext'
import type { StockSearchItem } from '../types/api'

interface AutocompleteProps {
  onSelect: (item: StockSearchItem | null) => void
  selected: StockSearchItem | null
}

export function Autocomplete({ onSelect, selected }: AutocompleteProps) {
  const { token } = useAuth()
  const listId = useId()
  const containerRef = useRef<HTMLDivElement>(null)
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const [debouncedQuery, setDebouncedQuery] = useState('')

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedQuery(query.trim()), 300)
    return () => window.clearTimeout(timer)
  }, [query])

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    if (!selected) return
    setQuery('')
  }, [selected])

  const searchQuery = useQuery({
    queryKey: ['stocks-search', debouncedQuery],
    queryFn: () => searchStocks(token!, debouncedQuery),
    enabled: Boolean(token) && debouncedQuery.length >= 1,
  })

  const results = searchQuery.data ?? []
  const displayValue =
    selected && query === '' ? `${selected.symbol} — ${selected.name}` : query

  return (
    <div className="autocomplete" ref={containerRef}>
      <label htmlFor="stock-search">Buscar acción</label>
      <div className="autocomplete__field">
        <input
          id="stock-search"
          type="text"
          role="combobox"
          aria-expanded={open}
          aria-controls={listId}
          aria-autocomplete="list"
          placeholder="Ej: JPM, DIS, KO..."
          value={displayValue}
          onChange={(event) => {
            setQuery(event.target.value)
            setOpen(true)
            if (selected) onSelect(null)
          }}
          onFocus={() => setOpen(true)}
        />
        {open && debouncedQuery.length >= 1 && (
          <ul id={listId} className="autocomplete__list" role="listbox">
            {searchQuery.isFetching && <li className="autocomplete__empty">Buscando...</li>}
            {searchQuery.isError && (
              <li className="autocomplete__empty">No se pudo buscar. Intentá de nuevo.</li>
            )}
            {!searchQuery.isFetching && !searchQuery.isError && results.length === 0 && (
              <li className="autocomplete__empty">Sin coincidencias</li>
            )}
            {results.map((item) => (
              <li key={`${item.symbol}-${item.exchange ?? ''}`}>
                <button
                  type="button"
                  className="autocomplete__option"
                  role="option"
                  onClick={() => {
                    onSelect(item)
                    setQuery('')
                    setOpen(false)
                  }}
                >
                  <strong>{item.symbol}</strong>
                  <span>
                    {item.name} · {item.currency}
                    {item.exchange ? ` · ${item.exchange}` : ''}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <p className="autocomplete__hint">
        La búsqueda solo incluye acciones del exchange <strong>NYSE</strong> (fuente Twelve
        Data). Ejemplos válidos: <strong>JPM</strong>, <strong>DIS</strong>, <strong>KO</strong>,{' '}
        <strong>NKE</strong>, <strong>V</strong>, <strong>BAC</strong>, <strong>PEP</strong>,{' '}
        <strong>AAP</strong>. Símbolos de NASDAQ como TSLA o AAPL no aparecerán.
      </p>
    </div>
  )
}
