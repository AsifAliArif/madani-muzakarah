import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.security import COOKIE_NAME, create_access_token, get_current_user
from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/auth", tags=["auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


@router.get("/login")
async def login(request: Request):
    state = secrets.token_urlsafe(32)
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    response = RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")
    response.set_cookie("oauth_state", state, httponly=True, max_age=600, samesite="lax")
    return response


@router.get("/callback")
async def callback(code: str, state: str, request: Request, db: Session = Depends(get_db)):
    stored_state = request.cookies.get("oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Google token exchange failed")
        access_token = token_resp.json().get("access_token")

        user_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        info = user_resp.json()

    google_id = info["id"]
    email = info["email"]
    name = info.get("name", "")
    avatar = info.get("picture")

    user = db.query(User).filter(User.google_id == google_id).first()
    if not user:
        user = db.query(User).filter(User.email == email).first()

    role = UserRole.admin if email.lower() == settings.admin_email.lower() else UserRole.user

    if user:
        if user.is_removed:
            raise HTTPException(status_code=403, detail="آپ کا اکاؤنٹ ہٹا دیا گیا ہے")
        user.google_id = google_id
        user.name = name
        user.avatar_url = avatar
        if email.lower() == settings.admin_email.lower():
            user.role = UserRole.admin
    else:
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            avatar_url=avatar,
            role=role,
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    jwt_token = create_access_token(str(user.id))
    response = RedirectResponse(settings.frontend_url)
    response.set_cookie(
        COOKIE_NAME,
        jwt_token,
        httponly=True,
        max_age=60 * 60 * 24 * 7,
        samesite="lax",
        secure=settings.frontend_url.startswith("https"),
    )
    response.delete_cookie("oauth_state")
    return response


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    from app.schemas import UserOut
    return UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        avatar_url=user.avatar_url,
        role=user.role.value,
    )


@router.post("/logout")
def logout():
    response = RedirectResponse(settings.frontend_url)
    response.delete_cookie(COOKIE_NAME)
    return response
