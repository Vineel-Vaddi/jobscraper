from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session as DBSession
from datetime import datetime, timedelta, timezone
import uuid
from urllib.parse import urlencode
import httpx
from pydantic import BaseModel
import typing

from src.database.database import get_db
from src.database.models import User, Session
from src.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Constants
SESSION_COOKIE_NAME = "jobtailor_session"
SESSION_EXPIRATION_DAYS = 7


class UserResponse(BaseModel):
    id: int
    display_name: typing.Optional[str]
    email: typing.Optional[str]
    
    class Config:
        from_attributes = True


def get_current_user(request: Request, db: DBSession = Depends(get_db)) -> User:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        
    session_record = db.query(Session).filter(Session.id == session_id).first()
    if not session_record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
        
    # Check expiry
    if session_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
        
    return session_record.user


@router.get("/login/linkedin")
async def login_linkedin():
    """Initiates LinkedIn OAuth login."""
    if settings.MOCK_LINKEDIN:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/api/auth/callback/linkedin?code=mock_code_123")
        
    params = {
        "response_type": "code",
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "state": str(uuid.uuid4()), # Would normally store and verify
        "scope": "openid profile email"
    }
    url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    return RedirectResponse(url=url)


@router.get("/callback/linkedin")
async def callback_linkedin(code: str, request: Request, db: DBSession = Depends(get_db)):
    """Handles OAuth callback and creates an app session."""
    
    user_info = {}
    
    if settings.MOCK_LINKEDIN and code == "mock_code_123":
        user_info = {
            "sub": "mock_linkedin_user_123",
            "email": "mockuser@example.com",
            "name": "Mock LinkedIn User"
        }
    else:
        # Exchange code for token
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post("https://www.linkedin.com/oauth/v2/accessToken", data=data)
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail="OAuth failure")
            
            token_data = resp.json()
            access_token = token_data.get("access_token")
            
            # Get User Info
            user_resp = await client.get(
                "https://api.linkedin.com/v2/userinfo", 
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if user_resp.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch user info")
            user_info = user_resp.json()
            
    # Upsert User
    linkedin_sub = user_info.get("sub")
    email = user_info.get("email")
    name = user_info.get("name")
    
    user = db.query(User).filter(User.linkedin_sub == linkedin_sub).first()
    if not user:
        user = User(
            linkedin_sub=linkedin_sub,
            email=email,
            display_name=name
        )
        db.add(user)
        db.flush()
    else:
        user.email = email
        user.display_name = name
    
    # Create Session
    session_id = str(uuid.uuid4())
    session_record = Session(
        id=session_id,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRATION_DAYS)
    )
    db.add(session_record)
    db.commit()
    
    # Set Cookie and Redirect to frontend dashboard
    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard")
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        max_age=SESSION_EXPIRATION_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=False # Set True in prod
    )
    return response


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Returns the current authenticated user."""
    return user


@router.post("/logout")
async def logout(request: Request, db: DBSession = Depends(get_db)):
    """Logs out user by destroying DB session and browser cookie."""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id:
        session_record = db.query(Session).filter(Session.id == session_id).first()
        if session_record:
            db.delete(session_record)
            db.commit()
            
    response = Response(status_code=status.HTTP_200_OK)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response
