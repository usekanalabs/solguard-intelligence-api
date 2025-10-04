"""
Kana - Intelligent Solana Ecosystem Companion API
Main application entry point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from routes import coin_analyzer, wallet_assistant, security, auth, signals
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("🚀 Kana API starting up...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    yield
    print("👋 Kana API shutting down...")

app = FastAPI(
    title="Kana API",
    description="Intelligent companion for navigating the Solana ecosystem safely",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(coin_analyzer.router, prefix="/api/v1/coin", tags=["Coin Analyzer"])
app.include_router(wallet_assistant.router, prefix="/api/v1/wallet", tags=["Wallet Assistant"])
app.include_router(security.router, prefix="/api/v1/security", tags=["Security"])
app.include_router(signals.router, prefix="/api/v1/signals", tags=["Trading Signals"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Kana API",
        "version": "1.0.0",
        "description": "Your intelligent companion for navigating the Solana ecosystem safely",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "kana-api"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development"
    )
