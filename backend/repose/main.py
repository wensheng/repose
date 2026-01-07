from pathlib import Path
from fastapi import FastAPI
from dotenv import load_dotenv
backend_dir = Path(__file__).parent.parent
load_dotenv(backend_dir / '.env')

from repose.core.config import settings
from repose.api.api import api_router
from repose.core.middleware import MetricsMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(MetricsMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to Repose API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
