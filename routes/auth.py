"""
Authentication routes for Solana wallet-based authentication and OAuth
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
    UserProfile,
    GoogleAuthRequest,
    GoogleAuthResponse
)
from services.auth_service import AuthService
from middleware.auth_middleware import get_current_user
from config import settings

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

@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth flow
    
    Returns the Google OAuth authorization URL
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured"
        )
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid email profile&"
        f"access_type=offline"
    )
    
    return {
        "auth_url": auth_url,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }

@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(request: GoogleAuthRequest):
    """
    Handle Google OAuth callback
    
    Exchange authorization code for user info and issue JWT token
    """
    try:
        # Verify Google token and get user info
        user_info = await auth_service.verify_google_token(
            code=request.code,
            redirect_uri=request.redirect_uri
        )
        
        if not user_info or not user_info.get("verified_email"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to verify Google account"
            )
        
        email = user_info["email"]
        
        # Create JWT token
        token_data = await auth_service.create_access_token(
            email=email,
            auth_method="google"
        )
        
        return TokenResponse(
            access_token=token_data["access_token"],
            token_type="bearer",
            expires_in=token_data["expires_in"],
            wallet_address=None,
            email=email,
            auth_method="google"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )

@router.post("/link-wallet")
async def link_wallet(
    wallet_address: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Link a Solana wallet to an authenticated Google account
    
    Protected route - requires valid JWT token from Google auth
    """
    try:
        if current_user.get("auth_method") != "google":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This endpoint is for linking wallets to Google accounts"
            )
        
        email = current_user.get("email")
        success = await auth_service.link_wallet_to_email(email, wallet_address)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to link wallet"
            )
        
        return {
            "message": "Wallet linked successfully",
            "email": email,
            "wallet_address": wallet_address
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link wallet: {str(e)}"
        )
