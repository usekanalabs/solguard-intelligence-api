"""
Authentication middleware for protected routes
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict

from services.auth_service import AuthService

security = HTTPBearer()
auth_service = AuthService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Dependency to get current authenticated user
    Use this to protect routes that require authentication
    """
    token = credentials.credentials
    
    payload = await auth_service.verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[Dict]:
    """
    Optional authentication - returns user if authenticated, None otherwise
    Use for routes that work with or without authentication
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = await auth_service.verify_token(token)
    
    return payload
