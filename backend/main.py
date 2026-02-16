"""
Cybersecurity Incident Tracker - FastAPI Backend
Production-ready API for managing security incidents and vulnerabilities
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Import routers
from app.routes import auth, incidents, vulnerabilities, dashboard, alerts, integrations

# ============================================================================
# FastAPI Lifespan for startup/shutdown logs
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Incident Tracker API starting up...")
    yield
    # Shutdown
    print("🛑 Incident Tracker API shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Cybersecurity Incident Tracker API",
    description="Enterprise-grade incident and vulnerability management platform",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================================
# CORS Configuration
# ============================================================================

# Add your frontend domain here (WITHOUT trailing slash)
FRONTEND_DOMAIN = "https://v0-cybersecurity-tracker-dashboard-opal.vercel.app"

# You can also allow localhost for local testing
allowed_origins = [
    FRONTEND_DOMAIN,
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"], # allow POST, GET, OPTIONS, etc
    allow_headers=["*"], # allow headers like Content-Type, Authorization
)

# ============================================================================
# Security
# ============================================================================

security = HTTPBearer()

# ============================================================================
# Health Check & Root Routes
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API status"""
    return {
        "status": "operational",
        "service": "Cybersecurity Incident Tracker",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "incident-tracker-api",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

# ============================================================================
# API Routes
# ============================================================================

app.include_router(auth.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")
app.include_router(vulnerabilities.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(integrations.router, prefix="/api")

# ============================================================================
# Run app
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),  # Use PORT env var if provided by Render
        reload=True
    )
