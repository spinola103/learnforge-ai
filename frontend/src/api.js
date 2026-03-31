import axios from 'axios'

const BASE = 'http://127.0.0.1:8000'

export const createStudent = (name) =>
  axios.post(`${BASE}/student/create`, { name }).then(r => r.data)

export const startSession = (student_id) =>
  axios.post(`${BASE}/session/start`, { student_id }).then(r => r.data)

export const sendAnswer = (session_id, student_answer, session_state = {}) =>
  axios.post(`${BASE}/session/respond`, {
    session_id,
    student_answer,
    session_state
  }).then(r => r.data)

export const endSession = (session_id) =>
  axios.get(`${BASE}/session/end/${session_id}`).then(r => r.data)

export const getStudentModel = (student_id) =>
  axios.get(`${BASE}/student/${student_id}/model`).then(r => r.data)