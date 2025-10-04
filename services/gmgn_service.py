"""
GMGN.AI Service for Solana token data and analytics
"""
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import settings

class GMGNService:
    """Service for interacting with GMGN.AI API"""
    
    def __init__(self):
        self.base_url = settings.GMGN_API_BASE_URL
        self.ws_url = settings.GMGN_WS_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_trending_tokens(
        self, 
        time_period: str = "24h",
        order_by: str = "volume",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get trending tokens from GMGN.AI
        
        Args:
            time_period: Time period (5m, 1h, 6h, 24h)
            order_by: Sort criteria (volume, swaps, price_change)
            limit: Number of tokens to return
        """
        try:
            url = f"{self.base_url}/defi/quotation/v1/rank/sol/swaps/{time_period}"
            params = {
                "orderby": order_by,
                "direction": "desc",
                "limit": limit
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_trending_tokens(data)
            
        except Exception as e:
            print(f"Error fetching trending tokens: {e}")
            return []
    
    async def get_token_details(self, token_address: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific token
        
        Args:
            token_address: Solana token address
        """
        try:
            url = f"{self.base_url}/defi/quotation/v1/tokens/sol/{token_address}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching token details: {e}")
            return {}
    
    async def get_token_trades(
        self, 
        token_address: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent trades for a token
        
        Args:
            token_address: Solana token address
            limit: Number of trades to return
        """
        try:
            url = f"{self.base_url}/defi/quotation/v1/trades/sol/{token_address}"
            params = {"limit": limit}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            return response.json().get("data", [])
            
        except Exception as e:
            print(f"Error fetching token trades: {e}")
            return []
    
    async def get_token_holders(self, token_address: str) -> Dict[str, Any]:
        """
        Get holder distribution for a token
        
        Args:
            token_address: Solana token address
        """
        try:
            url = f"{self.base_url}/defi/quotation/v1/tokens/sol/{token_address}/holders"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching token holders: {e}")
            return {}
    
    def _parse_trending_tokens(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse trending tokens response"""
        tokens = []
        
        # Handle different response formats from GMGN API
        token_list = data.get("data", {}).get("rank", []) if isinstance(data.get("data"), dict) else data.get("data", [])
        
        for item in token_list:
            try:
                tokens.append({
                    "token_address": item.get("address", ""),
                    "token_name": item.get("name", "Unknown"),
                    "token_symbol": item.get("symbol", "???"),
                    "price": float(item.get("price", 0)),
                    "price_change_24h": float(item.get("price_change_24h", 0)),
                    "volume_24h": float(item.get("volume_24h", 0)),
                    "liquidity": float(item.get("liquidity", 0)),
                    "market_cap": float(item.get("market_cap", 0)) if item.get("market_cap") else None,
                    "swaps_24h": int(item.get("swaps_24h", 0)),
                    "holders": int(item.get("holder_count", 0)),
                    "created_at": item.get("created_timestamp"),
                })
            except (ValueError, TypeError) as e:
                print(f"Error parsing token data: {e}")
                continue
        
        return tokens
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
