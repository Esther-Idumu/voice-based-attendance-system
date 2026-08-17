# Voice-Based Attendance System

A backend system that verifies student presence in class using voice biometrics. Students speak a short phrase to mark attendance, and the system confirms their identity by matching their voice against an enrolled voiceprint, not just checking that *a* voice said the right words.

**Live demo:** 

## How It Works

Attendance verification is a two-stage check, not a single pass:

1. **Speech-to-text check.** The submitted audio is transcribed using OpenAI Whisper. If the required keyword ("present") isn't detected, verification fails immediately, no point running speaker matching on invalid input.
2. **Speaker verification.** If the keyword is present, the system generates a voice embedding using SpeechBrain's ECAPA-TDNN speaker recognition model and compares it against every enrolled student's stored voiceprint using cosine similarity. The highest-scoring match above a similarity threshold (0.40) is accepted as the speaker.
3. **Business rules.** The matched student must be enrolled in the course being verified, and attendance can only be marked once per student per course per day. Both are checked before the attendance record is written.

This means the system isn't just checking *what* was said, but *who* said it.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| Database | PostgreSQL (via SQLAlchemy ORM) |
| Speech-to-text | OpenAI Whisper |
| Speaker verification | SpeechBrain (ECAPA-TDNN, `spkrec-ecapa-voxceleb`) |
| Audio processing | FFmpeg (converts uploaded audio to 16kHz mono WAV) |
| Frontend | React (Vite) |

## Features

- Student and course management (create, list, enroll)
- Voice enrollment: capture and store a student's voice embedding
- Attendance verification: single-endpoint flow that transcribes, verifies speaker identity, and marks attendance
- Duplicate-attendance prevention (one mark per student per course per day)
- Per-request timing breakdown (conversion, transcription, verification, DB write) returned in the API response, useful for performance tuning

## API Overview

| Endpoint | Method | Purpose |
|---|---|---|
| `/students/` | GET / POST | List or create students |
| `/students/{id}` | GET | Get a single student |
| `/students/{id}/enroll-voice` | POST | Upload a voice sample to enroll a student's voiceprint |
| `/courses/` | GET / POST | List or create courses |
| `/courses/enroll` | POST | Enroll a student in a course |
| `/attendance/verify` | POST | Submit audio to verify identity and mark attendance |

## Project Structure

```
app/
├── main.py                    # FastAPI app setup, CORS, router registration
├── models.py                  # SQLAlchemy models (Student, Course, VoiceEmbedding, Attendance)
├── database.py                # DB engine and session config
├── routes/
│   ├── students.py            # Student CRUD + voice enrollment
│   ├── courses.py             # Course CRUD + student-course enrollment
│   └── attendance.py          # Voice verification + attendance marking
└── services/
    ├── audio_converter.py     # FFmpeg-based audio conversion to WAV
    ├── transcription.py       # Whisper transcription
    └── speaker_embedding.py   # SpeechBrain embedding generation

frontend/
└── src/App.jsx                 # React UI for student/course management and voice capture
```

## Running Locally

### Backend

1. Create a PostgreSQL database and update the connection string in `app/database.py`.
2. Install dependencies (FastAPI, SQLAlchemy, Whisper, SpeechBrain, soundfile, torch; a `requirements.txt` is recommended if not already present).
3. Ensure FFmpeg is installed and available on your system PATH.
4. Run the API:
   ```
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.

### Frontend

1. From the `frontend/` folder:
   ```
   npm install
   npm run dev
   ```
2. Open the URL shown in the terminal (typically `http://localhost:5173`).

The frontend expects the backend running locally at `http://127.0.0.1:8000`.

## Deployment Notes

The React frontend is deployed to Vercel for browsing the UI, but full end-to-end voice verification (Whisper + SpeechBrain) requires the FastAPI backend, which is compute-heavy and currently run locally rather than deployed. A short demo video showing the full enrollment and verification flow is linked below.

**Demo video:** *(link here)*

## Known Limitations / Next Steps

- Database credentials are currently hardcoded for local development; these should move to environment variables before any real deployment.
- The frontend's API base URL is hardcoded to localhost; this needs to be environment-driven to point at a deployed backend.
- Whisper and SpeechBrain are loaded in-process, which makes the backend memory-heavy; splitting voice processing into a separate service would make cloud deployment more practical.

## Author

Built by Esther Idumu as a final year project, combining FastAPI, PostgreSQL, and speech ML models (Whisper, SpeechBrain) into a working two-factor voice attendance system.
