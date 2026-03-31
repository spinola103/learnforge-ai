import { useState, useRef, useEffect } from 'react'
import { sendAnswer } from '../api'

const STRATEGY_META = {
  nudge:     { color: 'var(--nudge)',     label: 'Nudge',     icon: '👆' },
  breakdown: { color: 'var(--breakdown)', label: 'Breakdown', icon: '🔍' },
  socratic:  { color: 'var(--socratic)',  label: 'Socratic',  icon: '❓' },
  analogy:   { color: 'var(--analogy)',   label: 'Analogy',   icon: '💡' },
}

const MISTAKE_META = {
  arithmetic:    { label: 'Arithmetic Slip',  color: 'var(--nudge)' },
  procedural:    { label: 'Procedural Error', color: 'var(--breakdown)' },
  conceptual:    { label: 'Conceptual Gap',   color: 'var(--analogy)' },
  misconception: { label: 'Misconception',    color: 'var(--socratic)' },
  transfer:      { label: 'Transfer Failure', color: 'var(--warning)' },
}

export default function Chat({ session, onSessionEnd }) {
  const [messages, setMessages] = useState([
    {
      role: 'system',
      text: session.message,
      problem: session.problem,
      topic: session.topic
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentProblem, setCurrentProblem] = useState(session.problem)
  const [sessionState, setSessionState] = useState({})
  const [currentMeta, setCurrentMeta] = useState({ strategy: null, mistakeType: null })

  const bottomRef = useRef(null)
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    const trimmed = input.trim()
    if (!trimmed || loading) return

    // Add user message
    setMessages(prev => [...prev, { role: 'user', text: trimmed }])
    setInput('')
    setLoading(true)

    try {
      // Build state to send
      let stateToSend = { ...sessionState }
      if (currentMeta.strategy === 'socratic' && sessionState.socratic_exchanges > 0) {
        stateToSend = {
          ...sessionState,
          socratic_history: [
            ...(sessionState.socratic_history || []),
            { role: 'user', content: trimmed }
          ]
        }
      }

      const res = await sendAnswer(session.session_id, trimmed, stateToSend)

      // Update session state
      if (res.session_state !== undefined) {
        setSessionState(res.session_state)
      }

      // Update current meta
      if (res.strategy || res.mistake_type) {
        setCurrentMeta({
          strategy: res.strategy || currentMeta.strategy,
          mistakeType: res.mistake_type || currentMeta.mistakeType
        })
      }

      if (res.correct) {
        setSessionState({})
        setCurrentMeta({ strategy: null, mistakeType: null })
        setMessages(prev => [...prev, {
          role: 'system',
          text: res.message,
          correct: true,
          nextProblem: res.next_problem,
          concept: res.concept
        }])
        if (res.next_problem) setCurrentProblem(res.next_problem)

      } else {
        setMessages(prev => [...prev, {
          role: 'system',
          text: res.message,
          correct: false,
          mistakeType: res.mistake_type || currentMeta.mistakeType,
          strategy: res.strategy || currentMeta.strategy,
          stepNum: res.session_state?.breakdown_step || null,
          isRetry: res.is_retry || false
        }])
      }

    } catch (e) {
      console.error(e)
      setMessages(prev => [...prev, {
        role: 'system',
        text: 'Connection error. Make sure the backend is running.',
        error: true
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>

      {/* Top Bar */}
      <div style={{
        padding: '14px 24px', borderBottom: '1px solid var(--border)',
        background: 'var(--surface)', display: 'flex',
        alignItems: 'center', justifyContent: 'space-between', gap: 16
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
          <span style={{ fontSize: 18 }}>⚡</span>
          <span style={{ fontWeight: 700, fontSize: 16 }}>
            LearnForge <span style={{ color: 'var(--accent)' }}>AI</span>
          </span>
        </div>
        <div style={{
          background: 'var(--surface2)', border: '1px solid var(--border)',
          borderRadius: 8, padding: '6px 16px', fontSize: 13,
          color: 'var(--text)', fontFamily: 'JetBrains Mono, monospace',
          flex: 1, textAlign: 'center'
        }}>
          {currentProblem}
        </div>
        <div style={{
          fontSize: 11, color: 'var(--accent)',
          fontFamily: 'JetBrains Mono, monospace', flexShrink: 0
        }}>
          {session.session_id}
        </div>
      </div>

      {/* Messages */}
      <div style={{
        flex: 1, overflowY: 'auto', padding: '24px',
        display: 'flex', flexDirection: 'column', gap: 16
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            display: 'flex',
            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
          }}>

            {msg.role === 'system' && (
              <div style={{ maxWidth: '78%' }}>

                {/* Initial problem card */}
                {msg.problem && (
                  <div style={{
                    background: 'rgba(108,99,255,0.1)',
                    border: '1px solid rgba(108,99,255,0.3)',
                    borderRadius: 12, padding: '14px 18px', marginBottom: 10
                  }}>
                    <div style={{
                      fontSize: 11, color: 'var(--accent)', fontWeight: 600,
                      marginBottom: 6, letterSpacing: '0.08em'
                    }}>
                      📚 PROBLEM · {msg.topic?.toUpperCase()}
                    </div>
                    <div style={{
                      fontSize: 15, fontWeight: 500,
                      fontFamily: 'JetBrains Mono, monospace'
                    }}>
                      {msg.problem}
                    </div>
                  </div>
                )}

                {/* Next problem card */}
                {msg.nextProblem && (
                  <div style={{
                    background: 'rgba(34,197,94,0.08)',
                    border: '1px solid rgba(34,197,94,0.25)',
                    borderRadius: 12, padding: '14px 18px', marginTop: 10
                  }}>
                    <div style={{
                      fontSize: 11, color: 'var(--success)', fontWeight: 600,
                      marginBottom: 6, letterSpacing: '0.08em'
                    }}>
                      🎯 NEXT PROBLEM · {msg.concept?.toUpperCase()}
                    </div>
                    <div style={{
                      fontSize: 15, fontWeight: 500,
                      fontFamily: 'JetBrains Mono, monospace'
                    }}>
                      {msg.nextProblem}
                    </div>
                  </div>
                )}

                {/* Strategy + mistake badges */}
                {msg.mistakeType && (
                  <div style={{
                    display: 'flex', gap: 8,
                    marginBottom: 8, flexWrap: 'wrap'
                  }}>
                    <span style={{
                      fontSize: 11, fontWeight: 600, padding: '3px 10px',
                      borderRadius: 20, background: 'var(--surface2)',
                      border: `1px solid ${MISTAKE_META[msg.mistakeType]?.color || 'var(--border)'}`,
                      color: MISTAKE_META[msg.mistakeType]?.color
                    }}>
                      {MISTAKE_META[msg.mistakeType]?.label}
                    </span>

                    {msg.strategy && (
                      <span style={{
                        fontSize: 11, fontWeight: 600, padding: '3px 10px',
                        borderRadius: 20, background: 'var(--surface2)',
                        border: `1px solid ${STRATEGY_META[msg.strategy]?.color || 'var(--border)'}`,
                        color: STRATEGY_META[msg.strategy]?.color
                      }}>
                        {STRATEGY_META[msg.strategy]?.icon} {STRATEGY_META[msg.strategy]?.label}
                      </span>
                    )}

                    {msg.strategy === 'breakdown' && msg.stepNum && (
                      <span style={{
                        fontSize: 11, padding: '3px 10px', borderRadius: 20,
                        background: 'var(--surface2)', color: 'var(--text-muted)',
                        border: '1px solid var(--border)'
                      }}>
                        Step {msg.stepNum}
                      </span>
                    )}

                    {msg.isRetry && (
                      <span style={{
                        fontSize: 11, padding: '3px 10px', borderRadius: 20,
                        background: 'rgba(239,68,68,0.1)',
                        color: 'var(--error)',
                        border: '1px solid rgba(239,68,68,0.3)'
                      }}>
                        ↺ Try again
                      </span>
                    )}
                  </div>
                )}

                {/* Message bubble */}
                <div style={{
                  background: msg.correct
                    ? 'rgba(34,197,94,0.07)'
                    : msg.error
                      ? 'rgba(239,68,68,0.07)'
                      : 'var(--surface)',
                  border: `1px solid ${
                    msg.correct ? 'rgba(34,197,94,0.2)'
                    : msg.error ? 'rgba(239,68,68,0.2)'
                    : 'var(--border)'}`,
                  borderRadius: 12, padding: '14px 18px',
                  fontSize: 14, lineHeight: 1.8, whiteSpace: 'pre-wrap'
                }}>
                  {msg.correct && (
                    <span style={{ color: 'var(--success)', fontWeight: 600 }}>
                      ✓ Correct!{' '}
                    </span>
                  )}
                  {msg.text}
                </div>

              </div>
            )}

            {/* Student bubble */}
            {msg.role === 'user' && (
              <div style={{
                background: 'var(--accent)', borderRadius: 12,
                padding: '12px 18px', fontSize: 14, lineHeight: 1.6,
                maxWidth: '60%', color: 'white', wordBreak: 'break-word'
              }}>
                {msg.text}
              </div>
            )}

          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex' }}>
            <div style={{
              background: 'var(--surface)', border: '1px solid var(--border)',
              borderRadius: 12, padding: '12px 18px', fontSize: 13,
              color: 'var(--text-muted)', display: 'flex', gap: 8, alignItems: 'center'
            }}>
              <span>⚡</span> Analyzing your response...
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div style={{
        padding: '16px 24px', borderTop: '1px solid var(--border)',
        background: 'var(--surface)', display: 'flex', gap: 12
      }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder={
            currentMeta.strategy === 'breakdown'
              ? 'Show your working for this step...'
              : currentMeta.strategy === 'socratic'
                ? 'Think it through and reply...'
                : 'Type your answer...'
          }
          disabled={loading}
          style={{
            flex: 1, background: 'var(--surface2)',
            border: '1px solid var(--border)', borderRadius: 10,
            padding: '12px 16px', fontSize: 14, color: 'var(--text)',
            outline: 'none', fontFamily: 'Inter, sans-serif',
            transition: 'border-color 0.2s'
          }}
          onFocus={e => e.target.style.borderColor = 'var(--accent)'}
          onBlur={e => e.target.style.borderColor = 'var(--border)'}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          style={{
            padding: '12px 22px', borderRadius: 10, border: 'none',
            background: loading || !input.trim() ? 'var(--border)' : 'var(--accent)',
            color: 'white', fontSize: 16, fontWeight: 700,
            cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
            transition: 'background 0.2s'
          }}
        >
          →
        </button>
      </div>

    </div>
  )
}