"""
Signal Service for generating trading signals using GMGN.AI and OpenAI
"""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from openai import AsyncOpenAI

from services.gmgn_service import GMGNService
from models.schemas import (
    SignalType, SignalStrength, RiskLevel, TradingSignal
)
from config import settings

class SignalService:
    """Service for generating and managing trading signals"""
    
    def __init__(self):
        self.gmgn_service = GMGNService()
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    async def generate_signals(
        self,
        token_address: Optional[str] = None,
        wallet_address: Optional[str] = None,
        signal_types: List[SignalType] = None,
        min_strength: SignalStrength = SignalStrength.MODERATE
    ) -> List[TradingSignal]:
        """
        Generate trading signals based on market data and AI analysis
        
        Args:
            token_address: Specific token to analyze (optional)
            wallet_address: User wallet for personalized signals (optional)
            signal_types: Types of signals to generate
            min_strength: Minimum signal strength threshold
        """
        signals = []
        
        if token_address:
            # Generate signal for specific token
            signal = await self._analyze_token_for_signal(token_address, signal_types)
            if signal and self._meets_strength_threshold(signal.signal_strength, min_strength):
                signals.append(signal)
        else:
            # Generate signals from trending tokens
            trending_tokens = await self.gmgn_service.get_trending_tokens(
                time_period="24h",
                order_by="volume",
                limit=20
            )
            
            for token_data in trending_tokens[:10]:  # Analyze top 10
                signal = await self._analyze_token_for_signal(
                    token_data["token_address"],
                    signal_types,
                    token_data
                )
                if signal and self._meets_strength_threshold(signal.signal_strength, min_strength):
                    signals.append(signal)
        
        # Sort by confidence and strength
        signals.sort(key=lambda x: (x.confidence, x.signal_strength.value), reverse=True)
        
        return signals[:10]  # Return top 10 signals
    
    async def _analyze_token_for_signal(
        self,
        token_address: str,
        signal_types: Optional[List[SignalType]] = None,
        cached_data: Optional[Dict] = None
    ) -> Optional[TradingSignal]:
        """Analyze a token and generate trading signal"""
        try:
            # Get token data
            if cached_data:
                token_data = cached_data
            else:
                token_data = await self.gmgn_service.get_token_details(token_address)
                if not token_data:
                    return None
            
            # Get additional context
            trades = await self.gmgn_service.get_token_trades(token_address, limit=50)
            holders = await self.gmgn_service.get_token_holders(token_address)
            
            # Prepare analysis context
            analysis_context = {
                "token_data": token_data,
                "recent_trades": trades[:10],  # Last 10 trades
                "holder_distribution": holders,
                "price": token_data.get("price", 0),
                "volume_24h": token_data.get("volume_24h", 0),
                "liquidity": token_data.get("liquidity", 0),
                "price_change_24h": token_data.get("price_change_24h", 0),
            }
            
            # Generate AI analysis
            ai_analysis = await self._generate_ai_signal_analysis(analysis_context)
            
            # Create trading signal
            signal = self._create_signal_from_analysis(
                token_data,
                ai_analysis,
                signal_types
            )
            
            return signal
            
        except Exception as e:
            print(f"Error analyzing token {token_address}: {e}")
            return None
    
    async def _generate_ai_signal_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered signal analysis using OpenAI"""
        if not self.openai_client:
            return self._generate_fallback_analysis(context)
        
        try:
            prompt = f"""
            Analyze this Solana token and generate a trading signal:
            
            Token Data:
            - Price: ${context['price']}
            - 24h Volume: ${context['volume_24h']:,.2f}
            - Liquidity: ${context['liquidity']:,.2f}
            - 24h Price Change: {context['price_change_24h']:.2f}%
            
            Recent Trading Activity: {len(context.get('recent_trades', []))} trades
            Holder Distribution: {json.dumps(context.get('holder_distribution', {}), indent=2)}
            
            Provide a JSON response with:
            {{
                "signal_type": "buy|sell|hold|alert",
                "signal_strength": "weak|moderate|strong|very_strong",
                "confidence": 0.0-1.0,
                "reasoning": "Brief explanation",
                "key_factors": ["factor1", "factor2", "factor3"],
                "risk_level": "low|medium|high|critical",
                "target_price": price or null,
                "stop_loss": price or null
            }}
            
            Consider: liquidity depth, volume trends, holder concentration, price momentum, and risk factors.
            """
            
            response = await self.openai_client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Solana token analyst providing trading signals."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            print(f"Error generating AI analysis: {e}")
            return self._generate_fallback_analysis(context)
    
    def _generate_fallback_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rule-based analysis when AI is unavailable"""
        price_change = context.get("price_change_24h", 0)
        volume = context.get("volume_24h", 0)
        liquidity = context.get("liquidity", 0)
        
        # Simple rule-based signal generation
        if price_change > 20 and volume > 100000 and liquidity > 50000:
            signal_type = "buy"
            strength = "strong"
            confidence = 0.75
            risk = "medium"
        elif price_change < -20 and volume > 100000:
            signal_type = "sell"
            strength = "strong"
            confidence = 0.70
            risk = "high"
        elif liquidity < 10000 or volume < 10000:
            signal_type = "alert"
            strength = "moderate"
            confidence = 0.60
            risk = "critical"
        else:
            signal_type = "hold"
            strength = "moderate"
            confidence = 0.65
            risk = "medium"
        
        return {
            "signal_type": signal_type,
            "signal_strength": strength,
            "confidence": confidence,
            "reasoning": f"Based on {price_change:.1f}% price change, ${volume:,.0f} volume, and ${liquidity:,.0f} liquidity",
            "key_factors": [
                f"Price momentum: {price_change:.1f}%",
                f"Trading volume: ${volume:,.0f}",
                f"Liquidity: ${liquidity:,.0f}"
            ],
            "risk_level": risk,
            "target_price": None,
            "stop_loss": None
        }
    
    def _create_signal_from_analysis(
        self,
        token_data: Dict,
        ai_analysis: Dict,
        signal_types: Optional[List[SignalType]] = None
    ) -> TradingSignal:
        """Create TradingSignal object from analysis"""
        signal_type = SignalType(ai_analysis.get("signal_type", "hold"))
        
        # Filter by requested signal types
        if signal_types and signal_type not in signal_types:
            return None
        
        return TradingSignal(
            signal_id=str(uuid.uuid4()),
            token_address=token_data.get("token_address", token_data.get("address", "")),
            token_name=token_data.get("token_name", token_data.get("name", "Unknown")),
            token_symbol=token_data.get("token_symbol", token_data.get("symbol", "???")),
            signal_type=signal_type,
            signal_strength=SignalStrength(ai_analysis.get("signal_strength", "moderate")),
            confidence=float(ai_analysis.get("confidence", 0.5)),
            price=float(token_data.get("price", 0)),
            target_price=ai_analysis.get("target_price"),
            stop_loss=ai_analysis.get("stop_loss"),
            reasoning=ai_analysis.get("reasoning", ""),
            key_factors=ai_analysis.get("key_factors", []),
            risk_level=RiskLevel(ai_analysis.get("risk_level", "medium")),
            timestamp=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
    
    def _meets_strength_threshold(
        self,
        signal_strength: SignalStrength,
        min_strength: SignalStrength
    ) -> bool:
        """Check if signal meets minimum strength threshold"""
        strength_order = {
            SignalStrength.WEAK: 1,
            SignalStrength.MODERATE: 2,
            SignalStrength.STRONG: 3,
            SignalStrength.VERY_STRONG: 4
        }
        
        return strength_order[signal_strength] >= strength_order[min_strength]
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get overall market overview"""
        trending = await self.gmgn_service.get_trending_tokens(limit=50)
        
        if not trending:
            return {
                "total_tokens": 0,
                "avg_volume": 0,
                "trending_up": 0,
                "trending_down": 0,
                "market_sentiment": "neutral"
            }
        
        total_volume = sum(t.get("volume_24h", 0) for t in trending)
        trending_up = sum(1 for t in trending if t.get("price_change_24h", 0) > 0)
        trending_down = len(trending) - trending_up
        
        sentiment = "bullish" if trending_up > trending_down * 1.5 else "bearish" if trending_down > trending_up * 1.5 else "neutral"
        
        return {
            "total_tokens": len(trending),
            "avg_volume": total_volume / len(trending) if trending else 0,
            "trending_up": trending_up,
            "trending_down": trending_down,
            "market_sentiment": sentiment,
            "top_gainers": sorted(trending, key=lambda x: x.get("price_change_24h", 0), reverse=True)[:5],
            "top_volume": sorted(trending, key=lambda x: x.get("volume_24h", 0), reverse=True)[:5]
        }
