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

def test_leave(db_conn, test_client):
    email = "test4@gmail.com"
    # correct
    response = test_client.post(
        f"{settings.API_V1_STR}/team-member/leave?team_id=18",
        headers=get_user_authentication_headers(db_conn, email)
    )
    assert response.status_code == 200
    assert response.json() == {'message': 'success'}

    # missing team_id 
    response = test_client.post(
        f"{settings.API_V1_STR}/team-member/leave?team_id=",
        headers=get_user_authentication_headers(db_conn, email)
    )
    print('response.text',response.text)
    assert response.status_code == 422
    assert "value is not a valid integer" in response.json()["detail"][0]["msg"]

    # invalid team_id
    response = test_client.post(
        f"{settings.API_V1_STR}/team-member/leave?team_id=30000",
        headers=get_user_authentication_headers(db_conn, email)
    )
    assert response.status_code == 400
    assert "No team to leave." in response.text