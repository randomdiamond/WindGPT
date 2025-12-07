
from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(
    title="WindGPT",
    version="0.1.0",
    description="KI-Agent für Windpark-Standortbewertung"
)

app.include_router(api_router, prefix="/api")
