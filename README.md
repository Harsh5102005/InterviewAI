# 🎯 InterviewAI — AI-Powered Technical Interview Practice

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Groq](https://img.shields.io/badge/Groq_AI-Powered-F55036?style=for-the-badge)

**Practice technical interviews with real-time AI questions, voice input, and instant scored feedback.**

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Question Generation** | Role-specific, difficulty-tiered questions powered by Groq — deduplicated across sessions |
| 🎙️ **Voice Input** | Answer questions using your microphone via Web Speech API |
| 🔊 **Text-to-Speech** | Questions are read aloud for a realistic interview feel |
| 📊 **Rubric Scoring (0-10)** | AI grades each answer with specific, actionable feedback |
| 📜 **Full Session History** | Track every question, answer, and score across all past interviews |
| 🔒 **User Accounts** | Register and log in to save your personal interview history |
| ⚡ **Pre-AI Validation** | Smart checks filter non-answers before wasting API calls |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, Pydantic v2 |
| **Frontend** | React 19, Vanilla CSS, Web Speech API |
| **Database** | MySQL 8.0+ |
| **AI Engine** | Groq API (Qwen model) |
| **Server** | Uvicorn (ASGI) |

---

## 📁 Project Structure

```
interviewai/
├── backend/
│   ├── .env.example              # Environment config template
│   ├── main.py                   # App entry point (port 8080)
│   ├── config.py                 # Pydantic settings loader
│   ├── database.py               # SQLAlchemy engine & session
│   ├── models.py                 # ORM models
│   ├── schemas.py                # Pydantic DTOs
│   ├── requirements.txt
│   ├── routers/
│   │   ├── auth.py
│   │   ├── interview.py
│   │   ├── question.py
│   │   └── answer.py
│   └── services/
│       ├── ai_service.py
│       ├── user_service.py
│       ├── interview_service.py
│       ├── question_service.py
│       └── answer_service.py
└── frontend/
    ├── package.json
    └── src/
        ├── App.js
        ├── index.css
        └── index.js
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- MySQL 8.0+ running on `localhost:3306`
- Groq API key — get one free at https://console.groq.com

### 1. Clone the Repository

```bash
git clone https://github.com/Harsh5102005/interviewai.git
cd interviewai
```

### 2. Database Setup

```sql
CREATE DATABASE ai_interview;
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Groq API key and MySQL password
```

```bash
# Start the backend (runs on http://localhost:8080)
python main.py
```

Interactive API docs: http://localhost:8080/docs

The backend auto-creates all database tables on first startup.

### 4. Frontend Setup

Open a new terminal (keep the backend running):

```bash
cd frontend
npm install
npm start
```

The app will open at http://localhost:3000.

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login |
| `POST` | `/api/interview/start` | Start a new interview session |
| `GET` | `/api/interview/{id}/history` | Get session Q&A history |
| `GET` | `/api/interview/user/{userId}` | Get all interviews for a user |
| `POST` | `/api/question` | Generate an AI interview question |
| `POST` | `/api/answer` | Submit answer for AI scoring |

---

## ⚙️ Configuration

All config lives in `backend/.env` (never committed):

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key (required) |
| `GROQ_API_MODEL` | AI model (default: `qwen/qwen3.8-27b`) |
| `DB_URL` | SQLAlchemy MySQL connection string |

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| Backend won't start | Check MySQL is running and `.env` credentials are correct |
| `Field id has no default value` | Run: `ALTER TABLE interview MODIFY id BIGINT NOT NULL AUTO_INCREMENT;` |
| AI not generating questions | Verify `GROQ_API_KEY` in `backend/.env` |
| Frontend connection error | Ensure the backend terminal is still running on port 8080 |

---

## 👤 Author

**Harsh Maurya** — [GitHub @Harsh5102005](https://github.com/Harsh5102005)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
