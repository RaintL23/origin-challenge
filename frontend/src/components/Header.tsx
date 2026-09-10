import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

interface HeaderProps {
  title?: string
}

export function Header({ title = 'Mis Acciones' }: HeaderProps) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="app-header">
      <div className="app-header__left">
        <button type="button" className="app-header__brand" onClick={() => navigate('/acciones')}>
          Challenge Acciones
        </button>
        <h1 className="app-header__title">{title}</h1>
      </div>
      <div className="app-header__right">
        <span className="app-header__user">{user?.display_name ?? user?.username}</span>
        <button type="button" className="btn btn--ghost" onClick={handleLogout}>
          Salir
        </button>
      </div>
    </header>
  )
}
