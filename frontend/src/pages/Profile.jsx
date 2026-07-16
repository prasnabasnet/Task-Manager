import { useEffect, useState } from 'react'
import { authApi } from '../api'
import { useAuth } from '../context/AuthContext'
import { ErrorBanner } from '../components/ui'
import ApiHint from '../components/ApiHint'

export default function Profile() {
  const { user, refresh } = useAuth()
  const [formData, setFormData] = useState({
    display_name: '',
    bio: '',
    avatar_url: '',
    timezone: 'UTC',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (user?.profile) {
      setFormData({
        display_name: user.profile.display_name || '',
        bio: user.profile.bio || '',
        avatar_url: user.profile.avatar_url || '',
        timezone: user.profile.timezone || 'UTC',
      })
    }
  }, [user])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setBusy(true)
    setError('')
    setSuccess('')
    try {
      await authApi.updateProfile(formData)
      await refresh()
      setSuccess('Profile updated successfully!')
    } catch (err) {
      setError(err.message || 'Failed to update profile.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '1rem' }}>
      <div className="page-header">
        <div>
          <h1>My Profile</h1>
          <p className="muted">
            Manage your personal profile details
            <ApiHint method="PATCH" path="/api/users/auth/me/" />
          </p>
        </div>
      </div>

      <ErrorBanner message={error} onDismiss={() => setError('')} />

      {success && (
        <div className="banner success" style={{ marginBottom: '1rem', padding: '0.75rem', borderRadius: '4px', backgroundColor: '#e6fffa', color: '#008b8b', border: '1px solid #b2f5ea' }}>
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="panel stack" style={{ padding: '2rem' }}>
        <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '2rem', alignItems: 'center' }}>
          {formData.avatar_url ? (
            <img
              src={formData.avatar_url}
              alt="Avatar Preview"
              style={{ width: '80px', height: '80px', borderRadius: '50%', objectFit: 'cover', border: '2px solid var(--primary)' }}
            />
          ) : (
            <div style={{ width: '80px', height: '80px', borderRadius: '50%', backgroundColor: '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', color: 'var(--primary)', fontWeight: 'bold' }}>
              {(formData.display_name?.[0] || user?.username?.[0] || '?').toUpperCase()}
            </div>
          )}
          <div>
            <h3 style={{ margin: 0 }}>{user?.username}</h3>
            <span className="muted small">{user?.email} • {user?.role}</span>
          </div>
        </div>

        <label className="field">
          <span>Display Name</span>
          <input
            type="text"
            value={formData.display_name}
            onChange={(e) => setFormData((f) => ({ ...f, display_name: e.target.value }))}
            placeholder="e.g. John Doe"
          />
        </label>

        <label className="field">
          <span>Avatar Image URL</span>
          <input
            type="url"
            value={formData.avatar_url}
            onChange={(e) => setFormData((f) => ({ ...f, avatar_url: e.target.value }))}
            placeholder="https://example.com/avatar.jpg"
          />
        </label>

        <label className="field">
          <span>Timezone</span>
          <select
            value={formData.timezone}
            onChange={(e) => setFormData((f) => ({ ...f, timezone: e.target.value }))}
            className="select"
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid var(--border)' }}
          >
            <option value="UTC">UTC (GMT+0)</option>
            <option value="America/New_York">Eastern Time (US & Canada)</option>
            <option value="America/Chicago">Central Time (US & Canada)</option>
            <option value="America/Denver">Mountain Time (US & Canada)</option>
            <option value="America/Los_Angeles">Pacific Time (US & Canada)</option>
            <option value="Europe/London">London (GMT+1)</option>
            <option value="Europe/Paris">Paris (GMT+2)</option>
            <option value="Asia/Kolkata">India (GMT+5:30)</option>
            <option value="Asia/Kathmandu">Nepal (GMT+5:45)</option>
            <option value="Asia/Tokyo">Tokyo (GMT+9)</option>
          </select>
        </label>

        <label className="field">
          <span>Bio</span>
          <textarea
            rows={4}
            value={formData.bio}
            onChange={(e) => setFormData((f) => ({ ...f, bio: e.target.value }))}
            placeholder="Tell us about yourself..."
            maxLength={500}
          />
        </label>

        <div className="row end" style={{ marginTop: '1rem' }}>
          <button type="submit" className="btn btn-primary" disabled={busy}>
            {busy ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>
    </div>
  )
}
