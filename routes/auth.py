"""
Authentication routes for Solana wallet-based authentication
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional

from models.schemas import (
    WalletAuthRequest,
    WalletAuthResponse,
    WalletVerifyRequest,
    TokenResponse,
    UserProfile
)
from services.auth_service import AuthService
from middleware.auth_middleware import get_current_user

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()

@router.post("/challenge", response_model=WalletAuthResponse)
async def request_challenge(wallet_address: str):
    """
    Request authentication challenge for wallet
    
    Step 1: Client requests a challenge message to sign
    """
    try:
        challenge = await auth_service.generate_challenge(wallet_address)
        return WalletAuthResponse(
            challenge=challenge["message"],
            expires_at=challenge["expires_at"],
            wallet_address=wallet_address
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate challenge: {str(e)}"
        )

@router.post("/verify", response_model=TokenResponse)
async def verify_signature(request: WalletVerifyRequest):
    """
    Verify wallet signature and issue JWT token
    
    Step 2: Client submits signed message for verification
    """
    try:
        # Verify the signature
        is_valid = await auth_service.verify_signature(
            wallet_address=request.wallet_address,
            signature=request.signature,
            message=request.message
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        # Generate JWT token
        token_data = await auth_service.create_access_token(
            wallet_address=request.wallet_address
        )
        
        return TokenResponse(
            access_token=token_data["access_token"],
            token_type="bearer",
            expires_in=token_data["expires_in"],
            wallet_address=request.wallet_address
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Refresh JWT token
    """
    try:
        token = credentials.credentials
        new_token_data = await auth_service.refresh_access_token(token)
        
        return TokenResponse(
            access_token=new_token_data["access_token"],
            token_type="bearer",
            expires_in=new_token_data["expires_in"],
            wallet_address=new_token_data["wallet_address"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get authenticated user profile
    
    Protected route - requires valid JWT token
    """
    try:
        profile = await auth_service.get_user_profile(
            current_user["wallet_address"]
        )
        return profile
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile: {str(e)}"
        )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user (invalidate token)
    """
    try:
        await auth_service.revoke_token(current_user["wallet_address"])
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )
