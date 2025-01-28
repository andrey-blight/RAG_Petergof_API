from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Header, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core import settings
from app.core.security import create_access_token
from app.db.schemas import Token

router = APIRouter()


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    if form_data.password != settings.API_PASSWORD and form_data.username != settings.API_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(data={"sub": form_data.password},
                                       expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
