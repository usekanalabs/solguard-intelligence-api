# Trading Signals Documentation

## Overview

The Kana Trading Signals feature provides AI-powered trading signals for Solana tokens using real-time data from GMGN.AI and intelligent analysis from OpenAI.

## Features

- **Real-time Market Data**: Live token data from GMGN.AI
- **AI-Powered Analysis**: OpenAI-driven signal generation
- **Multiple Signal Types**: BUY, SELL, HOLD, and ALERT signals
- **Risk Assessment**: Comprehensive risk scoring for each signal
- **Personalized Signals**: Tailored recommendations based on user portfolio
- **Market Overview**: Holistic market sentiment analysis

## API Endpoints

### 1. Get Trending Tokens

\`\`\`http
GET /api/v1/signals/trending
\`\`\`

**Query Parameters:**
- `time_period` (optional): Time period (5m, 1h, 6h, 24h) - default: 24h
- `limit` (optional): Number of tokens (1-100) - default: 20
- `order_by` (optional): Sort by (volume, swaps, price_change) - default: volume

**Response:**
\`\`\`json
[
  {
    "token_address": "TokenAddress...",
    "token_name": "Example Token",
    "token_symbol": "EXT",
    "price": 0.0123,
    "price_change_24h": 45.67,
    "volume_24h": 1234567.89,
    "liquidity": 500000.00,
    "market_cap": 10000000.00,
    "swaps_24h": 1234,
    "holders": 5678,
    "risk_score": 0.35,
    "timestamp": "2024-01-15T12:00:00Z"
  }
]
\`\`\`

### 2. Generate Trading Signals

\`\`\`http
POST /api/v1/signals/generate
Authorization: Bearer <token>
\`\`\`

**Request Body:**
\`\`\`json
{
  "token_address": "TokenAddress..." (optional),
  "wallet_address": "WalletAddress..." (optional),
  "signal_types": ["buy", "sell"],
  "min_strength": "moderate"
}
\`\`\`

**Response:**
\`\`\`json
{
  "signals": [
    {
      "signal_id": "uuid",
      "token_address": "TokenAddress...",
      "token_name": "Example Token",
      "token_symbol": "EXT",
      "signal_type": "buy",
      "signal_strength": "strong",
      "confidence": 0.85,
      "price": 0.0123,
      "target_price": 0.0180,
      "stop_loss": 0.0100,
      "reasoning": "Strong upward momentum with increasing volume...",
      "key_factors": [
        "24h volume increased 150%",
        "Liquidity above $500k",
        "Holder count growing steadily"
      ],
      "risk_level": "medium",
      "timestamp": "2024-01-15T12:00:00Z",
      "expires_at": "2024-01-16T12:00:00Z"
    }
  ],
  "market_overview": {
    "total_tokens": 50,
    "avg_volume": 234567.89,
    "trending_up": 32,
    "trending_down": 18,
    "market_sentiment": "bullish"
  },
  "ai_summary": "Market Sentiment: BULLISH. Generated 5 signals...",
  "timestamp": "2024-01-15T12:00:00Z"
}
\`\`\`

### 3. Get Token Signal

\`\`\`http
GET /api/v1/signals/token/{token_address}
Authorization: Bearer <token>
\`\`\`

**Response:** Single `TradingSignal` object

### 4. Subscribe to Signals

\`\`\`http
POST /api/v1/signals/subscribe
Authorization: Bearer <token>
\`\`\`

**Request Body:**
\`\`\`json
{
  "wallet_address": "WalletAddress...",
  "signal_types": ["buy", "sell", "alert"],
  "min_strength": "moderate",
  "tokens": ["Token1...", "Token2..."] (optional)
}
\`\`\`

## Signal Types

- **BUY**: Bullish signal indicating potential entry point
- **SELL**: Bearish signal suggesting exit or short opportunity
- **HOLD**: Neutral signal, maintain current position
- **ALERT**: Warning signal for unusual activity or high risk

## Signal Strength

- **WEAK**: Low confidence, informational only
- **MODERATE**: Medium confidence, consider with other factors
- **STRONG**: High confidence, actionable signal
- **VERY_STRONG**: Very high confidence, strong conviction

## Risk Levels

- **LOW**: Minimal risk, established token
- **MEDIUM**: Moderate risk, standard due diligence required
- **HIGH**: Elevated risk, proceed with caution
- **CRITICAL**: Extreme risk, likely scam or rug pull

## Integration Example

### Python Client

\`\`\`python
import httpx
import asyncio

async def get_trading_signals():
    async with httpx.AsyncClient() as client:
        # Authenticate
        auth_response = await client.post(
            "http://localhost:8000/api/v1/auth/wallet/verify",
            json={
                "wallet_address": "your_wallet",
                "signature": "signature",
                "message": "challenge"
            }
        )
        token = auth_response.json()["access_token"]
        
        # Get signals
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.post(
            "http://localhost:8000/api/v1/signals/generate",
            headers=headers,
            json={
                "signal_types": ["buy", "sell"],
                "min_strength": "strong"
            }
        )
        
        signals = response.json()
        print(f"Generated {len(signals['signals'])} signals")
        
        for signal in signals['signals']:
            print(f"\n{signal['signal_type'].upper()}: {signal['token_symbol']}")
            print(f"Confidence: {signal['confidence']:.0%}")
            print(f"Reasoning: {signal['reasoning']}")

asyncio.run(get_trading_signals())
\`\`\`

### JavaScript/TypeScript

\`\`\`typescript
async function getTradingSignals() {
  // Authenticate first
  const authResponse = await fetch('http://localhost:8000/api/v1/auth/wallet/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      wallet_address: 'your_wallet',
      signature: 'signature',
      message: 'challenge'
    })
  });
  
  const { access_token } = await authResponse.json();
  
  // Get signals
  const response = await fetch('http://localhost:8000/api/v1/signals/generate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${access_token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      signal_types: ['buy', 'sell'],
      min_strength: 'strong'
    })
  });
  
  const data = await response.json();
  console.log(`Generated ${data.signals.length} signals`);
  
  data.signals.forEach(signal => {
    console.log(`\n${signal.signal_type.toUpperCase()}: ${signal.token_symbol}`);
    console.log(`Confidence: ${(signal.confidence * 100).toFixed(0)}%`);
    console.log(`Reasoning: ${signal.reasoning}`);
  });
}
\`\`\`

## Configuration

Add these environment variables to your `.env` file:

\`\`\`bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...

# GMGN.AI Configuration (uses public API, no key required)
GMGN_API_BASE_URL=https://gmgn.ai
GMGN_WS_URL=wss://gmgn.ai/ws
\`\`\`

## Best Practices

1. **Always authenticate** before accessing signal endpoints
2. **Set appropriate strength thresholds** to filter noise
3. **Combine signals with your own research** - never trade on signals alone
4. **Monitor signal expiration** - signals expire after 24 hours
5. **Use stop-loss recommendations** to manage risk
6. **Start with small positions** when acting on signals
7. **Track signal performance** to understand accuracy over time

## Limitations

- Signals are based on available market data and AI analysis
- Past performance does not guarantee future results
- Always conduct your own research before trading
- Market conditions can change rapidly
- Not financial advice - use at your own risk
