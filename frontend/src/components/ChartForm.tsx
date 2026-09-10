import type { ChartMode, Interval } from '../types/api'

export interface ChartFormValues {
  mode: ChartMode
  interval: Interval
  startDate: string
  endDate: string
}

interface ChartFormProps {
  values: ChartFormValues
  onChange: (values: ChartFormValues) => void
  onSubmit: () => void
  loading?: boolean
  error?: string | null
}

const INTERVALS: Interval[] = ['1min', '5min', '15min']

export function ChartForm({ values, onChange, onSubmit, loading, error }: ChartFormProps) {
  return (
    <form
      className="chart-form"
      onSubmit={(event) => {
        event.preventDefault()
        onSubmit()
      }}
    >
      <fieldset>
        <legend>Modo</legend>
        <label className="radio">
          <input
            type="radio"
            name="mode"
            checked={values.mode === 'realtime'}
            onChange={() => onChange({ ...values, mode: 'realtime' })}
          />
          Tiempo real
        </label>
        <label className="radio">
          <input
            type="radio"
            name="mode"
            checked={values.mode === 'historical'}
            onChange={() => onChange({ ...values, mode: 'historical' })}
          />
          Histórico
        </label>
      </fieldset>

      <label>
        Intervalo
        <select
          value={values.interval}
          onChange={(event) =>
            onChange({ ...values, interval: event.target.value as Interval })
          }
        >
          {INTERVALS.map((interval) => (
            <option key={interval} value={interval}>
              {interval}
            </option>
          ))}
        </select>
      </label>

      {values.mode === 'historical' && (
        <div className="chart-form__range">
          <label>
            Desde
            <input
              type="datetime-local"
              value={values.startDate}
              onChange={(event) => onChange({ ...values, startDate: event.target.value })}
              required
            />
          </label>
          <label>
            Hasta
            <input
              type="datetime-local"
              value={values.endDate}
              onChange={(event) => onChange({ ...values, endDate: event.target.value })}
              required
            />
          </label>
        </div>
      )}

      {error && <p className="form-error">{error}</p>}

      <button type="submit" className="btn btn--primary" disabled={loading}>
        {loading ? 'Cargando...' : 'Graficar'}
      </button>
    </form>
  )
}
