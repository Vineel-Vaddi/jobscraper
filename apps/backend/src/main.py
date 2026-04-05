from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database.database import engine, Base
from src.config import settings
from src.routers import auth, documents, profiles, jobs, resume, admin
from src.telemetry.middleware import PrometheusMiddleware

app = FastAPI(title="JobTailor API")

app.add_middleware(PrometheusMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(profiles.router)
app.include_router(jobs.router)
app.include_router(resume.router)
app.include_router(admin.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
