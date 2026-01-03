
from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(
    title="WindGPT",
    version="0.1.0",
    description="AI-powered site feasibility assessment for wind energy projects using geospatial analysis."
)

app.include_router(api_router, prefix="/api")
