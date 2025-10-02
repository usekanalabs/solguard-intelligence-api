"""
Coin Analyzer API routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import httpx
from datetime import datetime

from models.schemas import (
    CoinAnalysisRequest,
    CoinAnalysisResponse,
    RiskLevel
)
from services.ai_service import AIService
from services.solana_service import SolanaService

router = APIRouter()
ai_service = AIService()
solana_service = SolanaService()

@router.post("/analyze", response_model=CoinAnalysisResponse)
async def analyze_coin(request: CoinAnalysisRequest):
    """
    Analyze a Solana token for potential risks and opportunities
    
    This endpoint performs comprehensive analysis including:
    - Smart contract verification
    - Liquidity analysis
    - Holder distribution
    - Social sentiment analysis
    - AI-powered risk assessment
    """
    try:
        # Fetch token data from Solana
        token_data = await solana_service.get_token_info(request.token_address)
        
        if not token_data:
            raise HTTPException(status_code=404, detail="Token not found")
        
        # Analyze liquidity if requested
        liquidity_data = None
        if request.include_liquidity:
            liquidity_data = await solana_service.get_liquidity_info(request.token_address)
        
        # Get holder information
        holder_data = await solana_service.get_holder_distribution(request.token_address)
        
        # Perform AI analysis
        analysis_context = {
            "token_data": token_data,
            "liquidity_data": liquidity_data,
            "holder_data": holder_data
        }
        
        ai_analysis = await ai_service.analyze_token_risk(analysis_context)
        
        # Calculate risk score and identify flags
        risk_score = calculate_risk_score(token_data, liquidity_data, holder_data)
        red_flags = identify_red_flags(token_data, liquidity_data, holder_data)
        green_flags = identify_green_flags(token_data, liquidity_data, holder_data)
        
        # Determine risk level
        risk_level = get_risk_level(risk_score)
        
        # Generate recommendations
        recommendations = generate_recommendations(risk_score, red_flags, green_flags)
        
        return CoinAnalysisResponse(
            token_address=request.token_address,
            token_name=token_data.get("name"),
            token_symbol=token_data.get("symbol"),
            risk_score=risk_score,
            risk_level=risk_level,
            market_cap=token_data.get("market_cap"),
            liquidity=liquidity_data.get("total_liquidity") if liquidity_data else None,
            holder_count=holder_data.get("holder_count"),
            red_flags=red_flags,
            green_flags=green_flags,
            ai_analysis=ai_analysis,
            recommendations=recommendations,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/trending")
async def get_trending_coins():
    """Get trending Solana tokens with safety scores"""
    try:
        trending = await solana_service.get_trending_tokens()
        return {
            "trending_tokens": trending,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending coins: {str(e)}")

@router.get("/watchlist/{wallet_address}")
async def get_watchlist(wallet_address: str):
    """Get personalized watchlist based on wallet activity"""
    try:
        watchlist = await solana_service.generate_watchlist(wallet_address)
        return {
            "wallet_address": wallet_address,
            "watchlist": watchlist,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate watchlist: {str(e)}")

def calculate_risk_score(token_data: Dict, liquidity_data: Dict, holder_data: Dict) -> float:
    """Calculate overall risk score for a token"""
    risk_score = 0.0
    
    # Liquidity risk
    if liquidity_data:
        liquidity = liquidity_data.get("total_liquidity", 0)
        if liquidity < 10000:
            risk_score += 0.3
        elif liquidity < 50000:
            risk_score += 0.15
    
    # Holder concentration risk
    if holder_data:
        top_holder_percentage = holder_data.get("top_10_percentage", 0)
        if top_holder_percentage > 50:
            risk_score += 0.3
        elif top_holder_percentage > 30:
            risk_score += 0.15
    
    # Contract verification
    if not token_data.get("verified", False):
        risk_score += 0.2
    
    # Age of token
    created_days_ago = token_data.get("age_days", 0)
    if created_days_ago < 7:
        risk_score += 0.2
    
    return min(risk_score, 1.0)

def identify_red_flags(token_data: Dict, liquidity_data: Dict, holder_data: Dict) -> List[str]:
    """Identify red flags in token analysis"""
    flags = []
    
    if liquidity_data and liquidity_data.get("total_liquidity", 0) < 10000:
        flags.append("Very low liquidity - high risk of rug pull")
    
    if holder_data and holder_data.get("top_10_percentage", 0) > 50:
        flags.append("High holder concentration - whale manipulation risk")
    
    if not token_data.get("verified", False):
        flags.append("Unverified contract - proceed with extreme caution")
    
    if token_data.get("age_days", 0) < 7:
        flags.append("Very new token - high volatility expected")
    
    if token_data.get("mint_authority_enabled", False):
        flags.append("Mint authority not revoked - unlimited supply risk")
    
    return flags

def identify_green_flags(token_data: Dict, liquidity_data: Dict, holder_data: Dict) -> List[str]:
    """Identify positive indicators in token analysis"""
    flags = []
    
    if liquidity_data and liquidity_data.get("total_liquidity", 0) > 100000:
        flags.append("Strong liquidity pool")
    
    if holder_data and holder_data.get("holder_count", 0) > 1000:
        flags.append("Large holder base - good distribution")
    
    if token_data.get("verified", False):
        flags.append("Verified contract")
    
    if token_data.get("age_days", 0) > 90:
        flags.append("Established token with history")
    
    if not token_data.get("mint_authority_enabled", False):
        flags.append("Mint authority revoked - fixed supply")
    
    return flags

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

def generate_recommendations(risk_score: float, red_flags: List[str], green_flags: List[str]) -> List[str]:
    """Generate actionable recommendations"""
    recommendations = []
    
    if risk_score > 0.7:
        recommendations.append("⚠️ High risk detected - avoid investing")
        recommendations.append("Consider waiting for more established tokens")
    elif risk_score > 0.4:
        recommendations.append("⚡ Moderate risk - only invest what you can afford to lose")
        recommendations.append("Set strict stop-loss limits")
    else:
        recommendations.append("✅ Relatively safe - still do your own research")
        recommendations.append("Consider dollar-cost averaging for entry")
    
    if len(red_flags) > 3:
        recommendations.append("Multiple red flags detected - extreme caution advised")
    
    if len(green_flags) > 3:
        recommendations.append("Multiple positive indicators - favorable risk/reward")
    
    return recommendations
