from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.routers.auth import router as auth_router
from src.routers.documents import router as documents_router

app = FastAPI(title="JobTailor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(documents_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
