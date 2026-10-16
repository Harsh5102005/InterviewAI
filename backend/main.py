"""
FastAPI application entry point — equivalent of AiApplication.java (@SpringBootApplication).

Runs on port 8080 to match the Spring Boot server the React frontend expects.
CORS is configured with origins="*" to match the original @CrossOrigin(origins = "*").
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import auth, interview, question, answer

# Configure logging (mirrors SLF4J/Logback from Spring Boot)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
)

# Create all tables if they don't exist (mirrors spring.jpa.hibernate.ddl-auto=update)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Interview Platform",
    description="AI-powered technical interview practice & evaluation API",
    version="0.0.1-SNAPSHOT",
)

# CORS — matches @CrossOrigin(origins = "*") on every Java controller
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers (equivalent of Spring's component scanning for @RestControllers)
app.include_router(auth.router)
app.include_router(interview.router)
app.include_router(question.router)
app.include_router(answer.router)


@app.get("/")
def root():
    return {"status": "running", "app": "AI Interview Platform (FastAPI)"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
