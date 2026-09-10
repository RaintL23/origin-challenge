import { Link } from 'react-router-dom'
import type { FavoriteStock } from '../types/api'

interface StockGridProps {
  items: FavoriteStock[]
  onDelete: (symbol: string) => void
  deletingSymbol?: string | null
}

export function StockGrid({ items, onDelete, deletingSymbol }: StockGridProps) {
  if (items.length === 0) {
    return <p className="empty-state">No tenés acciones preferidas todavía.</p>
  }

  return (
    <div className="table-wrap">
      <table className="stock-grid">
        <thead>
          <tr>
            <th>Símbolo</th>
            <th>Nombre</th>
            <th>Moneda</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td>
                <Link to={`/acciones/${encodeURIComponent(item.symbol)}`} className="symbol-link">
                  {item.symbol}
                </Link>
              </td>
              <td>{item.name}</td>
              <td>{item.currency}</td>
              <td>
                <button
                  type="button"
                  className="link-button"
                  disabled={deletingSymbol === item.symbol}
                  onClick={() => onDelete(item.symbol)}
                >
                  {deletingSymbol === item.symbol ? 'Eliminando...' : 'Eliminar'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
