import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getStock, getTimeseries } from '../api/stocks'
import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { ChartForm, type ChartFormValues } from '../components/ChartForm'
import { Header } from '../components/Header'
import { PriceChart } from '../components/PriceChart'
import type { Interval } from '../types/api'

const POLL_MS: Record<Interval, number> = {
  '1min': 60_000,
  '5min': 5 * 60_000,
  '15min': 15 * 60_000,
}

/** Convierte valor de datetime-local a formato API: `YYYY-MM-DD HH:MM:SS` */
function toApiDateTime(value: string): string {
  if (!value) return value
  const normalized = value.length === 16 ? `${value}:00` : value
  return normalized.replace('T', ' ')
}

export function StockDetailPage() {
  const { symbol = '' } = useParams()
  const decodedSymbol = decodeURIComponent(symbol).toUpperCase()
  const { token } = useAuth()

  const [form, setForm] = useState<ChartFormValues>({
    mode: 'realtime',
    interval: '5min',
    startDate: '',
    endDate: '',
  })
  const [formError, setFormError] = useState<string | null>(null)
  const [activeQuery, setActiveQuery] = useState<{
    mode: ChartFormValues['mode']
    interval: Interval
    startDate?: string
    endDate?: string
  } | null>(null)

  const stockQuery = useQuery({
    queryKey: ['stock', decodedSymbol],
    queryFn: () => getStock(token!, decodedSymbol),
    enabled: Boolean(token && decodedSymbol),
  })

  const timeseriesQuery = useQuery({
    queryKey: ['timeseries', decodedSymbol, activeQuery],
    queryFn: () =>
      getTimeseries(token!, decodedSymbol, {
        mode: activeQuery!.mode,
        interval: activeQuery!.interval,
        start_date: activeQuery!.startDate,
        end_date: activeQuery!.endDate,
      }),
    enabled: Boolean(token && decodedSymbol && activeQuery),
    refetchInterval:
      activeQuery?.mode === 'realtime' ? POLL_MS[activeQuery.interval] : false,
    refetchIntervalInBackground: false,
  })

  const title = useMemo(() => {
    if (stockQuery.data) {
      return `${stockQuery.data.symbol} — ${stockQuery.data.name}`
    }
    return decodedSymbol
  }, [stockQuery.data, decodedSymbol])

  function handleSubmit() {
    setFormError(null)

    if (form.mode === 'historical') {
      if (!form.startDate || !form.endDate) {
        setFormError('Completá fecha/hora desde y hasta')
        return
      }
      if (form.startDate >= form.endDate) {
        setFormError('La fecha desde debe ser anterior a hasta')
        return
      }
      setActiveQuery({
        mode: 'historical',
        interval: form.interval,
        startDate: toApiDateTime(form.startDate),
        endDate: toApiDateTime(form.endDate),
      })
      return
    }

    setActiveQuery({
      mode: 'realtime',
      interval: form.interval,
    })
  }

  return (
    <div className="page">
      <Header title="Detalle de Acción" />
      <main className="page__content">
        <p>
          <Link to="/acciones" className="back-link">
            ← Volver a Mis Acciones
          </Link>
        </p>

        <section className="panel">
          <h2>{title}</h2>
          {stockQuery.isLoading && <p className="muted">Cargando datos...</p>}
          {stockQuery.isError && (
            <p className="form-error">
              {stockQuery.error instanceof ApiError
                ? stockQuery.error.message
                : 'No se pudo cargar la acción'}
            </p>
          )}
          {stockQuery.data && (
            <dl className="stock-meta">
              <div>
                <dt>Símbolo</dt>
                <dd>{stockQuery.data.symbol}</dd>
              </div>
              <div>
                <dt>Nombre</dt>
                <dd>{stockQuery.data.name}</dd>
              </div>
              <div>
                <dt>Moneda</dt>
                <dd>{stockQuery.data.currency}</dd>
              </div>
              {stockQuery.data.exchange && (
                <div>
                  <dt>Exchange</dt>
                  <dd>{stockQuery.data.exchange}</dd>
                </div>
              )}
            </dl>
          )}
        </section>

        <section className="panel">
          <h2>Parámetros del gráfico</h2>
          <ChartForm
            values={form}
            onChange={(next) => {
              setForm(next)
              // Al pasar a histórico se cancela el polling (activeQuery se reemplaza solo al graficar)
              if (next.mode === 'historical' && activeQuery?.mode === 'realtime') {
                setActiveQuery(null)
              }
            }}
            onSubmit={handleSubmit}
            loading={timeseriesQuery.isFetching}
            error={formError}
          />
          {activeQuery?.mode === 'realtime' && (
            <p className="muted">
              Tiempo real: el gráfico se actualiza cada {activeQuery.interval}.
            </p>
          )}
        </section>

        <section className="panel">
          <h2>Gráfico</h2>
          {!activeQuery && (
            <p className="empty-state">Elegí los parámetros y hacé click en Graficar.</p>
          )}
          {timeseriesQuery.isError && (
            <p className="form-error">
              {timeseriesQuery.error instanceof ApiError
                ? timeseriesQuery.error.message
                : 'No se pudo obtener la serie temporal'}
            </p>
          )}
          {timeseriesQuery.data && (
            <PriceChart symbol={decodedSymbol} values={timeseriesQuery.data.values} />
          )}
        </section>
      </main>
    </div>
  )
}
