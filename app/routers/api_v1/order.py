import json
from typing import Any, Optional
from datetime import timedelta, datetime

import requests
from fastapi import APIRouter, Depends, HTTPException, Response
#from loguru import logger
from sqlalchemy.orm import Session,joinedload

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.routers import deps
import traceback


router = APIRouter()


@router.post("/my-rent-list/", response_model=schemas.OrderRentResponse)
def get_rent_list(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    rent_list = crud.order.get_user_order_history(db=db, user_id=current_user.id)

    
    return {"orders": rent_list}