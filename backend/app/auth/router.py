import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.security import COOKIE_NAME, create_access_token, get_current_user
from app.config import settings
from app.database import get_db
from app.debug_log import dbg
from app.models.user import User, UserRole

router = APIRouter(prefix="/api/auth", tags=["auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

_USE_SECURE_COOKIES = settings.frontend_url.startswith("https://")
_COOKIE_KWARGS = {"httponly": True, "samesite": "lax", "path": "/"}
if _USE_SECURE_COOKIES:
    _COOKIE_KWARGS["secure"] = True


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
    # #region agent log
    dbg("H3", "router.py:login", "login_start", {
        "redirect_uri": settings.google_redirect_uri,
        "secure_cookies": _USE_SECURE_COOKIES,
        "has_client_id": bool(settings.google_client_id),
    })
    # #endregion
    response = RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")
    response.set_cookie("oauth_state", state, max_age=600, **_COOKIE_KWARGS)
    return response


@router.get("/callback")
async def callback(code: str, state: str, request: Request, db: Session = Depends(get_db)):
    stored_state = request.cookies.get("oauth_state")
    # #region agent log
    dbg("H4", "router.py:callback", "callback_start", {
        "has_code": bool(code),
        "state_match": bool(stored_state and stored_state == state),
        "has_oauth_state_cookie": bool(stored_state),
    })
    # #endregion
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
            # #region agent log
            dbg("H4", "router.py:callback", "token_exchange_failed", {
                "status": token_resp.status_code,
            })
            # #endregion
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
    response.set_cookie(COOKIE_NAME, jwt_token, max_age=60 * 60 * 24 * 7, **_COOKIE_KWARGS)
    response.delete_cookie("oauth_state", path="/", secure=_USE_SECURE_COOKIES)
    # #region agent log
    dbg("H5", "router.py:callback", "login_success", {
        "user_id_prefix": str(user.id)[:8],
        "role": user.role.value,
    })
    # #endregion
    return response


@router.get("/me")
def me(request: Request, user: User = Depends(get_current_user)):
    # #region agent log
    dbg("H5", "router.py:me", "me_ok", {
        "has_token_cookie": bool(request.cookies.get(COOKIE_NAME)),
    })
    # #endregion
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
