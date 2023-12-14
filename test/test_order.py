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

from app.schemas.order import OrderCreate
from datetime import date

# pytest fixture
db_conn = db_conn
test_client = test_client

# rent list API

def test_get_rent_list_logged_in(db_conn, test_client):
    # Prepare authentication
    email = "cloudnativeg23@gmail.com"

    # Make the POST request
    response = test_client.post(
        f"{settings.API_V1_STR}/order/my-rent-list/",
        headers=get_user_authentication_headers(db_conn, email),  # Replace with your method to get auth headers
    )

    # Assert response status code
    assert response.status_code == 200

    # Assert response data
    response_data = response.json()
    # Assert the structure of the response data
    for order in response_data["orders"]:
        assert "id" in order
        assert "order_time" in order
        assert "start_time" in order
        assert "end_time" in order
        assert "stadium_name" in order
        assert "venue_name" in order
        assert "court_name" in order
        assert "status" in order
        assert "current_member_number" in order
        assert "max_number_of_member" in order
        assert "team_members" in order

def test_get_rent_list_not_logged_in(db_conn, test_client):
    # Make the POST request
    response = test_client.post(
        f"{settings.API_V1_STR}/order/my-rent-list/",
    )

    # Assert response status code
    assert response.status_code == 401

    # Assert response data
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated"

# cancel order API

def test_cancel_order_logged_in(db_conn, test_client):
    # Prepare authentication
    email = "cloudnativeg23@gmail.com"
    
    # Prepare test order data
    order_obj = OrderCreate(
            stadium_court_id = 1,
            renter_id = 1,
            date = date(2023, 12, 12),
            start_time = 10,
            end_time = 11,
            status = 1,
            is_matching = False,
        )
    test_order = crud.order.create(db_conn, obj_in=order_obj)

    # Make the POST request
    response = test_client.post(
        f"{settings.API_V1_STR}/order/order-cancel/?order_id={test_order.id}",
        headers=get_user_authentication_headers(db_conn, email),
    )

        # Parse the response
    response_data = response.json()

    # Assert response status code
    assert response.status_code == 200

    # Assert response data
    assert response_data["message"] == "success"
    order = response_data["order"]
    assert order["id"] is not None
    assert order["stadium_court_id"] == test_order.stadium_court_id
    assert order["renter_id"] == test_order.renter_id
    assert order["date"] == test_order.date.strftime("%Y-%m-%d")
    assert order["start_time"] == test_order.start_time
    assert order["end_time"] == test_order.end_time
    assert order["status"] == 0
    assert order["is_matching"] == test_order.is_matching

    #delete test order
    test_order_del = crud.order.get_by_order_id(db_conn, order_id=test_order.id)
    db_conn.delete(test_order_del)
    db_conn.commit()

def test_cancel_order_not_logged_in(db_conn, test_client):
    # Prepare test order data
    order_obj = OrderCreate(
            stadium_court_id = 1,
            renter_id = 1,
            date = date(2023, 12, 12),
            start_time = 10,
            end_time = 11,
            status = 1,
            is_matching = False,
        )
    test_order = crud.order.create(db_conn, obj_in=order_obj)

    # Make the POST request
    response = test_client.post(
        f"{settings.API_V1_STR}/order/order-cancel/?order_id={test_order.id}",
    )

        # Parse the response
    response_data = response.json()

    # Assert response status code
    assert response.status_code == 401

    # Assert response data
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated"

    #delete test order
    test_order_del = crud.order.get_by_order_id(db_conn, order_id=test_order.id)
    db_conn.delete(test_order_del)
    db_conn.commit()

def test_cancel_order_already_canceled(db_conn, test_client):
    # Prepare authentication
    email = "cloudnativeg23@gmail.com"
    
    # Prepare test order data
    order_obj = OrderCreate(
            stadium_court_id = 1,
            renter_id = 1,
            date = date(2023, 12, 12),
            start_time = 10,
            end_time = 11,
            status = 0,
            is_matching = False,
        )
    test_order = crud.order.create(db_conn, obj_in=order_obj)

    # Make the POST request
    response = test_client.post(
        f"{settings.API_V1_STR}/order/order-cancel/?order_id={test_order.id}",
        headers=get_user_authentication_headers(db_conn, email),
    )

        # Parse the response
    response_data = response.json()

    # Assert response status code
    assert response.status_code == 400

    # Assert response data
    assert response_data["detail"] == "Order is not available to cancel."

    #delete test order
    test_order_del = crud.order.get_by_order_id(db_conn, order_id=test_order.id)
    db_conn.delete(test_order_del)
    db_conn.commit()

