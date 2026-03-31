from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import session, student

app = FastAPI(title="LearnForge AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    print("LearnForge AI started. Database ready.")

app.include_router(session.router)
app.include_router(student.router)

@app.get("/")
def root():
    return {"status": "LearnForge AI is running"}