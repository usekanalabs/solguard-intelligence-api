"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CoinAnalysisRequest(BaseModel):
    """Request model for coin analysis"""
    token_address: str = Field(..., description="Solana token address")
    include_social: bool = Field(default=True, description="Include social media analysis")
    include_liquidity: bool = Field(default=True, description="Include liquidity analysis")

class CoinAnalysisResponse(BaseModel):
    """Response model for coin analysis"""
    token_address: str
    token_name: Optional[str]
    token_symbol: Optional[str]
    risk_score: float = Field(..., ge=0, le=1, description="Risk score from 0 (safe) to 1 (dangerous)")
    risk_level: RiskLevel
    market_cap: Optional[float]
    liquidity: Optional[float]
    holder_count: Optional[int]
    red_flags: List[str]
    green_flags: List[str]
    ai_analysis: str
    recommendations: List[str]
    timestamp: datetime

class WalletAnalysisRequest(BaseModel):
    """Request model for wallet analysis"""
    wallet_address: str = Field(..., description="Solana wallet address")
    analyze_transactions: bool = Field(default=True, description="Analyze transaction history")
    check_suspicious_activity: bool = Field(default=True, description="Check for suspicious activity")

class WalletAnalysisResponse(BaseModel):
    """Response model for wallet analysis"""
    wallet_address: str
    balance: float
    token_count: int
    transaction_count: int
    risk_score: float
    risk_level: RiskLevel
    suspicious_activities: List[str]
    portfolio_analysis: Dict[str, Any]
    ai_insights: str
    recommendations: List[str]
    timestamp: datetime

class ChatRequest(BaseModel):
    """Request model for AI chat"""
    message: str = Field(..., description="User message")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    wallet_address: Optional[str] = Field(default=None, description="User's wallet address for context")

class ChatResponse(BaseModel):
    """Response model for AI chat"""
    response: str
    suggestions: Optional[List[str]]
    warnings: Optional[List[str]]
    timestamp: datetime

class ThreatDetectionRequest(BaseModel):
    """Request model for threat detection"""
    transaction_data: Dict[str, Any] = Field(..., description="Transaction data to analyze")
    wallet_address: str = Field(..., description="Wallet address initiating transaction")

class ThreatDetectionResponse(BaseModel):
    """Response model for threat detection"""
    is_safe: bool
    risk_score: float
    risk_level: RiskLevel
    threats_detected: List[str]
    analysis: str
    should_proceed: bool
    timestamp: datetime
