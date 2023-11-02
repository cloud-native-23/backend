from typing import Generator

import loguru
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.database.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.user:
    try:
        print("in get_current_user")
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        loguru.logger.info(f"payload: {payload}")
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as e:
        loguru.logger.error(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{e}",
        )

    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=204, detail="User not found")

    return user


def get_current_active_user(
    current_user: models.user = Depends(get_current_user),
) -> models.user:
    if not crud.user.is_active(current_user):
        loguru.logger.info("Inactive user")
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


def get_current_active_superuser(
    current_user: models.user = Depends(get_current_active_user),
) -> models.user:
    if not crud.user.is_admin(current_user):
        loguru.logger.info("The user doesn't have enough privileges")
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )

    return current_user


# async def get_login_user(request: Request) -> Optional[dict]:
#     user = request.session.get("user")
#     if user is not None:
#         return user
#     else:
#         raise HTTPException(status_code=401, detail="Could not validate credentials.")
