import { useEffect, useState } from 'react'
import { commentsApi, projectsApi, tasksApi } from '../api'
import ApiHint from '../components/ApiHint'
import { ErrorBanner, Modal, PriorityBadge, StatusBadge } from '../components/ui'
import { useAuth } from '../context/AuthContext'

export default function TaskDetail({ taskId, onClose, onChanged }) {
  const { user } = useAuth()
  const [task, setTask] = useState(null)
  const [comments, setComments] = useState([])
  const [members, setMembers] = useState([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [edit, setEdit] = useState(null)
  const [commentBody, setCommentBody] = useState('')
  const [replyTo, setReplyTo] = useState(null)

  const load = async () => {
    setError('')
    try {
      const t = await tasksApi.get(taskId)
      setTask(t)
      setEdit({
        title: t.title,
        description: t.description || '',
        status: t.status,
        priority: t.priority,
        assignee_id: t.assignee?.id ?? '',
        due_date: t.due_date || '',
      })
      const [commentList, memberList] = await Promise.all([
        commentsApi.list({ target_type: 'task', target_id: taskId }),
        projectsApi.listMembers(t.project),
      ])
      setComments(Array.isArray(commentList) ? commentList : commentList.results || [])
      setMembers(Array.isArray(memberList) ? memberList : memberList.results || [])
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    load()
  }, [taskId])

  const save = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const payload = {
        title: edit.title,
        description: edit.description,
        status: edit.status,
        priority: edit.priority,
        due_date: edit.due_date || null,
        assignee_id: edit.assignee_id === '' ? null : Number(edit.assignee_id),
      }
      await tasksApi.update(taskId, payload)
      await load()
      onChanged?.()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const remove = async () => {
    if (!confirm('Delete this issue?')) return
    setBusy(true)
    try {
      await tasksApi.remove(taskId)
      onChanged?.()
      onClose()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const postComment = async (e) => {
    e.preventDefault()
    if (!commentBody.trim()) return
    setBusy(true)
    setError('')
    try {
      const body = replyTo
        ? { body: commentBody, parent: replyTo }
        : { body: commentBody, target_type: 'task', target_id: Number(taskId) }
      await commentsApi.create(body)
      setCommentBody('')
      setReplyTo(null)
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const deleteComment = async (id) => {
    try {
      await commentsApi.remove(id)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  if (!task || !edit) {
    return (
      <Modal title="Issue" onClose={onClose} wide>
        <p className="muted">Loading…</p>
      </Modal>
    )
  }

  return (
    <Modal title={`TM-${task.id}`} onClose={onClose} wide>
      <ErrorBanner message={error} onDismiss={() => setError('')} />

      <div className="issue-layout">
        <div className="issue-main">
          <form onSubmit={save} className="stack" id="issue-form">
            <label className="field">
              <span>Summary</span>
              <input
                value={edit.title}
                onChange={(e) => setEdit((f) => ({ ...f, title: e.target.value }))}
                required
              />
            </label>
            <label className="field">
              <span>Description</span>
              <textarea
                rows={5}
                value={edit.description}
                onChange={(e) => setEdit((f) => ({ ...f, description: e.target.value }))}
              />
            </label>
          </form>

          <div className="section">
            <h3>
              Comments
              <ApiHint
                method="GET"
                path={`/api/comments/?target_type=task&target_id=${taskId}`}
              />
            </h3>

            <div className="comment-list">
              {comments.length === 0 && <p className="muted">No comments yet.</p>}
              {comments.map((c) => (
                <div key={c.id} className="comment">
                  <div className="comment-head">
                    <strong>{c.author?.username || c.author?.email}</strong>
                    <span className="muted small">
                      {new Date(c.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p>{c.body}</p>
                  <div className="row">
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      onClick={() => setReplyTo(c.id)}
                    >
                      Reply
                    </button>
                    {(user?.id === c.author?.id || user?.role === 'ADMIN') && (
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm danger"
                        onClick={() => deleteComment(c.id)}
                      >
                        Delete
                        <ApiHint method="DELETE" path={`/api/comments/${c.id}/`} />
                      </button>
                    )}
                  </div>
                  {c.replies?.map((r) => (
                    <div key={r.id} className="comment reply">
                      <div className="comment-head">
                        <strong>{r.author?.username || r.author?.email}</strong>
                        <span className="muted small">
                          {new Date(r.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p>{r.body}</p>
                    </div>
                  ))}
                </div>
              ))}
            </div>

            <form onSubmit={postComment} className="stack comment-form">
              {replyTo && (
                <div className="row">
                  <span className="muted small">Replying to comment #{replyTo}</span>
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    onClick={() => setReplyTo(null)}
                  >
                    Cancel reply
                  </button>
                </div>
              )}
              <textarea
                rows={3}
                placeholder="Add a comment… Use @username to mention"
                value={commentBody}
                onChange={(e) => setCommentBody(e.target.value)}
              />
              <div className="row end">
                <button type="submit" className="btn btn-primary btn-sm" disabled={busy}>
                  Comment
                  <ApiHint method="POST" path="/api/comments/" />
                </button>
              </div>
            </form>
          </div>
        </div>

        <aside className="issue-side">
          <div className="side-block">
            <div className="muted small">Status</div>
            <select
              form="issue-form"
              value={edit.status}
              onChange={(e) => setEdit((f) => ({ ...f, status: e.target.value }))}
            >
              <option value="TODO">To Do</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="DONE">Done</option>
            </select>
            <StatusBadge status={edit.status} />
          </div>

          <div className="side-block">
            <div className="muted small">Priority</div>
            <select
              form="issue-form"
              value={edit.priority}
              onChange={(e) => setEdit((f) => ({ ...f, priority: e.target.value }))}
            >
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
            <PriorityBadge priority={edit.priority} />
          </div>

          <div className="side-block">
            <div className="muted small">Assignee</div>
            <select
              form="issue-form"
              value={edit.assignee_id}
              onChange={(e) => setEdit((f) => ({ ...f, assignee_id: e.target.value }))}
            >
              <option value="">Unassigned</option>
              {members.map((m) => (
                <option key={m.user_id} value={m.user_id}>
                  {m.email}
                </option>
              ))}
            </select>
            <ApiHint method="GET" path={`/api/projects/${task.project}/members/`} />
          </div>

          <div className="side-block">
            <div className="muted small">Due date</div>
            <input
              form="issue-form"
              type="date"
              value={edit.due_date}
              onChange={(e) => setEdit((f) => ({ ...f, due_date: e.target.value }))}
            />
          </div>

          <div className="side-block muted small">
            Reporter: {task.created_by?.email || '—'}
            <br />
            Created: {new Date(task.created_at).toLocaleString()}
          </div>

          <div className="stack">
            <button type="submit" form="issue-form" className="btn btn-primary" disabled={busy}>
              Save changes
              <ApiHint method="PATCH" path={`/api/tasks/${taskId}/`} />
            </button>
            <button type="button" className="btn btn-danger" disabled={busy} onClick={remove}>
              Delete issue
              <ApiHint method="DELETE" path={`/api/tasks/${taskId}/`} />
            </button>
          </div>
        </aside>
      </div>
    </Modal>
  )
}
