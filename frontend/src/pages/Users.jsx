import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { usersApi } from '../api'
import ApiHint from '../components/ApiHint'
import { EmptyState, ErrorBanner } from '../components/ui'
import { useAuth } from '../context/AuthContext'

export default function Users() {
  const { user } = useAuth()
  const [users, setUsers] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    if (user?.role !== 'ADMIN') return
    const load = async () => {
      setError('')
      try {
        const data = await usersApi.list()
        setUsers(Array.isArray(data) ? data : data.results || [])
      } catch (err) {
        setError(err.message)
      }
    }
    load()
  }, [user?.role])

  if (user?.role !== 'ADMIN') return <Navigate to="/" replace />

  const changeRole = async (id, role) => {
    try {
      await usersApi.update(id, { role })
      const data = await usersApi.list()
      setUsers(Array.isArray(data) ? data : data.results || [])
    } catch (err) {
      setError(err.message)
    }
  }

  const deactivate = async (id) => {
    if (!confirm('Deactivate this user?')) return
    try {
      await usersApi.deactivate(id)
      const data = await usersApi.list()
      setUsers(Array.isArray(data) ? data : data.results || [])
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Users</h1>
          <p className="muted">
            Admin user management
            <ApiHint method="GET" path="/api/users/" />
          </p>
        </div>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError('')} />

      {users.length === 0 ? (
        <EmptyState title="No users found" />
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>Username</th>
              <th>Role</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td className="mono">{u.id}</td>
                <td>{u.email}</td>
                <td>{u.username}</td>
                <td>
                  <select
                    value={u.role}
                    onChange={(e) => changeRole(u.id, e.target.value)}
                    disabled={u.id === user.id}
                  >
                    <option value="ADMIN">ADMIN</option>
                    <option value="PM">PM</option>
                    <option value="TM">TM</option>
                  </select>
                  <ApiHint method="PATCH" path={`/api/users/${u.id}/`} />
                </td>
                <td>
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm danger"
                    disabled={u.id === user.id}
                    onClick={() => deactivate(u.id)}
                  >
                    Deactivate
                    <ApiHint method="DELETE" path={`/api/users/${u.id}/`} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
