export default function SessionRecap({ recap, onRestart }) {
  const { total_mistakes, improved, mistake_breakdown, mastery_snapshot, recommendation, message } = recap

  return (
    <div style={{
      height: '100vh', display: 'flex',
      alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg)', padding: 24
    }}>
      <div style={{
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderRadius: 16, padding: 40, width: '100%', maxWidth: 560
      }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>
            {total_mistakes === 0 ? '🏆' : improved > 0 ? '📈' : '💪'}
          </div>
          <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>Session Complete</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>Here's what happened this session</p>
        </div>

        {/* Stats Row */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 28 }}>
          {[
            { label: 'Mistakes', value: total_mistakes, color: 'var(--error)' },
            { label: 'Corrected', value: improved, color: 'var(--success)' },
            { label: 'Concepts', value: Object.keys(mastery_snapshot || {}).length, color: 'var(--accent)' }
          ].map(stat => (
            <div key={stat.label} style={{
              background: 'var(--surface2)', borderRadius: 10,
              padding: '16px 12px', textAlign: 'center'
            }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: stat.color }}>{stat.value}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Mistake Breakdown */}
        {mistake_breakdown && Object.keys(mistake_breakdown).length > 0 && (
          <div style={{ marginBottom: 24 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', letterSpacing: '0.08em', marginBottom: 10 }}>
              MISTAKE TYPES THIS SESSION
            </div>
            {Object.entries(mistake_breakdown).map(([type, count]) => (
              <div key={type} style={{
                display: 'flex', justifyContent: 'space-between',
                padding: '8px 12px', background: 'var(--surface2)',
                borderRadius: 8, marginBottom: 6, fontSize: 14
              }}>
                <span style={{ textTransform: 'capitalize' }}>{type}</span>
                <span style={{ fontWeight: 600 }}>{count}×</span>
              </div>
            ))}
          </div>
        )}

        {/* Mastery Snapshot */}
        {mastery_snapshot && Object.keys(mastery_snapshot).length > 0 && (
          <div style={{ marginBottom: 24 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', letterSpacing: '0.08em', marginBottom: 10 }}>
              MASTERY UPDATE
            </div>
            {Object.entries(mastery_snapshot).map(([concept, score]) => (
              <div key={concept} style={{ marginBottom: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, fontSize: 13 }}>
                  <span style={{ textTransform: 'capitalize' }}>{concept.replace(/_/g, ' ')}</span>
                  <span style={{
                    fontWeight: 600,
                    color: score >= 70 ? 'var(--success)' : score >= 40 ? 'var(--warning)' : 'var(--error)'
                  }}>{Math.round(score)}/100</span>
                </div>
                <div style={{ height: 5, background: 'var(--border)', borderRadius: 3 }}>
                  <div style={{
                    height: '100%', borderRadius: 3, width: `${score}%`,
                    background: score >= 70 ? 'var(--success)' : score >= 40 ? 'var(--warning)' : 'var(--error)',
                  }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Recommendation */}
        <div style={{
          background: 'rgba(108,99,255,0.1)', border: '1px solid rgba(108,99,255,0.3)',
          borderRadius: 10, padding: '14px 16px', marginBottom: 28
        }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--accent)', marginBottom: 4 }}>
            📌 RECOMMENDATION
          </div>
          <div style={{ fontSize: 14, lineHeight: 1.6 }}>{recommendation}</div>
        </div>

        <button
          onClick={onRestart}
          style={{
            width: '100%', padding: 13, borderRadius: 8, border: 'none',
            background: 'var(--accent)', color: 'white',
            fontSize: 15, fontWeight: 600, cursor: 'pointer'
          }}
        >
          Start New Session →
        </button>
      </div>
    </div>
  )
}