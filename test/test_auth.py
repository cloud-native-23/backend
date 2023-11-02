import httpx
import loguru
import pytest
from fastapi.encoders import jsonable_encoder
from google.auth.transport import requests
from google.oauth2 import id_token

from app import crud
from app.core.config import settings

from .contest import db_conn, test_client

client = httpx.AsyncClient()

# pytest fixture
db_conn = db_conn
test_client = test_client


@pytest.fixture(scope="module")
def get_server_api():
    server_name = "http://localhost:8000"
    return server_name


@pytest.fixture(scope="module")
def get_token_id():
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    refresh_token = "1//04puCTtWhEyMiCgYIARAAGAQSNwF-L9IrfZCxCMa5klAX2MxipBNzCbCr2rEgddoS7ejTrWJL9Oza8TJnBcoZPXg6EQgYK3Nwh4w"  # SDM
    # refresh_token = "1//048_5yRM12FFvCgYIARAAGAQSNwF-L9IrdAP1F8Kl_5tpnrTALjwUscnYjsUsl056-S0LCznkp3TZdMHUClAAZUN33XLenEQuL04"  # me
    # access_token = "ya29.a0Ael9sCMnHqRrjWZkL1l7bZuz3IXXTpKtJ90aiiw0pHbneWgIuFA-6MEFWjcEs7ZpKvMmKE67mkrp5Fu6wJYXmhK2cLACneHOIDgrbMB8j3Y6-cmmEVaoNWsOCxg21w3GnH0kUoIp6IOxeLFoUSWJm8xzPgPxaCgYKAfgSARMSFQF4udJhqsJNcq5l_FTXN0nRGIbnTA0163" #me
    post_body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    response = httpx.post("https://oauth2.googleapis.com/token", json=post_body)

    id_token = response.json()["id_token"]

    return id_token


# test
def test_google_auth_verify_id_token_successfully(
    get_server_api, get_token_id, test_client, db_conn
):
    credential = get_token_id
    data = {"credential": credential}
    response = test_client.post(
        f"{get_server_api}{settings.API_V1_STR}/auth/sso-login", json=data
    )
    # 因為這個google身分沒有名字之類的info
    # assert response.status_code == 400
    # assert (
    #     response.json()["detail"]
    #     == "Missing some user info from google authentication. Please use another way to create new account."
    # )
    idinfo = id_token.verify_oauth2_token(
        credential,
        requests.Request(),
        settings.GOOGLE_CLIENT_ID,
        clock_skew_in_seconds=5,
    )
    email = idinfo["email"]
    user = crud.user.get_by_email(db=db_conn, email=email)
    loguru.logger.info(jsonable_encoder(user))

    if user:
        assert response.status_code == 200
    else:
        # 因為這個google身分沒有名字之類的info
        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Missing some user info from google authentication. Please use another way to create new account."
        )


def test_google_auth_verify_id_token_failed(get_server_api, test_client):
    credential = "fake_token_id"
    data = {"credential": credential}
    response = test_client.post(
        f"{get_server_api}{settings.API_V1_STR}/auth/sso-login", json=data
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
