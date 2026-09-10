import { Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { FavoritesPage } from './pages/FavoritesPage'
import { LoginPage } from './pages/LoginPage'
import { StockDetailPage } from './pages/StockDetailPage'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/acciones" element={<FavoritesPage />} />
        <Route path="/acciones/:symbol" element={<StockDetailPage />} />
      </Route>
      <Route path="/" element={<Navigate to="/acciones" replace />} />
      <Route path="*" element={<Navigate to="/acciones" replace />} />
    </Routes>
  )
}
