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

class WalletAuthRequest(BaseModel):
    """Request model for wallet authentication challenge"""
    wallet_address: str = Field(..., description="Solana wallet address")

class WalletAuthResponse(BaseModel):
    """Response model for authentication challenge"""
    challenge: str = Field(..., description="Challenge message to sign")
    expires_at: datetime = Field(..., description="Challenge expiration time")
    wallet_address: str

class WalletVerifyRequest(BaseModel):
    """Request model for signature verification"""
    wallet_address: str = Field(..., description="Solana wallet address")
    signature: str = Field(..., description="Base58 encoded signature")
    message: str = Field(..., description="Original challenge message")

class TokenResponse(BaseModel):
    """Response model for JWT token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration in seconds")
    wallet_address: str
    email: Optional[str] = None
    auth_method: str = Field(default="wallet", description="Authentication method used")

class UserProfile(BaseModel):
    """User profile model"""
    wallet_address: str
    created_at: datetime
    last_login: datetime
    preferences: Dict[str, Any] = Field(default_factory=dict)
    email: Optional[str] = None
    auth_method: str = Field(default="wallet", description="Primary authentication method")
    linked_accounts: List[str] = Field(default_factory=list, description="Linked authentication methods")

class GoogleAuthRequest(BaseModel):
    """Request model for Google OAuth"""
    code: str = Field(..., description="Authorization code from Google")
    redirect_uri: str = Field(..., description="Redirect URI used in OAuth flow")

class GoogleAuthResponse(BaseModel):
    """Response model for Google OAuth"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    email: str
    wallet_address: Optional[str] = None
    auth_method: str = "google"

# Signal-related schemas
class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    ALERT = "alert"

class SignalStrength(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

class TrendingTokenRequest(BaseModel):
    """Request model for trending tokens"""
    time_period: str = Field(default="24h", description="Time period: 5m, 1h, 6h, 24h")
    limit: int = Field(default=20, ge=1, le=100, description="Number of tokens to return")
    order_by: str = Field(default="volume", description="Order by: volume, swaps, price_change")

class TrendingTokenResponse(BaseModel):
    """Response model for trending token"""
    token_address: str
    token_name: str
    token_symbol: str
    price: float
    price_change_24h: float
    volume_24h: float
    liquidity: float
    market_cap: Optional[float]
    swaps_24h: int
    holders: int
    risk_score: float
    timestamp: datetime

class SignalRequest(BaseModel):
    """Request model for trading signal generation"""
    token_address: Optional[str] = Field(default=None, description="Specific token to analyze")
    wallet_address: Optional[str] = Field(default=None, description="User wallet for personalized signals")
    signal_types: List[SignalType] = Field(default=[SignalType.BUY, SignalType.SELL], description="Types of signals to generate")
    min_strength: SignalStrength = Field(default=SignalStrength.MODERATE, description="Minimum signal strength")

class TradingSignal(BaseModel):
    """Trading signal model"""
    signal_id: str
    token_address: str
    token_name: str
    token_symbol: str
    signal_type: SignalType
    signal_strength: SignalStrength
    confidence: float = Field(..., ge=0, le=1, description="AI confidence score")
    price: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    reasoning: str
    key_factors: List[str]
    risk_level: RiskLevel
    timestamp: datetime
    expires_at: datetime

class SignalResponse(BaseModel):
    """Response model for signals"""
    signals: List[TradingSignal]
    market_overview: Dict[str, Any]
    ai_summary: str
    timestamp: datetime

class SignalSubscriptionRequest(BaseModel):
    """Request model for signal subscription"""
    wallet_address: str
    signal_types: List[SignalType] = Field(default=[SignalType.BUY, SignalType.SELL, SignalType.ALERT])
    min_strength: SignalStrength = Field(default=SignalStrength.MODERATE)
    tokens: Optional[List[str]] = Field(default=None, description="Specific tokens to monitor")

class SignalSubscriptionResponse(BaseModel):
    """Response model for signal subscription"""
    subscription_id: str
    wallet_address: str
    active: bool
    created_at: datetime
    settings: Dict[str, Any]
