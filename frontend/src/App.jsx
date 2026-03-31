import { useState, useEffect } from 'react'
import StartScreen from './components/StartScreen'
import Chat from './components/Chat'
import MasteryPanel from './components/MasteryPanel'
import SessionRecap from './components/SessionRecap'
import { endSession, getStudentModel } from './api'

export default function App() {
  const [screen, setScreen] = useState('start')   // start | chat | recap
  const [student, setStudent] = useState(null)
  const [session, setSession] = useState(null)
  const [recap, setRecap] = useState(null)
  const [studentModel, setStudentModel] = useState(null)

  // Poll student model every 8 seconds during chat
  useEffect(() => {
    if (screen !== 'chat' || !student) return
    const refresh = () => getStudentModel(student.student_id).then(setStudentModel)
    refresh()
    const interval = setInterval(refresh, 8000)
    return () => clearInterval(interval)
  }, [screen, student])

  const handleStart = ({ student, session }) => {
    setStudent(student)
    setSession(session)
    setScreen('chat')
  }

  const handleEndSession = async () => {
    try {
      const recapData = await endSession(session.session_id)
      setRecap(recapData)
      setScreen('recap')
    } catch {
      alert('Could not end session. Try again.')
    }
  }

  const handleRestart = () => {
    setStudent(null)
    setSession(null)
    setRecap(null)
    setStudentModel(null)
    setScreen('start')
  }

  if (screen === 'start') return <StartScreen onStart={handleStart} />
  if (screen === 'recap') return <SessionRecap recap={recap} onRestart={handleRestart} />

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <MasteryPanel
        studentModel={studentModel}
        studentName={student?.name}
        onEndSession={handleEndSession}
      />
      <Chat
        session={session}
        studentId={student?.student_id}
        onSessionEnd={handleEndSession}
      />
    </div>
  )
}