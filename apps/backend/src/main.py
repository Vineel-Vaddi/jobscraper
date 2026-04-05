from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.routers import auth, documents, profiles, jobs

app = FastAPI(title="JobTailor API")

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

@app.get("/health")
def health_check():
    return {"status": "ok"}
