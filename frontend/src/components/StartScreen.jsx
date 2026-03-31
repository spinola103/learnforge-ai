import { useState } from 'react'
import { createStudent, startSession } from '../api'

export default function StartScreen({ onStart }) {
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleStart = async () => {
    if (!name.trim()) return setError('Please enter your name')
    setLoading(true)
    setError('')
    try {
      const student = await createStudent(name.trim())
      const session = await startSession(student.student_id)
      onStart({ student, session })
    } catch {
      setError('Could not connect to LearnForge backend. Is the server running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      height: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg)'
    }}>
      <div style={{
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderRadius: 16, padding: '48px 40px', width: 420, textAlign: 'center'
      }}>
        {/* Logo */}
        <div style={{ marginBottom: 8 }}>
          <span style={{
            background: 'var(--accent)', borderRadius: 10,
            padding: '8px 14px', fontSize: 22
          }}>⚡</span>
        </div>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 6 }}>
          LearnForge <span style={{ color: 'var(--accent)' }}>AI</span>
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 36 }}>
          Mistake-driven adaptive learning engine
        </p>

        <div style={{ textAlign: 'left', marginBottom: 24 }}>
          <label style={{ fontSize: 13, color: 'var(--text-muted)', fontWeight: 500 }}>
            YOUR NAME
          </label>
          <input
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleStart()}
            placeholder="Enter your name..."
            style={{
              display: 'block', width: '100%', marginTop: 8,
              background: 'var(--surface2)', border: '1px solid var(--border)',
              borderRadius: 8, padding: '12px 14px', fontSize: 15,
              color: 'var(--text)', outline: 'none',
              fontFamily: 'Inter, sans-serif'
            }}
          />
        </div>

        {error && (
          <p style={{ color: 'var(--error)', fontSize: 13, marginBottom: 16 }}>{error}</p>
        )}

        <button
          onClick={handleStart}
          disabled={loading}
          style={{
            width: '100%', padding: '13px', borderRadius: 8, border: 'none',
            background: loading ? 'var(--border)' : 'var(--accent)',
            color: 'white', fontSize: 15, fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer', transition: 'opacity 0.2s'
          }}
        >
          {loading ? 'Starting...' : 'Start Learning →'}
        </button>

        <div style={{
          marginTop: 32, display: 'flex', justifyContent: 'center',
          gap: 24, fontSize: 12, color: 'var(--text-muted)'
        }}>
          {['🧠 Mistake Analysis', '🎯 Adaptive Strategy', '🔒 Local AI'].map(f => (
            <span key={f}>{f}</span>
          ))}
        </div>
      </div>
    </div>
  )
}