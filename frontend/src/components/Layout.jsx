import { NavLink, Outlet, useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import ApiHint from './ApiHint'
import './Layout.css'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { projectId } = useParams()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const displayName = user?.profile?.display_name || user?.username || user?.email
  const initials = (displayName?.[0] || '?').toUpperCase()
  const avatarUrl = user?.profile?.avatar_url

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-mark">TM</span>
          <span className="brand-name">TaskBoard</span>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section-label">Workspace</div>
          <NavLink
            to="/organizations"
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            Organizations
          </NavLink>
          <NavLink
            to="/profile"
            className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
          >
            Profile
          </NavLink>
          {user?.role === 'ADMIN' && (
            <NavLink
              to="/users"
              className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
            >
              Users
            </NavLink>
          )}

          {projectId && (
            <>
              <div className="nav-section-label">Project</div>
              <NavLink
                to={`/projects/${projectId}/board`}
                className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
              >
                Board
              </NavLink>
              <NavLink
                to={`/projects/${projectId}/backlog`}
                className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
              >
                Backlog
              </NavLink>
              <NavLink
                to={`/projects/${projectId}/settings`}
                className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
              >
                Settings
              </NavLink>
            </>
          )}
        </nav>

        <div className="sidebar-footer">
          <div className="user-chip">
            {avatarUrl ? (
              <img
                src={avatarUrl}
                alt={displayName}
                className="avatar"
                style={{ objectFit: 'cover' }}
              />
            ) : (
              <span className="avatar">{initials}</span>
            )}
            <div className="user-meta">
              <div className="user-name">{displayName}</div>
              <div className="user-role">{user?.role}</div>
            </div>
          </div>
          <button type="button" className="btn btn-ghost btn-sm logout-btn" onClick={handleLogout}>
            Log out
            <ApiHint method="POST" path="/api/users/auth/logout/" />
          </button>
        </div>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <div className="topbar-title">Task Manager</div>
          <div className="topbar-right">
            <span className="muted">{user?.email}</span>
          </div>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}