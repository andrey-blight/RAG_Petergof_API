from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import settings
from app.core.security import create_access_token
from app.db.schemas import Token, UserCreate
from app.db.session import get_db
from app.db.models.user import get_user, create_user

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


# TODO add response model token
@router.post("/register/")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user(db, user.email)
    print(existing_user)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")

    new_user = await create_user(db, user)
    return new_user
