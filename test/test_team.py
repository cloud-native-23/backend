import random
import string

import loguru
import pytest
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from unittest.mock import patch
from app import crud
from app.core.config import settings
from .contest import db_conn, get_user_authentication_headers, test_client

from app.schemas.stadium import StadiumCreate
from app.schemas.stadium_disable import StadiumDisableCreate

# pytest fixture
db_conn = db_conn
test_client = test_client

def test_get_join_list(db_conn, test_client):
    email = "test1@gmail.com"
    # correct
    response = test_client.post(
        f"{settings.API_V1_STR}/team/my-join-list/",
        headers=get_user_authentication_headers(db_conn, email)
    )
    assert response.status_code == 200
    assert response.json() == {'message': 'success'}
