"""
Main FastAPI application for ESG Compliance Tracker.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uvicorn

try:
    from app.core.config import settings
except Exception:
    from config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ESG Compliance Tracker for retail SMBs - optimized for free LLM usage",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "model_provider": settings.model_provider
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    if settings.debug:
        # In debug mode, return detailed error information
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        # In production, return generic error message
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )


# Import and include routers (support both flat layout and app.api package layout)
try:
    from app.api import auth as auth_api
    from app.api import esg as esg_api
    from app.api import upload as upload_api
    from app.api import scraping as scraping_api
    from app.api import tasks as tasks_api
    from app.api import predictive as predictive_api
except Exception:
    import auth as auth_api
    import esg as esg_api
    import upload as upload_api
    import scraping as scraping_api
    import tasks as tasks_api
    import predictive as predictive_api

app.include_router(auth_api.router, prefix="/auth", tags=["authentication"])
app.include_router(esg_api.router, prefix="/esg", tags=["esg"])
app.include_router(upload_api.router, prefix="/upload", tags=["csv-upload"])
app.include_router(scraping_api.router, prefix="/scraping", tags=["web-scraping"])
app.include_router(tasks_api.router, prefix="/tasks", tags=["ai-tasks"])
app.include_router(predictive_api.router, prefix="/predictive", tags=["predictive-compliance"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

