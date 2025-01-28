from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError

from app.core import settings
from app.core.security import oauth2_scheme


async def check_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        password: str = payload.get("sub")

        if password != settings.API_PASSWORD:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    return True
