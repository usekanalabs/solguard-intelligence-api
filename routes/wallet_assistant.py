"""
Wallet Assistant AI API routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List

from models.schemas import (
    WalletAnalysisRequest,
    WalletAnalysisResponse,
    ChatRequest,
    ChatResponse,
    RiskLevel
)
from services.ai_service import AIService
from services.solana_service import SolanaService

router = APIRouter()
ai_service = AIService()
solana_service = SolanaService()

@router.post("/analyze", response_model=WalletAnalysisResponse)
async def analyze_wallet(request: WalletAnalysisRequest):
    """
    Analyze a Solana wallet for security and portfolio insights
    
    Provides:
    - Portfolio composition analysis
    - Transaction pattern analysis
    - Suspicious activity detection
    - AI-powered insights and recommendations
    """
    try:
        # Get wallet balance and tokens
        wallet_data = await solana_service.get_wallet_info(request.wallet_address)
        
        if not wallet_data:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        # Analyze transactions if requested
        transaction_analysis = None
        if request.analyze_transactions:
            transaction_analysis = await solana_service.analyze_transactions(
                request.wallet_address
            )
        
        # Check for suspicious activity
        suspicious_activities = []
        if request.check_suspicious_activity:
            suspicious_activities = await detect_suspicious_activity(
                request.wallet_address,
                transaction_analysis
            )
        
        # Portfolio analysis
        portfolio_analysis = analyze_portfolio(wallet_data)
        
        # Calculate wallet risk score
        risk_score = calculate_wallet_risk(
            wallet_data,
            transaction_analysis,
            suspicious_activities
        )
        
        # Get AI insights
        ai_context = {
            "wallet_data": wallet_data,
            "portfolio": portfolio_analysis,
            "transactions": transaction_analysis,
            "suspicious_activities": suspicious_activities
        }
        ai_insights = await ai_service.generate_wallet_insights(ai_context)
        
        # Generate recommendations
        recommendations = generate_wallet_recommendations(
            portfolio_analysis,
            risk_score,
            suspicious_activities
        )
        
        return WalletAnalysisResponse(
            wallet_address=request.wallet_address,
            balance=wallet_data.get("balance", 0),
            token_count=len(wallet_data.get("tokens", [])),
            transaction_count=wallet_data.get("transaction_count", 0),
            risk_score=risk_score,
            risk_level=get_risk_level(risk_score),
            suspicious_activities=suspicious_activities,
            portfolio_analysis=portfolio_analysis,
            ai_insights=ai_insights,
            recommendations=recommendations,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wallet analysis failed: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Chat with AI wallet assistant for personalized guidance
    
    The assistant can help with:
    - Portfolio optimization advice
    - Risk assessment questions
    - Transaction guidance
    - Market insights
    - Security recommendations
    """
    try:
        # Prepare context for AI
        context = request.context or {}
        
        # If wallet address provided, add wallet data to context
        if request.wallet_address:
            wallet_data = await solana_service.get_wallet_info(request.wallet_address)
            context["wallet_data"] = wallet_data
        
        # Get AI response
        response = await ai_service.chat_with_user(request.message, context)
        
        # Extract suggestions and warnings from response
        suggestions = extract_suggestions(response)
        warnings = extract_warnings(response)
        
        return ChatResponse(
            response=response,
            suggestions=suggestions,
            warnings=warnings,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.get("/portfolio/{wallet_address}")
async def get_portfolio_summary(wallet_address: str):
    """Get detailed portfolio summary with AI insights"""
    try:
        wallet_data = await solana_service.get_wallet_info(wallet_address)
        portfolio = analyze_portfolio(wallet_data)
        
        return {
            "wallet_address": wallet_address,
            "portfolio": portfolio,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio: {str(e)}")

def analyze_portfolio(wallet_data: dict) -> dict:
    """Analyze wallet portfolio composition"""
    tokens = wallet_data.get("tokens", [])
    total_value = wallet_data.get("total_value_usd", 0)
    
    portfolio = {
        "total_value_usd": total_value,
        "token_count": len(tokens),
        "diversification_score": calculate_diversification(tokens),
        "top_holdings": sorted(tokens, key=lambda x: x.get("value_usd", 0), reverse=True)[:5],
        "risk_distribution": categorize_holdings_by_risk(tokens)
    }
    
    return portfolio

def calculate_diversification(tokens: List[dict]) -> float:
    """Calculate portfolio diversification score (0-1)"""
    if not tokens:
        return 0.0
    
    # Simple Herfindahl index calculation
    total_value = sum(t.get("value_usd", 0) for t in tokens)
    if total_value == 0:
        return 0.0
    
    herfindahl = sum((t.get("value_usd", 0) / total_value) ** 2 for t in tokens)
    diversification = 1 - herfindahl
    
    return round(diversification, 2)

def categorize_holdings_by_risk(tokens: List[dict]) -> dict:
    """Categorize holdings by risk level"""
    risk_distribution = {
        "low_risk": 0,
        "medium_risk": 0,
        "high_risk": 0
    }
    
    for token in tokens:
        risk = token.get("risk_level", "medium")
        if risk in ["low", "safe"]:
            risk_distribution["low_risk"] += token.get("value_usd", 0)
        elif risk in ["high", "critical"]:
            risk_distribution["high_risk"] += token.get("value_usd", 0)
        else:
            risk_distribution["medium_risk"] += token.get("value_usd", 0)
    
    return risk_distribution

async def detect_suspicious_activity(wallet_address: str, transaction_analysis: dict) -> List[str]:
    """Detect suspicious activities in wallet"""
    suspicious = []
    
    if not transaction_analysis:
        return suspicious
    
    # Check for unusual transaction patterns
    if transaction_analysis.get("high_frequency_trading", False):
        suspicious.append("Unusual high-frequency trading detected")
    
    # Check for interactions with known scam addresses
    if transaction_analysis.get("scam_interactions", 0) > 0:
        suspicious.append("Interactions with flagged addresses detected")
    
    # Check for large sudden transfers
    if transaction_analysis.get("large_transfers", 0) > 5:
        suspicious.append("Multiple large transfers detected")
    
    return suspicious

def calculate_wallet_risk(wallet_data: dict, transaction_analysis: dict, suspicious: List[str]) -> float:
    """Calculate overall wallet risk score"""
    risk_score = 0.0
    
    # Risk from suspicious activities
    risk_score += len(suspicious) * 0.15
    
    # Risk from portfolio concentration
    tokens = wallet_data.get("tokens", [])
    if tokens:
        diversification = calculate_diversification(tokens)
        if diversification < 0.3:
            risk_score += 0.2
    
    # Risk from transaction patterns
    if transaction_analysis:
        if transaction_analysis.get("failed_transactions", 0) > 10:
            risk_score += 0.1
    
    return min(risk_score, 1.0)

def get_risk_level(risk_score: float) -> RiskLevel:
    """Convert risk score to risk level"""
    if risk_score < 0.25:
        return RiskLevel.LOW
    elif risk_score < 0.5:
        return RiskLevel.MEDIUM
    elif risk_score < 0.75:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL

def generate_wallet_recommendations(portfolio: dict, risk_score: float, suspicious: List[str]) -> List[str]:
    """Generate wallet-specific recommendations"""
    recommendations = []
    
    # Diversification recommendations
    diversification = portfolio.get("diversification_score", 0)
    if diversification < 0.3:
        recommendations.append("📊 Consider diversifying your portfolio across more tokens")
    
    # Risk-based recommendations
    if risk_score > 0.5:
        recommendations.append("⚠️ High risk detected - review your holdings")
    
    if suspicious:
        recommendations.append("🔒 Suspicious activity detected - enable additional security measures")
    
    # Portfolio balance recommendations
    risk_dist = portfolio.get("risk_distribution", {})
    high_risk_pct = risk_dist.get("high_risk", 0) / portfolio.get("total_value_usd", 1)
    if high_risk_pct > 0.5:
        recommendations.append("⚡ Over 50% in high-risk assets - consider rebalancing")
    
    return recommendations

def extract_suggestions(response: str) -> List[str]:
    """Extract actionable suggestions from AI response"""
    # Simple extraction - in production, use more sophisticated NLP
    suggestions = []
    lines = response.split('\n')
    for line in lines:
        if any(keyword in line.lower() for keyword in ['suggest', 'recommend', 'consider', 'try']):
            suggestions.append(line.strip())
    return suggestions[:3]  # Return top 3

def extract_warnings(response: str) -> List[str]:
    """Extract warnings from AI response"""
    warnings = []
    lines = response.split('\n')
    for line in lines:
        if any(keyword in line.lower() for keyword in ['warning', 'caution', 'risk', 'danger', 'avoid']):
            warnings.append(line.strip())
    return warnings[:3]  # Return top 3
