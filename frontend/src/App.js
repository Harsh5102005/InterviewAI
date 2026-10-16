import React, { useMemo, useState, useEffect } from "react";
import "./index.css";

const API_BASE_URL = "http://localhost:8080";

const apiFetch = async (path, options) => {
  try {
    return await fetch(`${API_BASE_URL}${path}`, options);
  } catch (err) {
    throw new Error(
      `Could not connect to the backend at ${API_BASE_URL}. Make sure the FastAPI server is running on port 8080.`
    );
  }
};

function App() {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem("ai_interview_user");
      if (!saved) return null;
      const parsed = JSON.parse(saved);
      // If old session has no id, clear it so user logs in fresh
      if (!parsed || !parsed.id) {
        localStorage.removeItem("ai_interview_user");
        return null;
      }
      return parsed;
    } catch (e) {
      return null;
    }
  });

  const [currentPage, setCurrentPage] = useState("home"); // "home" or "interview"
  const [authMode, setAuthMode] = useState("login"); // "login" or "register"
  const [authName, setAuthName] = useState("");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [isAuthSubmitting, setIsAuthSubmitting] = useState(false);

  const [isSoundMuted, setIsSoundMuted] = useState(false);
  const [pastInterviews, setPastInterviews] = useState([]);
  const [isLoadingPastInterviews, setIsLoadingPastInterviews] = useState(false);
  const [expandedInterviewId, setExpandedInterviewId] = useState(null);
  const [expandedInterviewHistory, setExpandedInterviewHistory] = useState([]);
  const [isLoadingExpandedHistory, setIsLoadingExpandedHistory] = useState(false);
  const [interviewId, setInterviewId] = useState("");
  const [role, setRole] = useState("Java developer");
  const [difficulty, setDifficulty] = useState("medium");
  const [question, setQuestion] = useState("");
  const [questionId, setQuestionId] = useState("");
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState("");
  const [score, setScore] = useState("");
  const [history, setHistory] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [error, setError] = useState("");
  const [isStartingInterview, setIsStartingInterview] = useState(false);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const wordCount = useMemo(() => {
    return answer.trim() ? answer.trim().split(/\s+/).length : 0;
  }, [answer]);

  const scorePercent = score === "" ? 0 : Math.max(0, Math.min(100, score * 10));

  const clearInterviewSession = () => {
    setInterviewId("");
    setQuestion("");
    setQuestionId("");
    setAnswer("");
    setFeedback("");
    setScore("");
    setHistory([]);
  };

  const loadHistory = async (idToFetch) => {
    const currentId = idToFetch || interviewId;
    if (!currentId) return;

    setIsLoadingHistory(true);
    try {
      const res = await apiFetch(`/api/interview/${currentId}/history`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (err) {
      console.error("Could not fetch history", err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  useEffect(() => {
    if (interviewId) {
      loadHistory(interviewId);
    } else {
      setHistory([]);
    }
  }, [interviewId]);

  const loadPastInterviews = async () => {
    if (!user || !user.id) return;
    setIsLoadingPastInterviews(true);
    try {
      const res = await apiFetch(`/api/interview/user/${user.id}`);
      if (res.ok) {
        const data = await res.json();
        setPastInterviews(data);
      }
    } catch (err) {
      console.error("Could not fetch past interviews", err);
    } finally {
      setIsLoadingPastInterviews(false);
    }
  };

  const toggleExpandInterview = async (sessionId) => {
    if (expandedInterviewId === sessionId) {
      setExpandedInterviewId(null);
      setExpandedInterviewHistory([]);
      return;
    }
    setExpandedInterviewId(sessionId);
    setExpandedInterviewHistory([]);
    setIsLoadingExpandedHistory(true);
    try {
      const res = await apiFetch(`/api/interview/${sessionId}/history`);
      if (res.ok) {
        const data = await res.json();
        setExpandedInterviewHistory(data);
      }
    } catch (err) {
      console.error("Could not load session history", err);
    } finally {
      setIsLoadingExpandedHistory(false);
    }
  };

  useEffect(() => {
    if (user && user.id) {
      loadPastInterviews();
    } else {
      setPastInterviews([]);
    }
  }, [user]);

  const handleAuthSubmit = async (e) => {
    e.preventDefault();
    setAuthError("");
    setIsAuthSubmitting(true);

    const endpoint = authMode === "register" ? "/api/auth/register" : "/api/auth/login";
    const payload =
      authMode === "register"
        ? { name: authName, email: authEmail, password: authPassword }
        : { email: authEmail, password: authPassword };

    try {
      const res = await apiFetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const message = await res.text();
        throw new Error(message || `Could not ${authMode}`);
      }

      const userData = await res.json();
      setUser(userData);
      localStorage.setItem("ai_interview_user", JSON.stringify(userData));
      setAuthPassword("");
      setAuthError("");
      setCurrentPage("home");
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setIsAuthSubmitting(false);
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("ai_interview_user");
    clearInterviewSession();
    setCurrentPage("home");
  };

  const speak = (text) => {
    if (!text || !window.speechSynthesis || isSoundMuted) {
      return;
    }

    window.speechSynthesis.cancel();
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    window.speechSynthesis.speak(speech);
  };

  const startInterview = async () => {
    setIsStartingInterview(true);
    setError("");

    try {
      const res = await apiFetch("/api/interview/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId: user ? user.id : null,
          role,
          difficulty,
        }),
      });

      if (!res.ok) {
        const message = await res.text();
        throw new Error(message || "Could not start the interview.");
      }

      const data = await res.json();
      const newId = data.id || "";
      setInterviewId(newId);
      setQuestion("");
      setQuestionId("");
      setAnswer("");
      setFeedback("");
      setScore("");
      setHistory([]);
      if (newId) {
        loadHistory(newId);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsStartingInterview(false);
    }
  };

  const getQuestion = async () => {
    if (!interviewId) {
      setError("Choose a role and difficulty before loading questions.");
      return;
    }

    setIsLoadingQuestion(true);
    setError("");

    try {
      const res = await apiFetch("/api/question", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ interviewId }),
      });

      if (!res.ok) {
        const message = await res.text();
        throw new Error(message || "Could not load a question.");
      }

      const data = await res.json();
      setQuestion(data.questionText || "");
      setQuestionId(data.id || "");
      setAnswer("");
      setFeedback("");
      setScore("");

      speak(data.questionText);
      loadHistory(interviewId);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoadingQuestion(false);
    }
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError("Speech recognition is not supported in this browser. Type your answer instead.");
      return;
    }

    setError("");
    setIsListening(true);

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setAnswer((current) => `${current}${current ? " " : ""}${transcript}`.trim());
    };

    recognition.onerror = () => {
      setError("Could not capture your voice. Try again or type the answer.");
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  const submitAnswer = async () => {
    if (!questionId) {
      setError("Start the interview before submitting an answer.");
      return;
    }

    setIsSubmitting(true);
    setError("");
    setFeedback("");
    setScore("");

    try {
      const res = await apiFetch("/api/answer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          questionId,
          answerText: answer,
        }),
      });

      if (!res.ok) {
        const message = await res.text();
        throw new Error(message || "Could not submit the answer.");
      }

      const data = await res.json();
      setFeedback(data.feedback || "");
      setScore(Number.isFinite(data.score) ? data.score : 0);

      if (data.feedback) {
        speak(data.feedback);
      }
      loadHistory(interviewId);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!user) {
    return (
      <main className="auth-shell">
        <div className="auth-particles">
          <div className="auth-particle" style={{ width: 6, height: 6, left: "15%", top: "80%", animationDuration: "14s", animationDelay: "0s" }} />
          <div className="auth-particle" style={{ width: 10, height: 10, left: "35%", top: "90%", animationDuration: "18s", animationDelay: "2s" }} />
          <div className="auth-particle" style={{ width: 4, height: 4, left: "65%", top: "85%", animationDuration: "12s", animationDelay: "1s" }} />
          <div className="auth-particle" style={{ width: 8, height: 8, left: "80%", top: "95%", animationDuration: "16s", animationDelay: "3s" }} />
          <div className="auth-particle" style={{ width: 5, height: 5, left: "50%", top: "88%", animationDuration: "15s", animationDelay: "4s" }} />
        </div>

        <div className="auth-card">
          <div className="auth-brand">
            <div className="auth-logo-icon">🤖</div>
            <div>
              <div className="auth-brand-name">AI Interview Hub</div>
              <div className="auth-brand-sub">Smart Candidate Evaluator</div>
            </div>
          </div>

          <div className="auth-header">
            <p className="eyebrow">AI Interview Console</p>
            <h2>{authMode === "login" ? "Welcome Back" : "Create Account"}</h2>
            <p className="auth-subtitle">
              {authMode === "login"
                ? "Sign in to access your personalized interview practice sessions."
                : "Register to practice technical interviews with real-time AI scoring."}
            </p>
          </div>

          <div className="auth-tabs">
            <button
              className={authMode === "login" ? "auth-tab active" : "auth-tab"}
              onClick={() => {
                setAuthMode("login");
                setAuthError("");
              }}
            >
              Sign In
            </button>
            <button
              className={authMode === "register" ? "auth-tab active" : "auth-tab"}
              onClick={() => {
                setAuthMode("register");
                setAuthError("");
              }}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleAuthSubmit} className="auth-form">
            {authMode === "register" && (
              <label className="field">
                <span>Full Name</span>
                <input
                  type="text"
                  value={authName}
                  onChange={(e) => setAuthName(e.target.value)}
                  placeholder="e.g. Alex Johnson"
                  required
                />
              </label>
            )}

            <label className="field">
              <span>Email Address</span>
              <input
                type="email"
                value={authEmail}
                onChange={(e) => setAuthEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </label>

            <label className="field">
              <span>Password</span>
              <input
                type="password"
                value={authPassword}
                onChange={(e) => setAuthPassword(e.target.value)}
                placeholder="Enter password"
                required
              />
            </label>

            {authError && <div className="error-banner">{authError}</div>}

            <button type="submit" className="primary-button auth-submit-btn" disabled={isAuthSubmitting}>
              {isAuthSubmitting
                ? "Please wait..."
                : authMode === "login"
                ? "Sign In →"
                : "Create Account →"}
            </button>
          </form>

          <footer className="auth-footer">
            Designed & Developed with <span className="heart">❤️</span> by{" "}
            <a
              href="https://github.com/Harsh5102005"
              target="_blank"
              rel="noopener noreferrer"
              className="github-footer-link"
            >
              Harsh Maurya ↗
            </a>
          </footer>
        </div>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="main-header">
        <div className="brand-group">
          <p className="eyebrow">AI Interviewer</p>
          <nav className="topbar-nav">
            <button
              className={`nav-btn ${currentPage === "home" ? "active" : ""}`}
              onClick={() => setCurrentPage("home")}
            >
              Home
            </button>
            <button
              className={`nav-btn ${currentPage === "interview" ? "active" : ""}`}
              onClick={() => setCurrentPage("interview")}
            >
              Interview Console
            </button>
          </nav>
        </div>

        <div className="topbar-right">
          <div className="user-profile-badge">
            <div className="user-avatar">{user.name ? user.name.charAt(0).toUpperCase() : "U"}</div>
            <div className="user-info">
              <span className="user-name">{user.name || "User"}</span>
              <span className="user-email">{user.email}</span>
            </div>
            <button className="logout-button" onClick={handleLogout} title="Log Out">
              Logout
            </button>
          </div>
        </div>
      </header>

      {currentPage === "home" ? (
        <section className="home-container">
          <div className="hero-card">
            <div className="hero-pill">🤖 Intelligent Tech Interview Practice</div>
            <h1>Welcome back, {user.name || "Candidate"}! 👋</h1>
            <p className="hero-lead">
              Prepare for real-world technical interviews with AI-generated role-specific questions, voice answer evaluation, rubric scoring, and complete session tracking.
            </p>
            <div className="hero-btn-row">
              <button
                className="primary-button hero-cta-btn"
                onClick={() => setCurrentPage("interview")}
              >
                Start Practice Session →
              </button>
            </div>
          </div>

          <div className="home-grid-2">
            <div className="info-card">
              <div className="card-badge">Step-by-Step</div>
              <h2>How to Practice</h2>
              <div className="steps-list">
                <div className="step-item">
                  <span className="step-badge">1</span>
                  <div>
                    <strong>Select Role & Difficulty</strong>
                    <p>Enter any technical role (e.g. Java Developer, React Frontend, Full Stack) and pick your target difficulty level.</p>
                  </div>
                </div>
                <div className="step-item">
                  <span className="step-badge">2</span>
                  <div>
                    <strong>Answer Questions</strong>
                    <p>Read or replay generated questions, then type your explanation or use Voice Input for speech recognition.</p>
                  </div>
                </div>
                <div className="step-item">
                  <span className="step-badge">3</span>
                  <div>
                    <strong>Instant AI Feedback & Score</strong>
                    <p>Get evaluated against realistic grading rubrics (0 to 10 points) and review past answers in your history list.</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="info-card">
              <div className="card-badge">Key Features</div>
              <h2>Platform Capabilities</h2>
              <div className="features-list">
                <div className="feature-item">
                  <span className="feature-icon">🎯</span>
                  <div>
                    <strong>Dynamic Question Generator</strong>
                    <p>Questions automatically adapt to avoid duplicates and test core role concepts.</p>
                  </div>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">🎙️</span>
                  <div>
                    <strong>Speech Recognition Voice Input</strong>
                    <p>Dictate answers verbally to build natural interviewing confidence.</p>
                  </div>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">📊</span>
                  <div>
                    <strong>0-10 Rubric Scoring</strong>
                    <p>Specific feedback highlights missed concepts, buzzwords, or vagueness.</p>
                  </div>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">📜</span>
                  <div>
                    <strong>Live Answer History</strong>
                    <p>Keep a clear record of all questions answered during your practice run.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="past-interviews-section info-card">
            <div className="past-interviews-header">
              <div>
                <div className="card-badge">Session History</div>
                <h2>Your Past Interviews</h2>
              </div>
              <button
                className="ghost-button"
                onClick={loadPastInterviews}
                disabled={isLoadingPastInterviews}
              >
                {isLoadingPastInterviews ? "Refreshing..." : "↻ Refresh"}
              </button>
            </div>

            {isLoadingPastInterviews ? (
              <p className="empty-text">Loading your interview history...</p>
            ) : pastInterviews.length === 0 ? (
              <p className="empty-text">
                You haven't completed any interviews yet. Start a practice session to see your history here.
              </p>
            ) : (
              <div className="past-interviews-list">
                {pastInterviews.map((session) => {
                  const isExpanded = expandedInterviewId === session.id;
                  const avgScoreLabel = session.avgScore != null ? `${session.avgScore}/10` : "—";
                  let diffClass = "diff-neutral";
                  if (session.difficulty === "easy") diffClass = "diff-easy";
                  else if (session.difficulty === "medium") diffClass = "diff-medium";
                  else if (session.difficulty === "hard") diffClass = "diff-hard";
                  else if (session.difficulty === "advanced") diffClass = "diff-advanced";

                  return (
                    <div key={session.id} className="past-interview-card">
                      <div
                        className="past-interview-summary"
                        onClick={() => toggleExpandInterview(session.id)}
                      >
                        <div className="past-interview-meta">
                          <span className="past-role-label">{session.role || "Unknown Role"}</span>
                          <span className={`diff-badge ${diffClass}`}>{session.difficulty}</span>
                        </div>
                        <div className="past-interview-stats">
                          <span className="stat-item">📋 {session.answeredQuestions}/{session.totalQuestions} answered</span>
                          {session.avgScore != null && (
                            <span className="stat-item">⭐ Avg: {avgScoreLabel}</span>
                          )}
                          {session.startTime && (
                            <span className="stat-item stat-date">
                              🕐 {new Date(session.startTime).toLocaleDateString("en-IN", {
                                day: "numeric", month: "short", year: "numeric",
                                hour: "2-digit", minute: "2-digit"
                              })}
                            </span>
                          )}
                        </div>
                        <span className="expand-arrow">{isExpanded ? "▲ Hide" : "▼ View Q&A"}</span>
                      </div>

                      {isExpanded && (
                        <div className="expanded-history">
                          {isLoadingExpandedHistory ? (
                            <p className="empty-text">Loading session Q&A...</p>
                          ) : expandedInterviewHistory.length === 0 ? (
                            <p className="empty-text">No questions were loaded in this session.</p>
                          ) : (
                            expandedInterviewHistory.map((item, idx) => {
                              const answered = item.answerText != null && item.answerText !== "";
                              let badgeClass = "score-badge-neutral";
                              if (answered) {
                                if (item.score >= 7) badgeClass = "score-badge-high";
                                else if (item.score >= 4) badgeClass = "score-badge-mid";
                                else badgeClass = "score-badge-low";
                              }
                              return (
                                <div key={item.questionId || idx} className="expanded-qa-item">
                                  <div className="expanded-qa-header">
                                    <span className="history-q-num">Q{idx + 1}</span>
                                    <span className={`history-score-badge ${badgeClass}`}>
                                      {answered ? `Score: ${item.score}/10` : "Not Answered"}
                                    </span>
                                  </div>
                                  <div className="history-q-text"><strong>Q:</strong> {item.questionText}</div>
                                  {answered && (
                                    <>
                                      <div className="history-ans-text"><strong>A:</strong> {item.answerText}</div>
                                      {item.feedback && (
                                        <div className="history-feedback-text"><strong>Feedback:</strong> {item.feedback}</div>
                                      )}
                                    </>
                                  )}
                                </div>
                              );
                            })
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="banner-card">
            <div>
              <h2>Ready for your technical interview practice?</h2>
              <p>Launch the console, set up your role, and answer your first question.</p>
            </div>
            <button
              className="primary-button cta-banner-btn"
              onClick={() => setCurrentPage("interview")}
            >
              Go to Interview Console →
            </button>
          </div>
        </section>
      ) : (
        <div className="interview-layout">
          <section className="workspace">
            <header className="topbar">
              <div>
                <p className="eyebrow">Interview Console</p>
                <h1>Practice answers with instant scoring.</h1>
              </div>
              <div className="status-pill">
                <span className={interviewId ? "status-dot active" : "status-dot"} />
                {interviewId ? `${difficulty} interview` : "Setup required"}
              </div>
            </header>

            <section className="setup-panel">
              <div className="section-heading">
                <span>Interview Setup</span>
                {interviewId && <span className="meta-text">Session #{interviewId}</span>}
              </div>
              <div className="setup-grid">
                <label className="field">
                  <span>Role</span>
                  <input
                    value={role}
                    onChange={(event) => {
                      setRole(event.target.value);
                      clearInterviewSession();
                    }}
                    placeholder="Java developer"
                  />
                </label>
                <label className="field">
                  <span>Difficulty</span>
                  <select
                    value={difficulty}
                    onChange={(event) => {
                      setDifficulty(event.target.value);
                      clearInterviewSession();
                    }}
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </label>
                <button className="primary-button setup-button" onClick={startInterview} disabled={isStartingInterview}>
                  {isStartingInterview ? "Starting..." : interviewId ? "Restart Setup" : "Create Interview"}
                </button>
              </div>
            </section>

            <section className="question-panel">
              <div className="section-heading">
                <span>Question</span>
                <div className="audio-actions">
                  <button
                    className={`ghost-button sound-toggle-btn ${isSoundMuted ? "muted" : ""}`}
                    onClick={() => {
                      if (!isSoundMuted && window.speechSynthesis) {
                        window.speechSynthesis.cancel();
                      }
                      setIsSoundMuted(!isSoundMuted);
                    }}
                    title={isSoundMuted ? "Turn Question Sound ON" : "Turn Question Sound OFF"}
                  >
                    {isSoundMuted ? "🔇 Sound: OFF" : "🔊 Sound: ON"}
                  </button>
                  <button className="ghost-button" onClick={() => speak(question)} disabled={!question || isSoundMuted}>
                    Replay
                  </button>
                </div>
              </div>
              <p className={question ? "question-text" : "empty-text"}>
                {question || "Create an interview, then load your first question."}
              </p>
              <button className="primary-button" onClick={getQuestion} disabled={!interviewId || isLoadingQuestion}>
                {isLoadingQuestion ? "Loading..." : question ? "Next Question" : "Load Question"}
              </button>
            </section>

            <section className="answer-panel">
              <div className="section-heading">
                <span>Your Answer</span>
                <span className="meta-text">{wordCount} words</span>
              </div>
              <textarea
                className="answer-input"
                value={answer}
                onChange={(event) => setAnswer(event.target.value)}
                placeholder="Type your answer here, or use voice input and refine it before submitting."
                disabled={!questionId || isSubmitting}
              />
              <div className="action-row">
                <button className="secondary-button" onClick={startListening} disabled={!questionId || isListening}>
                  {isListening ? "Listening..." : "Voice Input"}
                </button>
                <button className="primary-button" onClick={submitAnswer} disabled={!questionId || isSubmitting}>
                  {isSubmitting ? "Checking..." : "Submit Answer"}
                </button>
              </div>
            </section>

            <section className="history-panel">
              <div className="section-heading">
                <span>Answer History</span>
                <div className="history-heading-meta">
                  {history.length > 0 && (
                    <span className="meta-badge">
                      {history.filter((item) => item.answerText !== null).length} / {history.length} Answered
                    </span>
                  )}
                  {interviewId && (
                    <button
                      className="ghost-button refresh-history-btn"
                      onClick={() => loadHistory(interviewId)}
                      disabled={isLoadingHistory}
                    >
                      {isLoadingHistory ? "Refreshing..." : "Refresh"}
                    </button>
                  )}
                </div>
              </div>

              {history.length === 0 ? (
                <p className="empty-text">
                  No answer history yet. Start an interview and load questions to build your record.
                </p>
              ) : (
                <div className="history-list">
                  {history.map((item, index) => {
                    const isAnswered = item.answerText !== null && item.answerText !== undefined;
                    const itemScore = item.score;
                    let scoreBadgeClass = "score-badge-neutral";
                    if (isAnswered) {
                      if (itemScore >= 7) scoreBadgeClass = "score-badge-high";
                      else if (itemScore >= 4) scoreBadgeClass = "score-badge-mid";
                      else scoreBadgeClass = "score-badge-low";
                    }

                    return (
                      <div key={item.questionId || index} className="history-card">
                        <div className="history-card-header">
                          <span className="history-q-num">Q{index + 1}</span>
                          <span className={`history-score-badge ${scoreBadgeClass}`}>
                            {isAnswered ? `Score: ${itemScore}/10` : "Pending Answer"}
                          </span>
                        </div>

                        <div className="history-q-text">
                          <strong>Question:</strong> {item.questionText}
                        </div>

                        {isAnswered ? (
                          <>
                            <div className="history-ans-text">
                              <strong>Your Answer:</strong> {item.answerText || "(Empty response)"}
                            </div>
                            {item.feedback && (
                              <div className="history-feedback-text">
                                <strong>Feedback:</strong> {item.feedback}
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="history-pending-text">
                            Awaiting your response for this question.
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </section>

            {error && <div className="error-banner">{error}</div>}
          </section>

          <aside className="score-panel">
            <div className="score-header">
              <span>Feedback</span>
              <strong>{score === "" ? "--" : `${score}/10`}</strong>
            </div>
            <div className="score-ring" style={{ "--score": `${scorePercent}%` }}>
              <span>{score === "" ? "--" : score}</span>
            </div>
            <div className="score-track">
              <span style={{ width: `${scorePercent}%` }} />
            </div>
            <p className={feedback ? "feedback-text" : "empty-text"}>
              {feedback || "Submit an answer to see score, feedback, and improvement guidance."}
            </p>
          </aside>
        </div>
      )}

      <footer className="app-footer">
        <div className="footer-content">
          <p>
            AI Technical Interview Practice & Evaluation Platform • Made with <span className="heart">❤️</span> by{" "}
            <a
              href="https://github.com/Harsh5102005"
              target="_blank"
              rel="noopener noreferrer"
              className="github-footer-link"
            >
              Harsh Maurya ↗
            </a>
          </p>
        </div>
      </footer>
    </main>
  );
}

export default App;
