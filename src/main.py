"""
Main Application Module

This is the entry point for the FastAPI application.
It initializes the app, configures middleware, and registers routes.

Responsibilities:
    - Create FastAPI application instance
    - Configure CORS, middleware, exception handlers
    - Register API routers
    - Handle application lifecycle (startup/shutdown)

Example:
    >>> # Run application
    >>> uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from api.v1.router import api_router
from config.settings import settings
from config.dependencies import init_db, close_db
from config.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events for the application.

    Startup:
        - Initialize database
        - Log application start

    Shutdown:
        - Close database connections
        - Log application shutdown

    Example:
        This is automatically called by FastAPI, no manual invocation needed.
    """
    # Startup
    logger.info("🚀 Starting application...")
    await init_db()
    logger.info("✅ Database initialized")
    logger.info(
        f"🌐 Application running in {'DEBUG' if settings.DEBUG else 'PRODUCTION'} mode"
    )

    yield

    # Shutdown
    logger.info("👋 Shutting down application...")
    await close_db()
    logger.info("✅ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI service with Pragmatic Clean Architecture",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(api_router, prefix="/api")


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.

    Returns application health status.
    Used by load balancers and monitoring systems.

    Returns:
        dict: Health status

    Example:
        >>> GET /health
        >>> {"status": "healthy", "version": "1.0.0"}
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": "debug" if settings.DEBUG else "production",
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint.

    Returns basic API information.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
