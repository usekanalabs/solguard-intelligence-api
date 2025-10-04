"""
Example usage of Kana Trading Signals API
"""
import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

async def main():
    async with httpx.AsyncClient() as client:
        print("🔍 Kana Trading Signals Example\n")
        
        # 1. Get trending tokens (no auth required)
        print("1. Fetching trending tokens...")
        response = await client.get(
            f"{BASE_URL}/signals/trending",
            params={
                "time_period": "24h",
                "limit": 10,
                "order_by": "volume"
            }
        )
        
        if response.status_code == 200:
            trending = response.json()
            print(f"✅ Found {len(trending)} trending tokens\n")
            
            for i, token in enumerate(trending[:5], 1):
                print(f"{i}. {token['token_symbol']} - {token['token_name']}")
                print(f"   Price: ${token['price']:.6f}")
                print(f"   24h Change: {token['price_change_24h']:.2f}%")
                print(f"   Volume: ${token['volume_24h']:,.2f}")
                print(f"   Risk Score: {token['risk_score']:.2f}\n")
        
        # 2. Authenticate (replace with your actual wallet and signature)
        print("\n2. Authenticating...")
        # In production, you would:
        # - Get challenge from /auth/wallet/challenge
        # - Sign the challenge with your wallet
        # - Verify with /auth/wallet/verify
        
        # For demo purposes, using mock token
        token = "demo_token"
        print("⚠️  Using demo token (implement proper auth in production)\n")
        
        # 3. Generate trading signals
        print("3. Generating trading signals...")
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = await client.post(
                f"{BASE_URL}/signals/generate",
                headers=headers,
                json={
                    "signal_types": ["buy", "sell"],
                    "min_strength": "moderate"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                signals = data['signals']
                market = data['market_overview']
                
                print(f"✅ Generated {len(signals)} signals")
                print(f"\n📊 Market Overview:")
                print(f"   Sentiment: {market['market_sentiment'].upper()}")
                print(f"   Trending Up: {market['trending_up']}")
                print(f"   Trending Down: {market['trending_down']}")
                print(f"\n💡 AI Summary:")
                print(f"   {data['ai_summary']}")
                
                print(f"\n🎯 Top Signals:")
                for i, signal in enumerate(signals[:3], 1):
                    print(f"\n{i}. {signal['signal_type'].upper()}: {signal['token_symbol']}")
                    print(f"   Strength: {signal['signal_strength'].upper()}")
                    print(f"   Confidence: {signal['confidence']:.0%}")
                    print(f"   Price: ${signal['price']:.6f}")
                    if signal.get('target_price'):
                        print(f"   Target: ${signal['target_price']:.6f}")
                    if signal.get('stop_loss'):
                        print(f"   Stop Loss: ${signal['stop_loss']:.6f}")
                    print(f"   Risk: {signal['risk_level'].upper()}")
                    print(f"   Reasoning: {signal['reasoning']}")
                    print(f"   Key Factors:")
                    for factor in signal['key_factors']:
                        print(f"      • {factor}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Note: Signals endpoint requires authentication")
                
        except Exception as e:
            print(f"❌ Error generating signals: {e}")
            print(f"   Make sure to implement proper authentication")
        
        # 4. Get signal for specific token
        print("\n\n4. Getting signal for specific token...")
        if trending:
            token_address = trending[0]['token_address']
            print(f"   Analyzing: {trending[0]['token_symbol']}")
            
            try:
                response = await client.get(
                    f"{BASE_URL}/signals/token/{token_address}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    signal = response.json()
                    print(f"✅ Signal: {signal['signal_type'].upper()}")
                    print(f"   Confidence: {signal['confidence']:.0%}")
                else:
                    print(f"❌ Error: {response.status_code}")
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
