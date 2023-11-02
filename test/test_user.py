import random
import string

import loguru
import pytest
from fastapi.encoders import jsonable_encoder

from app import crud
from app.core.config import settings

from .contest import db_conn, get_user_authentication_headers, test_client

# pytest fixture
db_conn = db_conn
test_client = test_client


@pytest.fixture(scope="module")
def get_server_api():
    server_name = "http://localhost:8000"
    return server_name


# def get_user_authentication_headers(session, email):
#     user = crud.user.get_by_email(db=session, email=email)
#     loguru.logger.info(jsonable_encoder(user))
#     user = jsonable_encoder(user)
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = security.create_access_token(
#         user["user_uuid"], expires_delta=access_token_expires
#     )
#     headers = {"Authorization": f"Bearer {access_token}"}
#     return headers


def random_lower_string():
    return "".join(random.choices(string.ascii_lowercase, k=32))


# Test
def test_read_user_me_who_has_logged_in(get_server_api, db_conn, test_client):
    # crud.user.create(
    #     db_conn,
    #     obj_in=schemas.UserCreate(
    #         email="admin@sdm-teamatch.com", name="admin", is_google_sso=True
    #     ),
    # )
    email = "admin@sdm-teamatch.com"
    loguru.logger.info(jsonable_encoder(crud.user.get_by_email(db_conn, email=email)))

    response = test_client.get(
        f"{get_server_api}{settings.API_V1_STR}/users/profile/me/",
        headers=get_user_authentication_headers(db_conn, email),
    )
    loguru.logger.info(response)

    assert response.status_code == 200
    assert email == response.json()["data"]["email"]
    assert response.json()["message"] == "success"


def test_read_user_me_who_has_not_logged_in(get_server_api, test_client):
    response = test_client.get(
        f"{get_server_api}{settings.API_V1_STR}/users/profile/me/"
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_read_user_me_who_has_wrong_credential(get_server_api, test_client):
    response = test_client.get(
        f"{get_server_api}{settings.API_V1_STR}/users/profile/me/",
        headers={"Authorization": "Bearer wrongToken"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough segments"


def test_update_logged_in_user_profile(get_server_api, db_conn, test_client):
    # crud.user.create(
    #     db_conn,
    #     obj_in=schemas.UserCreate(
    #         email="admin@sdm-teamatch.com", name="admin", is_google_sso=True
    #     ),
    # )
    email = "admin@sdm-teamatch.com"

    line_id = "fake_line_id" + random_lower_string()
    update_data = {"line_id": line_id}

    response = test_client.put(
        f"{get_server_api}{settings.API_V1_STR}/users/profile",
        json=update_data,
        headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 200
    assert email == response.json()["data"]["email"]
    assert response.json()["message"] == "success"


def test_update_user_profile_who_has_not_logged_in(get_server_api, test_client):
    update_data = {"line_id": "fake_line_id"}
    response = test_client.put(
        f"{get_server_api}{settings.API_V1_STR}/users/profile", json=update_data
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_update_user_profile_who_has_wrong_credential(get_server_api, test_client):
    update_data = {"line_id": "fake_line_id"}
    response = test_client.put(
        f"{get_server_api}{settings.API_V1_STR}/users/profile",
        json=update_data,
        headers={"Authorization": "Bearer wrongToken"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough segments"


def test_create_new_user(get_server_api, test_client, db_conn):
    email = "create-test-user@example.com"
    name = "test-user"
    password = "testuser"
    loguru.logger.info(jsonable_encoder(crud.user.get_by_email(db_conn, email=email)))
    data = {"email": email, "name": name, "password": password}
    response = test_client.post(
        f"{get_server_api}{settings.API_V1_STR}/users/", json=data
    )

    obj = crud.user.get_by_email(db_conn, email=email)
    db_conn.delete(obj)
    db_conn.commit()

    assert response.status_code == 200
    created_user = response.json()
    assert email == created_user["data"]["email"]


def test_create_existing_user(get_server_api, test_client):
    # crud.user.create(
    #     session,
    #     obj_in=schemas.UserCreate(
    #         email="admin@sdm-teamatch.com", name="admin", is_google_sso=True
    #     ),
    # )
    email = "admin@sdm-teamatch.com"
    name = "admin"

    data = {"email": email, "name": name}
    response = test_client.post(
        f"{get_server_api}{settings.API_V1_STR}/users/", json=data
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "The user with this username already exists in the system."
    )


def test_read_user_by_user_uuid(db_conn, test_client):
    user = crud.user.get_by_email(db=db_conn, email=settings.ADMIN_EMAIL)
    user_with_user_uuid = crud.user.get_by_user_uuid(
        db=db_conn, user_uuid=user.user_uuid
    )

    assert user_with_user_uuid.email == settings.ADMIN_EMAIL
