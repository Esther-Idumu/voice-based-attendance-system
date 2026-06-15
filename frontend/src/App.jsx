import { useEffect, useState } from 'react'

const API_BASE = 'http://127.0.0.1:8000'

function App() {
  const [students, setStudents] = useState([])
  const [courses, setCourses] = useState([])
  const [message, setMessage] = useState('')

  const [newStudentName, setNewStudentName] = useState('')
  const [newMatricNumber, setNewMatricNumber] = useState('')
  const [newCourseName, setNewCourseName] = useState('')

  const [enrollStudentId, setEnrollStudentId] = useState('')
  const [enrollCourseId, setEnrollCourseId] = useState('')

  const [voiceFile, setVoiceFile] = useState(null)
  const [voiceStudentId, setVoiceStudentId] = useState('')
  const [verifyCourseId, setVerifyCourseId] = useState('')
  const [verifyFile, setVerifyFile] = useState(null)
  const [verifyCourseInput, setVerifyCourseInput] = useState('')

  useEffect(() => {
    fetchStudents()
    fetchCourses()
  }, [])

  const fetchStudents = async () => {
    try {
      const res = await fetch(`${API_BASE}/students/`)
      const data = await res.json()
      setStudents(data)
    } catch (error) {
      setMessage('Unable to load students.')
    }
  }

  const fetchCourses = async () => {
    try {
      const res = await fetch(`${API_BASE}/courses/`)
      const data = await res.json()
      setCourses(data)
    } catch (error) {
      setMessage('Unable to load courses.')
    }
  }

  const createStudent = async (event) => {
    event.preventDefault()
    if (!newStudentName || !newMatricNumber) {
      setMessage('Student name and matric number are required.')
      return
    }

    const form = new URLSearchParams()
    form.append('name', newStudentName)
    form.append('matric_number', newMatricNumber)

    try {
      const res = await fetch(`${API_BASE}/students/`, {
        method: 'POST',
        body: form,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Failed to create student')
      setStudents((prev) => [...prev, data])
      setNewStudentName('')
      setNewMatricNumber('')
      setMessage(`Student created: ${data.name}`)
    } catch (error) {
      setMessage(error.message)
    }
  }

  const createCourse = async (event) => {
    event.preventDefault()
    if (!newCourseName) {
      setMessage('Course name is required.')
      return
    }

    const form = new URLSearchParams()
    form.append('name', newCourseName)

    try {
      const res = await fetch(`${API_BASE}/courses/`, {
        method: 'POST',
        body: form,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Failed to create course')
      setCourses((prev) => [...prev, data])
      setNewCourseName('')
      setMessage(`Course created: ${data.name}`)
    } catch (error) {
      setMessage(error.message)
    }
  }

  const enrollStudent = async (event) => {
    event.preventDefault()
    if (!enrollStudentId || !enrollCourseId) {
      setMessage('Select a student and a course to enroll.')
      return
    }

    const form = new URLSearchParams()
    form.append('student_id', enrollStudentId)
    form.append('course_id', enrollCourseId)

    try {
      const res = await fetch(`${API_BASE}/courses/enroll`, {
        method: 'POST',
        body: form,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || data.message || 'Enrollment failed')
      setMessage(data.message)
      setEnrollStudentId('')
      setEnrollCourseId('')
      fetchStudents()
    } catch (error) {
      setMessage(error.message)
    }
  }

  const enrollVoice = async (event) => {
    event.preventDefault()
    if (!voiceStudentId || !voiceFile) {
      setMessage('Select a student and upload a voice file.')
      return
    }

    const formData = new FormData()
    formData.append('file', voiceFile)

    try {
      const res = await fetch(`${API_BASE}/students/${voiceStudentId}/enroll-voice`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || data.message || 'Voice enrollment failed')
      setVoiceFile(null)
      setMessage(data.message)
    } catch (error) {
      setMessage(error.message)
    }
  }

  const verifyAttendance = async (event) => {
    event.preventDefault()
    if (!verifyCourseId || !verifyFile) {
      setMessage('Select a course, mention it in your voice, and upload the file.')
      return
    }

    const formData = new FormData()
    formData.append('file', verifyFile)

    try {
      const res = await fetch(`${API_BASE}/attendance/verify?course_id=${verifyCourseId}`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || data.message || 'Attendance verification failed')
      setMessage(data.message || JSON.stringify(data))
    } catch (error) {
      setMessage(error.message)
    }
  }

  return (
    <div className="app-shell">
      <header>
        <h1>Voice Attendance System</h1>
        <p>Use the forms below to manage students, courses, enroll voice samples, and verify attendance.</p>
      </header>

      <section className="panel">
        <h2>Students</h2>
        <form onSubmit={createStudent} className="form-grid">
          <label>
            Name
            <input value={newStudentName} onChange={(e) => setNewStudentName(e.target.value)} />
          </label>
          <label>
            Matric Number
            <input value={newMatricNumber} onChange={(e) => setNewMatricNumber(e.target.value)} />
          </label>
          <button type="submit">Create Student</button>
        </form>
        <div className="list-box">
          <h3>Existing students</h3>
          {students.length ? (
            <ul>
              {students.map((student) => (
                <li key={student.id}>
                  {student.name} ({student.matric_number})
                </li>
              ))}
            </ul>
          ) : (
            <p>No students yet.</p>
          )}
        </div>
      </section>

      <section className="panel">
        <h2>Courses</h2>
        <form onSubmit={createCourse} className="form-grid">
          <label>
            Course Name
            <input value={newCourseName} onChange={(e) => setNewCourseName(e.target.value)} />
          </label>
          <button type="submit">Create Course</button>
        </form>
        <div className="list-box">
          <h3>Existing courses</h3>
          {courses.length ? (
            <ul>
              {courses.map((course) => (
                <li key={course.id}>{course.name}</li>
              ))}
            </ul>
          ) : (
            <p>No courses yet.</p>
          )}
        </div>
      </section>

      <section className="panel">
        <h2>Enroll Student in Course</h2>
        <form onSubmit={enrollStudent} className="form-grid">
          <label>
            Student
            <select value={enrollStudentId} onChange={(e) => setEnrollStudentId(e.target.value)}>
              <option value="">Select student</option>
              {students.map((student) => (
                <option key={student.id} value={student.id}>
                  {student.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Course
            <select value={enrollCourseId} onChange={(e) => setEnrollCourseId(e.target.value)}>
              <option value="">Select course</option>
              {courses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit">Enroll</button>
        </form>
      </section>

      <section className="panel">
        <h2>Enroll Voice Sample</h2>
        <form onSubmit={enrollVoice} className="form-grid">
          <label>
            Student
            <select value={voiceStudentId} onChange={(e) => setVoiceStudentId(e.target.value)}>
              <option value="">Select student</option>
              {students.map((student) => (
                <option key={student.id} value={student.id}>
                  {student.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Voice File
            <input type="file" accept="audio/*" onChange={(e) => setVoiceFile(e.target.files?.[0] ?? null)} />
          </label>
          <button type="submit">Upload Voice</button>
        </form>
      </section>

      <section className="panel">
        <h2>Verify Attendance</h2>
        <form onSubmit={verifyAttendance} className="form-grid">
          <label>
            Course
            <select value={verifyCourseId} onChange={(e) => setVerifyCourseId(e.target.value)}>
              <option value="">Select course</option>
              {courses.map((course) => (
                <option key={course.id} value={course.id}>
                  {course.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Voice File
            <input type="file" accept="audio/*" onChange={(e) => setVerifyFile(e.target.files?.[0] ?? null)} />
          </label>
          <button type="submit">Verify Attendance</button>
        </form>
        <p className="hint">Your voice should say “present” and mention the selected course name.</p>
      </section>

      <footer>
        <div className="status-box">{message || 'Ready'}</div>
      </footer>
    </div>
  )
}

export default App
