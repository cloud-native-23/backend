from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import exc
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.routers import deps

router = APIRouter()

# TODO
# @router.get("/", response_model=List[schemas.User])
# def read_users(
#     db: Session = Depends(deps.get_db),
#     skip: int = 0,
#     limit: int = 100,
#     current_user: models.User = Depends(deps.get_current_active_superuser),
# ) -> Any:
#     """
#     Retrieve users.
#     """
#     users = crud.user.get_multi(db, skip=skip, limit=limit)
#     return users


@router.post("/", response_model=schemas.user.UserMessage)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    # current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    return {"message": "success", "data": user}


@router.get("/profile/me", response_model=schemas.user.UserMessage)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current logged-in user's profile.
    """

    return {"message": "success", "data": current_user}


# TODO
# @router.post("/profile", response_model=schemas.user.UserMessage)
# def read_user_by_email(
#     *,
#     db: Session = Depends(deps.get_db),
#     user_in: schemas.user.UserGetBase,
#     current_user: models.User = Depends(deps.get_current_active_superuser)
# ) -> Any:
#     """
#     Read active user's profile by email for super user only.
#     """
#     user = crud.user.get_by_email(db, email=user_in.email)
#     if not user:
#         raise HTTPException(
#         status_code=204,
#         detail="Failed to get profile by the email."
#     )

#     return {
#         "message": "success",
#         "data": user
#     }
#     #return user


@router.put("/profile", response_model=schemas.user.UserMessage)
def update_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.user.UserUpdateNoEmail,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current logged-in user's profile.
    """
    try:
        user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    except exc.IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="duplicate line_id",
        )

    return {
        "message": "success",
        # "data": schemas.User(**jsonable_encoder(user)).dict()
        "data": user,
    }


# @router.get("/logout", response_model=schemas.user.UserMessage)
# async def logout(request: Request):
#     user = request.session.get("user")
#     if not user:
#         raise HTTPException(status_code=400, detail="User has not logged in.")
#     # Remove the user
#     request.session.pop("user", None)

#     return {"message": "User log out", "data": ""}
