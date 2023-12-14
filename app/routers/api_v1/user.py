from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import exc
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.routers import deps

router = APIRouter()

@router.get("/get-all-users", response_model=schemas.user.AllUsersResponse)
def get_all_user_except_provider_and_current_user(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    all_user_except_provider_and_current_user = crud.user.get_all_user_except_provider_and_current_user(db=db,current_user=current_user )
    user_list_items = [
        schemas.user.UserListItem(id=user.id, email=user.email)
        for user in all_user_except_provider_and_current_user
    ]
    return {"message": "success", "data": user_list_items}