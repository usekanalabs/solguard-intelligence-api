"""
Authentication service for Solana wallet verification
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
import secrets
import base58
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from jose import JWTError, jwt

from config import settings

class AuthService:
    """Service for handling Solana wallet authentication"""
    
    def __init__(self):
        self.challenges: Dict[str, Dict] = {}  # In production, use Redis
        self.revoked_tokens: set = set()  # In production, use Redis
    
    async def generate_challenge(self, wallet_address: str) -> Dict:
        """
        Generate a challenge message for wallet to sign
        """
        # Create unique challenge message
        nonce = secrets.token_hex(16)
        timestamp = datetime.utcnow().isoformat()
        
        message = (
            f"Sign this message to authenticate with Kana API\n\n"
            f"Wallet: {wallet_address}\n"
            f"Nonce: {nonce}\n"
            f"Timestamp: {timestamp}\n\n"
            f"This request will not trigger a blockchain transaction or cost any gas fees."
        )
        
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        # Store challenge temporarily
        self.challenges[wallet_address] = {
            "message": message,
            "nonce": nonce,
            "expires_at": expires_at
        }
        
        return {
            "message": message,
            "expires_at": expires_at
        }
    
    async def verify_signature(
        self,
        wallet_address: str,
        signature: str,
        message: str
    ) -> bool:
        """
        Verify Solana wallet signature
        """
        try:
            # Check if challenge exists and is valid
            if wallet_address not in self.challenges:
                return False
            
            challenge = self.challenges[wallet_address]
            
            # Check expiration
            if datetime.utcnow() > challenge["expires_at"]:
                del self.challenges[wallet_address]
                return False
            
            # Verify message matches
            if message != challenge["message"]:
                return False
            
            # Decode signature and public key
            signature_bytes = base58.b58decode(signature)
            public_key_bytes = base58.b58decode(wallet_address)
            
            # Verify signature using nacl
            verify_key = VerifyKey(public_key_bytes)
            verify_key.verify(message.encode(), signature_bytes)
            
            # Clean up used challenge
            del self.challenges[wallet_address]
            
            return True
            
        except (BadSignatureError, Exception) as e:
            print(f"Signature verification failed: {e}")
            return False
    
    async def create_access_token(self, wallet_address: str) -> Dict:
        """
        Create JWT access token for authenticated wallet
        """
        expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": wallet_address,
            "wallet_address": wallet_address,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return {
            "access_token": encoded_jwt,
            "expires_in": int(expires_delta.total_seconds()),
            "wallet_address": wallet_address
        }
    
    async def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode JWT token
        """
        try:
            # Check if token is revoked
            if token in self.revoked_tokens:
                return None
            
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            wallet_address: str = payload.get("sub")
            if wallet_address is None:
                return None
            
            return payload
            
        except JWTError:
            return None
    
    async def refresh_access_token(self, token: str) -> Dict:
        """
        Refresh JWT token
        """
        payload = await self.verify_token(token)
        if not payload:
            raise ValueError("Invalid token")
        
        wallet_address = payload.get("wallet_address")
        return await self.create_access_token(wallet_address)
    
    async def revoke_token(self, wallet_address: str):
        """
        Revoke token (logout)
        """
        # In production, store in Redis with expiration
        # For now, just mark as revoked
        pass
    
    async def get_user_profile(self, wallet_address: str) -> Dict:
        """
        Get user profile data
        """
        # In production, fetch from database
        return {
            "wallet_address": wallet_address,
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow(),
            "preferences": {}
        }
