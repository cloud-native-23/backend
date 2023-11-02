from datetime import timedelta

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_utils.functions import create_database, database_exists

from app import crud
from app.core import security
from app.core.config import settings
from app.database.base_class import Base
from app.database.test.test_database import (
    SQLALCHEMY_DATABASE_URL,
    TestingSessionLocal,
    engine,
)
from app.main import app
from app.routers.deps import get_db

if not database_exists(SQLALCHEMY_DATABASE_URL):
    create_database(SQLALCHEMY_DATABASE_URL)

# Set up the database once
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="module")
def db_conn():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def test_client():
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    # reset overrides
    app.dependency_overrides = {}


test_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_user_authentication_headers(session, email):
    user = crud.user.get_by_email(db=session, email=email)
    user = jsonable_encoder(user)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user["user_uuid"], expires_delta=access_token_expires
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


# def override_get_db():
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()


# app.dependency_overrides[get_db] = override_get_db

# test_session = TestingSessionLocal(autocommit=False, autoflush=False, bind=engine)

# test_client = TestClient(app)
