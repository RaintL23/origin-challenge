import Highcharts from 'highcharts'
import { HighchartsReact } from 'highcharts-react-official'
import type { TimeSeriesPoint } from '../types/api'

interface PriceChartProps {
  symbol: string
  values: TimeSeriesPoint[]
}

export function PriceChart({ symbol, values }: PriceChartProps) {
  const seriesData = [...values]
    .reverse()
    .filter((point) => point.close != null)
    .map((point) => [Date.parse(point.datetime.replace(' ', 'T')), point.close as number])

  const options: Highcharts.Options = {
    chart: {
      type: 'line',
      height: 420,
      backgroundColor: 'transparent',
    },
    title: {
      text: `${symbol} — Cotización`,
    },
    xAxis: {
      type: 'datetime',
      title: { text: 'Fecha / hora' },
    },
    yAxis: {
      title: { text: 'Precio de cierre' },
    },
    legend: { enabled: false },
    credits: { enabled: false },
    tooltip: {
      xDateFormat: '%Y-%m-%d %H:%M',
      valueDecimals: 2,
    },
    series: [
      {
        type: 'line',
        name: 'Close',
        data: seriesData,
      },
    ],
  }

  if (seriesData.length === 0) {
    return <p className="empty-state">No hay datos para graficar con los parámetros elegidos.</p>
  }

  return (
    <div className="price-chart">
      <HighchartsReact highcharts={Highcharts} options={options} />
    </div>
  )
}
