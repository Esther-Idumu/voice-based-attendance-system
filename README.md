# voice-based-attendance-system
A system that uses voice biometrics to verify student's presence in class.

## Frontend UI
A simple React UI has been added in the `frontend/` folder.

### Run the frontend
1. Open a terminal inside `frontend/`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open the URL shown in the terminal, typically `http://localhost:5173`.

### Backend
Make sure the FastAPI backend is running at `http://127.0.0.1:8000` before using the UI.

### Notes
- The frontend uses the backend endpoints for students, courses, voice enrollment, and attendance verification.
- The backend `app/main.py` now includes CORS support for `http://localhost:5173`.
