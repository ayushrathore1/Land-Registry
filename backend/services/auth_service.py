"""
Authentication Service - JWT-based authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
import hashlib

# Security configuration
SECRET_KEY = "land-records-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours


def hash_password(password: str) -> str:
    """Simple password hashing using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


# Sample users database (in production, use a real database with proper hashing)
USERS_DB = {
    "viewer1": {
        "username": "viewer1",
        "hashed_password": hash_password("viewer123"),
        "role": "viewer",
        "full_name": "View Only User",
        "disabled": False
    },
    "editor1": {
        "username": "editor1",
        "hashed_password": hash_password("editor123"),
        "role": "editor",
        "full_name": "Record Editor",
        "disabled": False
    },
    "admin1": {
        "username": "admin1",
        "hashed_password": hash_password("admin123"),
        "role": "admin",
        "full_name": "System Administrator",
        "disabled": False
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return hash_password(password)


def get_user(username: str) -> Optional[Dict]:
    """Get user from database"""
    if username in USERS_DB:
        return USERS_DB[username]
    return None


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate user with username and password"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            return None
        
        user = get_user(username)
        if user is None:
            return None
        
        return {
            "username": username,
            "role": user["role"],
            "full_name": user["full_name"]
        }
    except JWTError:
        return None


def check_permission(user_role: str, required_role: str) -> bool:
    """Check if user role has required permission"""
    role_hierarchy = {
        "viewer": 1,
        "editor": 2,
        "admin": 3
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level
