import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { projectsApi } from '../api'
import ApiHint from '../components/ApiHint'
import { EmptyState, ErrorBanner, Modal } from '../components/ui'
import { useAuth } from '../context/AuthContext'

export default function Projects() {
  const { user } = useAuth()
  const [projects, setProjects] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ name: '', description: '' })
  const [busy, setBusy] = useState(false)

  const canCreate = user?.role === 'ADMIN' || user?.role === 'PM'

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await projectsApi.list()
      setProjects(Array.isArray(data) ? data : data.results || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const create = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await projectsApi.create(form)
      setShowCreate(false)
      setForm({ name: '', description: '' })
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Projects</h1>
          <p className="muted">
            Select a project to open its board
            <ApiHint method="GET" path="/api/projects/" />
          </p>
        </div>
        {canCreate && (
          <button type="button" className="btn btn-primary" onClick={() => setShowCreate(true)}>
            Create project
            <ApiHint method="POST" path="/api/projects/" />
          </button>
        )}
      </div>

      <ErrorBanner message={error} onDismiss={() => setError('')} />

      {loading ? (
        <p className="muted">Loading projects…</p>
      ) : projects.length === 0 ? (
        <EmptyState title="No projects yet" subtitle="Create a project to get started." />
      ) : (
        <div className="project-grid">
          {projects.map((p) => (
            <Link key={p.id} to={`/projects/${p.id}/board`} className="project-card">
              <div className="project-card-top">
                <span className="project-icon">{p.name.slice(0, 1).toUpperCase()}</span>
                <div>
                  <div className="project-name">{p.name}</div>
                  <div className="muted small">
                    Owner: {p.owner?.email || '—'} · {p.task_count ?? 0} issues ·{' '}
                    {p.member_count ?? 0} members
                  </div>
                </div>
              </div>
              <p className="project-desc">{p.description || 'No description'}</p>
            </Link>
          ))}
        </div>
      )}

      {showCreate && (
        <Modal title="Create project" onClose={() => setShowCreate(false)}>
          <form onSubmit={create} className="stack">
            <label className="field">
              <span>Name</span>
              <input
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                required
              />
            </label>
            <label className="field">
              <span>Description</span>
              <textarea
                rows={3}
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              />
            </label>
            <div className="row end">
              <button type="button" className="btn" onClick={() => setShowCreate(false)}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={busy}>
                Create
                <ApiHint method="POST" path="/api/projects/" />
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
