"""
Signal routes for trading signals and market intelligence
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from models.schemas import (
    TrendingTokenRequest, TrendingTokenResponse,
    SignalRequest, SignalResponse, TradingSignal,
    SignalSubscriptionRequest, SignalSubscriptionResponse
)
from services.gmgn_service import GMGNService
from services.signal_service import SignalService
from middleware.auth_middleware import get_current_user

router = APIRouter()

@router.get("/trending", response_model=List[TrendingTokenResponse])
async def get_trending_tokens(
    time_period: str = "24h",
    limit: int = 20,
    order_by: str = "volume"
):
    """
    Get trending tokens from GMGN.AI
    
    - **time_period**: Time period (5m, 1h, 6h, 24h)
    - **limit**: Number of tokens to return (1-100)
    - **order_by**: Sort criteria (volume, swaps, price_change)
    """
    gmgn_service = GMGNService()
    
    try:
        tokens = await gmgn_service.get_trending_tokens(
            time_period=time_period,
            order_by=order_by,
            limit=min(limit, 100)
        )
        
        # Calculate basic risk scores
        response_tokens = []
        for token in tokens:
            risk_score = calculate_basic_risk_score(token)
            
            response_tokens.append(TrendingTokenResponse(
                token_address=token["token_address"],
                token_name=token["token_name"],
                token_symbol=token["token_symbol"],
                price=token["price"],
                price_change_24h=token["price_change_24h"],
                volume_24h=token["volume_24h"],
                liquidity=token["liquidity"],
                market_cap=token["market_cap"],
                swaps_24h=token["swaps_24h"],
                holders=token["holders"],
                risk_score=risk_score,
                timestamp=datetime.utcnow()
            ))
        
        return response_tokens
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trending tokens: {str(e)}"
        )
    finally:
        await gmgn_service.close()

@router.post("/generate", response_model=SignalResponse)
async def generate_signals(
    request: SignalRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered trading signals
    
    Requires authentication. Analyzes market data from GMGN.AI and generates
    intelligent trading signals using OpenAI.
    """
    signal_service = SignalService()
    
    try:
        # Generate signals
        signals = await signal_service.generate_signals(
            token_address=request.token_address,
            wallet_address=request.wallet_address or current_user.get("wallet_address"),
            signal_types=request.signal_types,
            min_strength=request.min_strength
        )
        
        # Get market overview
        market_overview = await signal_service.get_market_overview()
        
        # Generate AI summary
        ai_summary = generate_signal_summary(signals, market_overview)
        
        return SignalResponse(
            signals=signals,
            market_overview=market_overview,
            ai_summary=ai_summary,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate signals: {str(e)}"
        )

@router.post("/subscribe", response_model=SignalSubscriptionResponse)
async def subscribe_to_signals(
    request: SignalSubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Subscribe to real-time trading signals
    
    Requires authentication. Creates a subscription for personalized trading signals.
    """
    # In production, this would store subscription in database
    subscription_id = f"sub_{current_user.get('wallet_address')}_{datetime.utcnow().timestamp()}"
    
    return SignalSubscriptionResponse(
        subscription_id=subscription_id,
        wallet_address=request.wallet_address,
        active=True,
        created_at=datetime.utcnow(),
        settings={
            "signal_types": [st.value for st in request.signal_types],
            "min_strength": request.min_strength.value,
            "tokens": request.tokens or []
        }
    )

@router.get("/token/{token_address}", response_model=TradingSignal)
async def get_token_signal(
    token_address: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get trading signal for a specific token
    
    Requires authentication. Analyzes a specific token and returns a trading signal.
    """
    signal_service = SignalService()
    
    try:
        signals = await signal_service.generate_signals(
            token_address=token_address,
            wallet_address=current_user.get("wallet_address")
        )
        
        if not signals:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No signal generated for this token"
            )
        
        return signals[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate signal: {str(e)}"
        )

def calculate_basic_risk_score(token: dict) -> float:
    """Calculate basic risk score for a token"""
    risk_score = 0.5  # Start neutral
    
    # Liquidity risk
    liquidity = token.get("liquidity", 0)
    if liquidity < 10000:
        risk_score += 0.3
    elif liquidity < 50000:
        risk_score += 0.15
    
    # Volume risk
    volume = token.get("volume_24h", 0)
    if volume < 10000:
        risk_score += 0.2
    
    # Holder concentration risk
    holders = token.get("holders", 0)
    if holders < 100:
        risk_score += 0.2
    elif holders < 500:
        risk_score += 0.1
    
    # Price volatility
    price_change = abs(token.get("price_change_24h", 0))
    if price_change > 50:
        risk_score += 0.15
    
    return min(risk_score, 1.0)

def generate_signal_summary(signals: List[TradingSignal], market_overview: dict) -> str:
    """Generate AI summary of signals"""
    if not signals:
        return "No strong signals detected in current market conditions. Market appears neutral."
    
    buy_signals = sum(1 for s in signals if s.signal_type.value == "buy")
    sell_signals = sum(1 for s in signals if s.signal_type.value == "sell")
    
    sentiment = market_overview.get("market_sentiment", "neutral")
    
    summary = f"Market Sentiment: {sentiment.upper()}. "
    summary += f"Generated {len(signals)} signals: {buy_signals} BUY, {sell_signals} SELL. "
    
    if buy_signals > sell_signals:
        summary += "Bullish opportunities detected with strong volume and momentum. "
    elif sell_signals > buy_signals:
        summary += "Bearish pressure observed. Consider taking profits or reducing exposure. "
    else:
        summary += "Mixed signals suggest cautious approach. "
    
    top_signal = signals[0]
    summary += f"Top signal: {top_signal.signal_type.value.upper()} {top_signal.token_symbol} "
    summary += f"(Confidence: {top_signal.confidence:.0%}, Strength: {top_signal.signal_strength.value})"
    
    return summary
