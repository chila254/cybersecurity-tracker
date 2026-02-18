"""
Cybersecurity Incident Tracker - FastAPI Backend
Production-ready API for managing security incidents and vulnerabilities
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
from create_tables import create_tables  # your table-creation function

# ============================================================================
# Load environment variables
# ============================================================================

load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
PORT = int(os.getenv("PORT", 8000))

# ============================================================================
# Create database tables (run once safely)
# ============================================================================

try:
    create_tables()
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️ Tables may already exist or creation failed: {e}")

# ============================================================================
# Import Routers
# ============================================================================

from app.routes import auth, incidents, vulnerabilities, dashboard, alerts, integrations

# ============================================================================
# FastAPI Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Incident Tracker API starting up...")
    yield
    # Shutdown
    print("🛑 Incident Tracker API shutting down...")

# ============================================================================
# Initialize FastAPI app
# ============================================================================

app = FastAPI(
    title="Cybersecurity Incident Tracker API",
    description="Enterprise-grade incident and vulnerability management platform",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================================
# CORS Configuration
# ============================================================================

FRONTEND_DOMAIN = "https://cybersecurity-tracker.vercel.app/"

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
    allow_methods=["*"],
    allow_headers=["*"]
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
        "version": "1.0.0",
        "environment": ENVIRONMENT
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "incident-tracker-api",
        "environment": ENVIRONMENT
    }

# ============================================================================
# Global HTTP Exception Handler
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

# ============================================================================
# API Routes
# ============================================================================

# All API routes are under /api
app.include_router(auth.router, prefix="/api/auth")
app.include_router(incidents.router, prefix="/api/incidents")
app.include_router(vulnerabilities.router, prefix="/api/vulnerabilities")
app.include_router(dashboard.router, prefix="/api/dashboard")
app.include_router(alerts.router, prefix="/api/alerts")
app.include_router(integrations.router, prefix="/api/integrations")

# ============================================================================
# Run app
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True
    )
