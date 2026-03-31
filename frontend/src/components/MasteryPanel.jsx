const STRATEGY_COLORS = {
  nudge: 'var(--nudge)',
  breakdown: 'var(--breakdown)',
  socratic: 'var(--socratic)',
  analogy: 'var(--analogy)',
}

const MISTAKE_LABELS = {
  arithmetic: '🔢 Arithmetic',
  procedural: '📋 Procedural',
  conceptual: '💡 Conceptual',
  misconception: '❌ Misconception',
  transfer: '🔄 Transfer',
}

export default function MasteryPanel({ studentModel, studentName, onEndSession }) {
  if (!studentModel) return (
    <div style={panelStyle}>
      <div style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', marginTop: 40 }}>
        Loading student model...
      </div>
    </div>
  )

  const { mastery = {}, mistake_profile = {}, total_sessions, total_mistakes } = studentModel

  return (
    <div style={panelStyle}>
      {/* Student Header */}
      <div style={{ padding: '20px 20px 16px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 36, height: 36, borderRadius: '50%',
            background: 'var(--accent)', display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            fontSize: 16, fontWeight: 700
          }}>
            {studentName?.[0]?.toUpperCase()}
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 14 }}>{studentName}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              {total_sessions} session{total_sessions !== 1 ? 's' : ''} · {total_mistakes} mistake{total_mistakes !== 1 ? 's' : ''}
            </div>
          </div>
        </div>
      </div>

      {/* Mastery Scores */}
      <div style={{ padding: '16px 20px' }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', letterSpacing: '0.08em', marginBottom: 12 }}>
          CONCEPT MASTERY
        </div>
        {Object.keys(mastery).length === 0 ? (
          <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            No data yet — start answering!
          </div>
        ) : (
          Object.entries(mastery).map(([concept, score]) => (
            <div key={concept} style={{ marginBottom: 14 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
                <span style={{ fontSize: 13, textTransform: 'capitalize' }}>
                  {concept.replace(/_/g, ' ')}
                </span>
                <span style={{
                  fontSize: 12, fontWeight: 600,
                  color: score >= 70 ? 'var(--success)' : score >= 40 ? 'var(--warning)' : 'var(--error)'
                }}>
                  {Math.round(score)}
                </span>
              </div>
              <div style={{ height: 6, background: 'var(--surface2)', borderRadius: 3 }}>
                <div style={{
                  height: '100%', borderRadius: 3,
                  width: `${score}%`,
                  background: score >= 70 ? 'var(--success)' : score >= 40 ? 'var(--warning)' : 'var(--error)',
                  transition: 'width 0.5s ease'
                }} />
              </div>
            </div>
          ))
        )}
      </div>

      {/* Mistake Profile */}
      {Object.keys(mistake_profile).length > 0 && (
        <div style={{ padding: '4px 20px 16px', borderTop: '1px solid var(--border)' }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', letterSpacing: '0.08em', margin: '16px 0 12px' }}>
            MISTAKE PROFILE
          </div>
          {Object.entries(mistake_profile).map(([type, count]) => (
            <div key={type} style={{
              display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', marginBottom: 8
            }}>
              <span style={{ fontSize: 13 }}>{MISTAKE_LABELS[type] || type}</span>
              <span style={{
                background: 'var(--surface2)', borderRadius: 12,
                padding: '2px 10px', fontSize: 12, fontWeight: 600
              }}>{count}</span>
            </div>
          ))}
        </div>
      )}

      {/* End Session Button */}
      <div style={{ padding: '12px 20px', marginTop: 'auto', borderTop: '1px solid var(--border)' }}>
        <button
          onClick={onEndSession}
          style={{
            width: '100%', padding: '10px', borderRadius: 8,
            border: '1px solid var(--border)', background: 'transparent',
            color: 'var(--text-muted)', fontSize: 13, cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseOver={e => e.target.style.borderColor = 'var(--accent)'}
          onMouseOut={e => e.target.style.borderColor = 'var(--border)'}
        >
          End Session & View Recap
        </button>
      </div>
    </div>
  )
}

const panelStyle = {
  width: 260, minWidth: 260, height: '100vh',
  background: 'var(--surface)', borderRight: '1px solid var(--border)',
  display: 'flex', flexDirection: 'column', overflow: 'hidden'
}