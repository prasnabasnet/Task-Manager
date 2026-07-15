import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { projectsApi } from '../api'
import ApiHint from '../components/ApiHint'
import { ErrorBanner, Modal } from '../components/ui'

export default function ProjectSettings() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [members, setMembers] = useState([])
  const [form, setForm] = useState({ name: '', description: '' })
  const [userId, setUserId] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)

  const load = async () => {
    setError('')
    try {
      const [proj, memberList] = await Promise.all([
        projectsApi.get(projectId),
        projectsApi.listMembers(projectId),
      ])
      setProject(proj)
      setForm({ name: proj.name, description: proj.description || '' })
      setMembers(Array.isArray(memberList) ? memberList : memberList.results || [])
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    load()
  }, [projectId])

  const save = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await projectsApi.update(projectId, form)
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const addMember = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await projectsApi.addMember(projectId, Number(userId))
      setUserId('')
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const removeMember = async (uid) => {
    setBusy(true)
    try {
      await projectsApi.removeMember(projectId, uid)
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const removeProject = async () => {
    setBusy(true)
    try {
      await projectsApi.remove(projectId)
      navigate('/')
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={() => navigate(`/projects/${projectId}/board`)}
          >
            ← Board
          </button>
          <h1>Project settings</h1>
          <p className="muted">
            {project?.name}
            <ApiHint method="GET" path={`/api/projects/${projectId}/`} />
          </p>
        </div>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError('')} />

      <div className="settings-grid">
        <section className="panel">
          <h2>Details</h2>
          <form onSubmit={save} className="stack">
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
            <button type="submit" className="btn btn-primary" disabled={busy}>
              Save
              <ApiHint method="PATCH" path={`/api/projects/${projectId}/`} />
            </button>
          </form>
        </section>

        <section className="panel">
          <h2>
            People
            <ApiHint method="GET" path={`/api/projects/${projectId}/members/`} />
          </h2>
          <ul className="member-list">
            {members.map((m) => (
              <li key={m.user_id}>
                <div>
                  <strong>{m.email}</strong>
                  <div className="muted small">{m.role}</div>
                </div>
                <button
                  type="button"
                  className="btn btn-ghost btn-sm danger"
                  onClick={() => removeMember(m.user_id)}
                >
                  Remove
                  <ApiHint
                    method="DELETE"
                    path={`/api/projects/${projectId}/members/${m.user_id}/`}
                  />
                </button>
              </li>
            ))}
          </ul>

          <form onSubmit={addMember} className="row">
            <input
              type="number"
              placeholder="User ID"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              required
            />
            <button type="submit" className="btn btn-primary" disabled={busy}>
              Add member
              <ApiHint method="POST" path={`/api/projects/${projectId}/members/`} />
            </button>
          </form>
        </section>

        <section className="panel danger-zone">
          <h2>Danger zone</h2>
          <p className="muted">Delete this project and all of its issues permanently.</p>
          <button type="button" className="btn btn-danger" onClick={() => setConfirmDelete(true)}>
            Delete project
            <ApiHint method="DELETE" path={`/api/projects/${projectId}/`} />
          </button>
        </section>
      </div>

      {confirmDelete && (
        <Modal title="Delete project?" onClose={() => setConfirmDelete(false)}>
          <p>This cannot be undone.</p>
          <div className="row end">
            <button type="button" className="btn" onClick={() => setConfirmDelete(false)}>
              Cancel
            </button>
            <button type="button" className="btn btn-danger" disabled={busy} onClick={removeProject}>
              Delete
            </button>
          </div>
        </Modal>
      )}
    </div>
  )
}
