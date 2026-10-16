# How to Run Smart Interview Prep (Python Edition)

This guide will walk you through starting both the FastAPI backend and the React frontend.

## Prerequisites
1. **MySQL** must be running on `localhost:3306` with a root password `harsh` (or update `backend/.env` with your credentials).
2. Create the database if it doesn't exist: `CREATE DATABASE ai_interview;`
3. You must have Python 3.11+ and Node.js 18+ installed.

---

## Step 1: Start the Backend (FastAPI)

Open a new terminal and run the following commands:

```bash
# Navigate to the backend directory
cd e:\ai\smart-interview-prep-python\backend

# (Optional but recommended) Create and activate a virtual environment
# python -m venv venv
# .\venv\Scripts\activate

# Install the Python dependencies (only needed the first time)
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```
*The backend server will start on **http://localhost:8080**.*
*(You can view the interactive API documentation at http://localhost:8080/docs)*

---

## Step 2: Start the Frontend (React)

Open a **second** new terminal (keep the backend running in the first one) and run:

```bash
# Navigate to the frontend directory
cd e:\ai\smart-interview-prep-python\frontend

# Install the Node.js dependencies (only needed the first time)
npm install

# Start the React development server
npm start
```
*The React app will automatically open in your browser at **http://localhost:3000**.*

---

## Troubleshooting

- **Backend fails to start / Database error:** Ensure MySQL is running and the credentials in `backend/.env` are correct.
- **AI errors:** Ensure your Groq API key is valid in `backend/.env` (`GROQ_API_KEY=...`).
- **Frontend can't connect to backend:** Make sure the backend terminal is still running and listening on port 8080.
