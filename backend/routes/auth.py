"""
Authentication Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta
from typing import Dict, Any

from services.auth_service import (
    authenticate_user, 
    create_access_token, 
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.post("/login")
async def login(credentials: Dict[str, Any] = Body(...)):
    """
    Authenticate user and return JWT token
    """
    user = authenticate_user(credentials.get("username", ""), credentials.get("password", ""))
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    if user.get("disabled"):
        raise HTTPException(
            status_code=403,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "username": user["username"],
            "role": user["role"],
            "full_name": user["full_name"]
        }
    }


@router.get("/verify")
async def verify(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify if the current token is valid
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = verify_token(credentials.credentials)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {
        "valid": True,
        "user": user
    }


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client should discard token)
    """
    return {"message": "Successfully logged out"}


# Dependency for protected routes
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated user
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = verify_token(credentials.credentials)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user


async def require_editor(user: dict = Depends(get_current_user)):
    """
    Dependency to require editor or admin role
    """
    if user["role"] not in ["editor", "admin"]:
        raise HTTPException(status_code=403, detail="Editor access required")
    return user


async def require_admin(user: dict = Depends(get_current_user)):
    """
    Dependency to require admin role
    """
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
