import random
import string

import loguru
import pytest
from fastapi.encoders import jsonable_encoder

from app.core.config import settings
from .contest import db_conn, get_user_authentication_headers, test_client

# pytest fixture
db_conn = db_conn
test_client = test_client

def test_get_all_user_except_provider_and_current_user(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.get(
        f"{settings.API_V1_STR}/users/get-all-users",
        headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 200
    assert response.json()["data"][0]["email"] == "test2@gmail.com" # skip provider(cloudnativeg23) and current_user(test1)
    assert response.json()["message"] == "success"

def test_get_all_user_except_provider_and_current_user_not_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.get(
        f"{settings.API_V1_STR}/users/get-all-users",
        # headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"