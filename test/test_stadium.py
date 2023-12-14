import random
import string

import loguru
import pytest
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from unittest.mock import patch
from app import crud, models
from app.core.config import settings
from .contest import db_conn, get_user_authentication_headers, test_client

from app.schemas.stadium import StadiumCreate
from app.schemas.stadium_disable import StadiumDisableCreate

# pytest fixture
db_conn = db_conn
test_client = test_client

# Stadium Create API

def test_create_stadium_logged_in(db_conn, test_client):
    # Prepare test data
    email = "cloudnativeg23@gmail.com"
    post_data = {
        "stadium": {
            "name": "test stadium",
            "venue_name": "test venue",
            "address": "test address",
            "picture": "test picture",
            "area": 500,
            "description": "test description",
            "max_number_of_people": 3,
            "google_map_url": "test google map url"
        },
        "stadium_available_times": {
            "weekday": [
                1, 2, 3
            ],
            "start_time": 8,
            "end_time": 20
        },
        "stadium_court_name": [
            "test court A", "test court B"
        ]
    }

    # Make the request
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/create",  # Adjust the URL as needed
        json=post_data,
        headers=get_user_authentication_headers(db_conn, email),
    )

    # Parse the response
    response_data = response.json()

    # Assert response status code
    assert response.status_code == 200

    # Assert response message
    assert response_data["message"] == "success"

    # Assert details of the created stadium
    stadium = response_data["stadium"]
    assert stadium["id"] is not None
    assert stadium["name"] == post_data["stadium"]["name"]
    assert stadium["venue_name"] == post_data["stadium"]["venue_name"]
    assert stadium["address"] == post_data["stadium"]["address"]
    assert stadium["picture"] == post_data["stadium"]["picture"]
    assert stadium["area"] == post_data["stadium"]["area"]
    assert stadium["description"] == post_data["stadium"]["description"]
    assert stadium["max_number_of_people"] == post_data["stadium"]["max_number_of_people"]
    assert stadium["google_map_url"] == post_data["stadium"]["google_map_url"]

    # Assert details of the stadium available times
    i = 0
    for available_time in response_data["stadium_available_times"]:
        assert available_time["id"] is not None
        assert available_time["stadium_id"] == stadium["id"]
        assert available_time["weekday"] == post_data["stadium_available_times"]["weekday"][i]
        assert available_time["start_time"] == post_data["stadium_available_times"]["start_time"]
        assert available_time["end_time"] == post_data["stadium_available_times"]["end_time"]
        i += 1

    # Assert details of the stadium courts
    i = 0
    for court in response_data["stadium_court"]:
        assert court["stadium_court_id"] is not None
        assert court["name"] == post_data["stadium_court_name"][i]
        assert court["is_enabled"] is True
        i += 1

    # Delete the created stadium
    crud.stadium.remove(db_conn, id=stadium["id"])

def test_create_stadium_not_logged_in(db_conn, test_client):
    # Prepare test data
    email = "cloudnativeg23@gmail.com"
    post_data = {
        "stadium": {
            "name": "test stadium",
            "venue_name": "test venue",
            "address": "test address",
            "picture": "test picture",
            "area": 500,
            "description": "test description",
            "max_number_of_people": 3,
            "google_map_url": "test google map url"
        },
        "stadium_available_times": {
            "weekday": [
                1, 2, 3
            ],
            "start_time": 8,
            "end_time": 20
        },
        "stadium_court_name": [
            "test court A", "test court B"
        ]
    }

    # Make the request
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/create",  # Adjust the URL as needed
        json=post_data,
        # headers=get_user_authentication_headers(db_conn, email),
    )

    # Parse the response
    response_data = response.json()

    # Assert response status code
    assert response.status_code == 401

    # Assert response message
    assert response.json()["detail"] == "Not authenticated"

def test_create_stadium_missed_value_logged_in(db_conn, test_client):
    # Prepare test data
    email = "cloudnativeg23@gmail.com"
    post_data = {
        "stadium": {
            "name": "test stadium",
            # "venue_name": "test venue",
            "address": "test address",
            "picture": "test picture",
            "area": 500,
            "description": "test description",
            "max_number_of_people": 3,
            "google_map_url": "test google map url"
        },
        "stadium_available_times": {
            "weekday": [
                1, 2, 3
            ],
            "start_time": 8,
            "end_time": 20
        },
        "stadium_court_name": [
            "test court A", "test court B"
        ]
    }

    # Make the request
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/create",  # Adjust the URL as needed
        json=post_data,
        headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 422

    # Assert response message
    assert response.json()["detail"] == [
        {
            "loc": [
                "body",
                "stadium",
                "venue_name"
            ],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]

def test_create_stadium_missed_value_not_logged_in(db_conn, test_client):

    # Prepare test data
    email = "cloudnativeg23@gmail.com"
    post_data = {
        "stadium": {
            "name": "test stadium",
            # "venue_name": "test venue",
            "address": "test address",
            "picture": "test picture",
            "area": 500,
            "description": "test description",
            "max_number_of_people": 3,
            "google_map_url": "test google map url"
        },
        "stadium_available_times": {
            "weekday": [
                1, 2, 3
            ],
            "start_time": 8,
            "end_time": 20
        },
        "stadium_court_name": [
            "test court A", "test court B"
        ]
    }

    # Make the request
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/create",  # Adjust the URL as needed
        json=post_data,
        # headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 401

    # Assert response message
    assert response.json()["detail"] == "Not authenticated"

def test_create_stadium_exception(db_conn, test_client):
    # Prepare test data
    email = "cloudnativeg23@gmail.com"
    post_data = {
        "stadium": {
            "name": "test stadium",
            "venue_name": "test venue",
            "address": "test address",
            "picture": "test picture",
            "area": 500,
            "description": "test description",
            "max_number_of_people": 3,
            "google_map_url": "test google map url"
        },
        "stadium_available_times": {
            "weekday": [
                1, 2, 3
            ],
            "start_time": 8,
            "end_time": 20
        },
        "stadium_court_name": [
            "test court A", "test court B"
        ]
    }

    # Mock the CRUD operation to raise an exception
    with patch('app.crud.stadium.create', side_effect=Exception("Simulated Failure")):
        response = test_client.post(
            f"{settings.API_V1_STR}/stadium/create",  # Adjust the URL as needed
            json=post_data,
            headers=get_user_authentication_headers(db_conn, email),
        )

    # Assert that an HTTPException with a 500 status code was raised
    assert response.status_code == 500
    assert "Simulated Failure" in response.json()["detail"]

# Stadium List API

def test_get_stadium_list(db_conn, test_client):

    # Make the request
    response = test_client.get(
        f"{settings.API_V1_STR}/stadium/stadium-list/",
        # headers=get_user_authentication_headers(db_conn, email),
    )

    # Parse the response
    response_data = response.json()

    # Assert response status code
    assert response.status_code == 200

    # Assert response message
    assert response_data["message"] == "success"

    # Assert the structure of the response data
    for stadium in response_data["stadium"]:
        assert "id" in stadium
        assert "name" in stadium
        assert "venue_name" in stadium
        assert "picture" in stadium
        assert "area" in stadium
        assert "max_number_of_people" in stadium
        assert "current_people_count" in stadium

def test_get_stadium_list_exception(db_conn, test_client):
    # Make the request
    with patch('app.crud.stadium.get_stadium_list', side_effect=Exception("Simulated Failure")):
        response = test_client.get(
            f"{settings.API_V1_STR}/stadium/stadium-list/",
            # headers=get_user_authentication_headers(db_conn, email),
        )

    # Assert that an HTTPException with a 500 status code was raised
    assert response.status_code == 500
    assert "Simulated Failure" in response.json()["detail"]

# Stadium Delete API 

def test_delete_stadium_logged_in(db_conn, test_client):
    # Create a stadium for testing delete functionality
    stadium_data = {
        "name": "test stadium",
        "venue_name": "test venue",
        "address": "test address",
        "picture": "test picture",
        "area": 500,
        "description": "test description",
        "max_number_of_people": 3,
        "google_map_url": "test google map url"
    }
    stadium_obj = StadiumCreate(**stadium_data)
    test_stadium = crud.stadium.create(db=db_conn, obj_in=stadium_obj, user_id=1)  # Implement this function
    # Prepare authentication
    email = "cloudnativeg23@gmail.com"

    # Make the DELETE request
    response = test_client.delete(
        f"{settings.API_V1_STR}/stadium/delete?stadium_id={test_stadium.id}",
        headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    response_data = response.json()["data"]
    assert response.status_code == 200

    # Assert response message
    assert response.json()["message"] == "success"

def test_delete_stadium_not_logged_in(db_conn, test_client):
    # Create a stadium for testing delete functionality
    stadium_data = {
        "name": "test stadium",
        "venue_name": "test venue",
        "address": "test address",
        "picture": "test picture",
        "area": 500,
        "description": "test description",
        "max_number_of_people": 3,
        "google_map_url": "test google map url"
    }
    stadium_obj = StadiumCreate(**stadium_data)
    test_stadium = crud.stadium.create(db=db_conn, obj_in=stadium_obj, user_id=1)  # Implement this function
    # Prepare authentication
    email = "cloudnativeg23@gmail.com"

    # Make the DELETE request
    response = test_client.delete(
        f"{settings.API_V1_STR}/stadium/delete?stadium_id={test_stadium.id}",
        # headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 401

    # Assert response message
    assert response.json()["detail"] == "Not authenticated"

    #delete the created stadium
    crud.stadium.delete(db_conn, db_obj=test_stadium)

def test_delete_stadium_not_logged_in(db_conn, test_client):
    # Create a stadium for testing delete functionality
    stadium_data = {
        "name": "test stadium",
        "venue_name": "test venue",
        "address": "test address",
        "picture": "test picture",
        "area": 500,
        "description": "test description",
        "max_number_of_people": 3,
        "google_map_url": "test google map url"
    }
    stadium_obj = StadiumCreate(**stadium_data)
    test_stadium = crud.stadium.create(db=db_conn, obj_in=stadium_obj, user_id=1)  # Implement this function
    # Prepare authentication
    email = "cloudnativeg23@gmail.com"

    # Make the DELETE request
    response = test_client.delete(
        f"{settings.API_V1_STR}/stadium/delete?stadium_id={test_stadium.id}",
        # headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 401

    # Assert response message
    assert response.json()["detail"] == "Not authenticated"

    #delete the created stadium
    crud.stadium.delete(db_conn, db_obj=test_stadium)

def test_delete_stadium_no_stadium(db_conn, test_client):
    # Create a stadium for testing delete functionality
    stadium_data = {
        "name": "test stadium",
        "venue_name": "test venue",
        "address": "test address",
        "picture": "test picture",
        "area": 500,
        "description": "test description",
        "max_number_of_people": 3,
        "google_map_url": "test google map url"
    }
    stadium_obj = StadiumCreate(**stadium_data)
    test_stadium = crud.stadium.create(db=db_conn, obj_in=stadium_obj, user_id=1)  # Implement this function
    stadium_id = test_stadium.id

    #delete the created stadium
    crud.stadium.delete(db_conn, db_obj=test_stadium)
    
    # Prepare authentication
    email = "cloudnativeg23@gmail.com"
    
    # Make the DELETE request
    response = test_client.delete(
        f"{settings.API_V1_STR}/stadium/delete?stadium_id={stadium_id}",
        headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 400

    # Assert response message
    assert response.json()["detail"] == "No stadium to delete."

def test_delete_stadium_fail(db_conn, test_client):

    # Prepare authentication
    email = "cloudnativeg23@gmail.com"

    # Make the DELETE request
    with patch('app.crud.stadium.delete', return_value=False):
        response = test_client.delete(
            f"{settings.API_V1_STR}/stadium/delete?stadium_id=1",
            headers=get_user_authentication_headers(db_conn, email),
        )

    # Assert fail
    assert response.json()["message"] == "fail"

# Disable API

def test_disable_stadium_logged_in(db_conn, test_client):
    # Create test data for a stadium and its availability

    # Prepare authentication and request data
    #stadium 1
    email = "cloudnativeg23@gmail.com"
    disable_data = {
        "stadium_id": 1,  # Use the ID of the created test stadium
        "start_date": "2023-11-15",
        "start_time": 11,
        "end_date": "2023-11-15",
        "end_time": 12
    }

    # Make the POST request
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/disable",
        json=disable_data,
        headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 200

    # Assert response message
    response_data = response.json()
    assert response_data["message"] == "success"

    # Assert other response details
    assert response_data["stadium_id"] == disable_data["stadium_id"]
    assert len(response_data["sessions"]) > 0
    assert len(response_data["cancel_orders"]) >= 0

    #undisable the created session
    for session in response_data["sessions"]:
        crud.stadium_disable.delete_by_stadium_id_and_session(db_conn, stadium_id=response_data["stadium_id"], date=session["date"], start_time=session["start_time"])

    #clear order status
    for order in response_data["cancel_orders"]:
        order_obj = crud.order.get_by_order_id(db_conn, order_id=order)
        crud.order.update(db_conn, db_obj=order_obj, obj_in={"status": 1})

def test_disable_stadium_not_logged_in(db_conn, test_client):
    # Create test data for a stadium and its availability

    # Prepare authentication and request data
    email = "cloudnativeg23@gmail.com"
    disable_data = {
        "stadium_id": 1,  # Use the ID of the created test stadium
        "start_date": "2023-12-01",
        "start_time": 10,
        "end_date": "2023-12-01",
        "end_time": 12
    }

    # Make the POST request
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/disable",
        json=disable_data,
        # headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 401

    # Assert response message
    response_data = response.json()
    assert response.json()["detail"] == "Not authenticated"

def test_disable_stadium_no_stadium(db_conn, test_client):
    # Create test data for a stadium and its availability

    # Prepare authentication and request data
    email = "cloudnativeg23@gmail.com"
    disable_data = {
        "stadium_id": 0,  # Use the ID of the created test stadium
        "start_date": "2023-12-01",
        "start_time": 10,
        "end_date": "2023-12-01",
        "end_time": 12
    }

    # Make the POST request
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/disable",
        json=disable_data,
        headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 400

    # Assert response message
    response_data = response.json()
    assert response.json()["detail"] == "No stadium to disable."

def test_disable_stadium_invalid_time(db_conn, test_client):
    # Create test data for a stadium and its availability

    # Prepare authentication and request data
    email = "cloudnativeg23@gmail.com"
    disable_data = {
        "stadium_id": 1,  # Use the ID of the created test stadium
        "start_date": "2023-12-01",
        "start_time": 12,
        "end_date": "2023-12-01",
        "end_time": 10
    }

    # Make the POST request
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/disable",
        json=disable_data,
        headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 400

    # Assert response message
    response_data = response.json()
    assert response.json()["detail"] == "The disable time is not valid."

def test_disable_stadium_already_disabled(db_conn, test_client):
    # Create test data for a stadium and its availability

    # Prepare authentication and request data
    email = "cloudnativeg23@gmail.com"
    disable_data = {
        "stadium_id": 1,  # Use the ID of the created test stadium
        "start_date": "2023-11-14",
        "start_time": 9,
        "end_date": "2023-11-14",
        "end_time": 10
    }

    # Make the POST request
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/disable",
        json=disable_data,
        headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 200

    # Assert response message
    response_data = response.json()
    assert response_data["message"] == "Stadium is already disabled at the time."

    # Assert other response details
    assert response_data["stadium_id"] == disable_data["stadium_id"]
    assert len(response_data["sessions"]) == 0
    assert len(response_data["cancel_orders"]) == 0

def test_disable_stadium_fail(db_conn, test_client):

    # Prepare authentication and request data
    #stadium 1
    email = "cloudnativeg23@gmail.com"
    disable_data = {
        "stadium_id": 1,  # Use the ID of the created test stadium
        "start_date": "2023-11-15",
        "start_time": 11,
        "end_date": "2023-11-15",
        "end_time": 12
    }

    # Make the POST request
    with patch('app.crud.stadium_disable.create', return_value=None):
        response = test_client.post(
            f"{settings.API_V1_STR}/stadium/disable",
            json=disable_data,
            headers=get_user_authentication_headers(db_conn, email),
        )

    # Assert fail
    assert response.json()["message"] == "fail"
    assert response.json()["stadium_id"] == disable_data["stadium_id"]
    assert response.json()["sessions"] == None
    assert response.json()["cancel_orders"] == None

# Undisable API

def test_undisable_stadium_logged_in(db_conn, test_client):
    # Create test data for a stadium and its availability

    # Prepare authentication and request data
    #stadium 1
    email = "cloudnativeg23@gmail.com"

    # Prepare requset data
    stadium_id = 1
    start_date = "2023-11-14"
    start_time = 9
    end_date = "2023-11-14"
    end_time = 11

    # Make the delete request
    response = test_client.delete(
        f"{settings.API_V1_STR}/stadium/undisable?stadium_id={stadium_id}&start_date={start_date}&start_time={start_time}&end_date={end_date}&end_time={end_time}",
        headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 200

    # Assert response message
    response_data = response.json()
    assert response_data["message"] == "success"

    # Assert other response details
    assert response_data["stadium_id"] == stadium_id
    assert len(response_data["sessions"]) > 0

    #disable the delete session
    for session in response_data["sessions"]:
        disable_data = {
            "stadium_id": response_data["stadium_id"],
            "date": session["date"],
            "start_time": session["start_time"],
            "end_time": session["start_time"]+1
        }
        disable_obj = StadiumDisableCreate(**disable_data)
        crud.stadium_disable.create(db_conn, obj_in=disable_obj)

def test_undisable_stadium_not_logged_in(db_conn, test_client):
    # Create test data for a stadium and its availability

    # Prepare authentication and request data
    email = "cloudnativeg23@gmail.com"

    # Prepare requset data
    stadium_id = 1
    start_date = "2023-11-14"
    start_time = 9
    end_date = "2023-11-14"
    end_time = 11

    # Make the delete request
    response = test_client.delete(
        f"{settings.API_V1_STR}/stadium/undisable?stadium_id={stadium_id}&start_date={start_date}&start_time={start_time}&end_date={end_date}&end_time={end_time}",
        # headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 401

    # Assert response message
    response_data = response.json()
    assert response.json()["detail"] == "Not authenticated"

def test_undisable_stadium_no_stadium(db_conn, test_client):
    # Create test data for a stadium and its availability

    # Prepare authentication and request data
    email = "cloudnativeg23@gmail.com"

    # Prepare requset data
    stadium_id = 0
    start_date = "2023-11-14"
    start_time = 9
    end_date = "2023-11-14"
    end_time = 11

    # Make the delete request
    response = test_client.delete(
        f"{settings.API_V1_STR}/stadium/undisable?stadium_id={stadium_id}&start_date={start_date}&start_time={start_time}&end_date={end_date}&end_time={end_time}",
        headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 400

    # Assert response message
    response_data = response.json()
    assert response.json()["detail"] == "No stadium to undisable."

def test_undisable_stadium_invalid_time(db_conn, test_client):
    # Create test data for a stadium and its availability

    # Prepare authentication and request data
    email = "cloudnativeg23@gmail.com"

    # Prepare requset data
    stadium_id = 1
    start_date = "2023-11-14"
    start_time = 19
    end_date = "2023-11-14"
    end_time = 11

    # Make the delete request
    response = test_client.delete(
        f"{settings.API_V1_STR}/stadium/undisable?stadium_id={stadium_id}&start_date={start_date}&start_time={start_time}&end_date={end_date}&end_time={end_time}",
        headers=get_user_authentication_headers(db_conn, email),
    )

    # Assert response status code
    assert response.status_code == 400

    # Assert response message
    response_data = response.json()
    assert response.json()["detail"] == "The undisable time is not valid."

def test_undisable_stadium_not_disabled(db_conn, test_client):

    # Create test data for a stadium and its availability

    # Prepare authentication and request data
    email = "cloudnativeg23@gmail.com"

    # Prepare requset data
    stadium_id = 1
    start_date = "2023-12-14"
    start_time = 15
    end_date = "2023-12-14"
    end_time = 17

    # Make the delete request
    response = test_client.delete(
        f"{settings.API_V1_STR}/stadium/undisable?stadium_id={stadium_id}&start_date={start_date}&start_time={start_time}&end_date={end_date}&end_time={end_time}",
        headers=get_user_authentication_headers(db_conn, email),
    )
    # Assert response status code
    assert response.status_code == 200

    # Assert response message
    response_data = response.json()
    assert response_data["message"] == "Stadium is not disabled at the time."

    # Assert other response details
    assert response_data["stadium_id"] == stadium_id
    assert len(response_data["sessions"]) == 0

def test_undisable_stadium_exception(db_conn, test_client):
        # Prepare authentication and request data
    #stadium 1
    email = "cloudnativeg23@gmail.com"
    # Prepare requset data
    stadium_id = 1
    start_date = "2023-11-14"
    start_time = 9
    end_date = "2023-11-14"
    end_time = 11

    # Make the POST request
    with patch('app.crud.stadium_disable.delete_by_stadium_id_and_session', return_value=None):
        response = test_client.delete(
                f"{settings.API_V1_STR}/stadium/undisable?stadium_id={stadium_id}&start_date={start_date}&start_time={start_time}&end_date={end_date}&end_time={end_time}",
                headers=get_user_authentication_headers(db_conn, email),
            )

    # Assert exception
    assert response.status_code == 400
    assert response.json()["detail"] == f"Fail to undisable stadium. Stadium ID: {stadium_id}, Date: {start_date}, Start Time: {start_time}"

def test_get_stadium_info_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/info?stadium_id=1",
        headers=get_user_authentication_headers(db_conn, email),
    )
    response_data = response.json()["data"]
    assert response.status_code == 200
    assert response_data["id"] == 1
    assert response_data["name"] == "綜合體育館"
    assert response_data["venue_name"] == "桌球室"
    assert response_data["address"] == "臺北市大安區羅斯福路四段1號"
    assert response_data["picture"] == None
    assert response_data["area"] == 906
    assert response_data["description"] == "共6張球桌，可機動調整成集會場地/羽球場地(挑高：9公尺)"
    assert response_data["created_user"] == 1
    assert response_data["max_number_of_people"] == 4
    assert response_data["google_map_url"] == None
    assert len(response_data["stadium_courts"]) == 6
    assert len(response_data["available_times"]["weekdays"]) == 5
    assert response_data["available_times"]["start_time"] == 9
    assert response_data["available_times"]["end_time"] == 19
    assert response.json()["message"] == "success"

def test_get_stadium_info_not_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/info?stadium_id=1",
        # headers=get_user_authentication_headers(db_conn, email),
    )
    response_data = response.json()["data"]
    assert response.status_code == 200
    assert response_data["id"] == 1
    assert response_data["name"] == "綜合體育館"
    assert response_data["venue_name"] == "桌球室"
    assert response_data["address"] == "臺北市大安區羅斯福路四段1號"
    assert response_data["picture"] == None
    assert response_data["area"] == 906
    assert response_data["description"] == "共6張球桌，可機動調整成集會場地/羽球場地(挑高：9公尺)"
    assert response_data["created_user"] == 1
    assert response_data["max_number_of_people"] == 4
    assert response_data["google_map_url"] == None
    assert len(response_data["stadium_courts"]) == 6
    assert len(response_data["available_times"]["weekdays"]) == 5
    assert response_data["available_times"]["start_time"] == 9
    assert response_data["available_times"]["end_time"] == 19
    assert response.json()["message"] == "success"

def test_get_stadium_info_stadium_not_exist_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/info?stadium_id=5",
        headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Fail to get stadium info. No stadium data with stadium_id = {}.".format(5)

def test_get_stadium_info_stadium_not_exist_not_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/info?stadium_id=5",
        # headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Fail to get stadium info. No stadium data with stadium_id = {}.".format(5)

def test_get_stadium_info_missing_param_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/info",
        headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] ==["query", "stadium_id"]
    assert response.json()["detail"][0]["msg"] == "field required"
    assert response.json()["detail"][0]["type"] == "value_error.missing"

def test_get_stadium_info_missing_param_not_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium/info",
        # headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] ==["query", "stadium_id"]
    assert response.json()["detail"][0]["msg"] == "field required"
    assert response.json()["detail"][0]["type"] == "value_error.missing"

def test_update_stadium_logged_in(db_conn, test_client):
    email = "cloudnativeg23@gmail.com"
    put_data = {
                   "id": 2,
                    "name": "新的體育館與戶外場地",
                    "venue_name": "新的新生籃球場",
                    "address": "新的臺北市大安區羅斯福路四段1號",
                    "picture": "test picture value",
                    "area": 9200, # 920
                    "description": "新的週一至六提供夜間照明至晚上10點，週日無提供夜間照明；遇雨或場地濕滑暫停使用",
                    "max_number_of_people": 10, # 12
                    "google_map_url": "https://www.google.com", # null
                    "stadium_courts": [
                        {
                            "id": 7,
                            "name": "新的A場"
                        },
                        {
                            "id": 8,
                            "name": "新的B場"
                        },
                        {
                            "id": 9,
                            "name": "新的C場"
                        },
                    ],
                    "available_times": {
                        "weekdays": [
                            1,2,3,4,5,6,7
                        ],
                        "start_time": 7, # 8 
                        "end_time": 23 # 22
                    }
    }
    response = test_client.put(
        f"{settings.API_V1_STR}/stadium",
        json=put_data,
        headers=get_user_authentication_headers(db_conn, email)
    )
    response_data = response.json()["data"]
    assert response.status_code == 200
    assert response_data["name"] == put_data["name"]
    assert response_data["venue_name"] == put_data["venue_name"]
    assert response_data["address"] == put_data["address"]
    assert response_data["picture"] == put_data["picture"]
    assert response_data["area"] == put_data["area"]
    assert response_data["description"] == put_data["description"]
    assert response_data["max_number_of_people"] == put_data["max_number_of_people"]
    assert response_data["google_map_url"] == put_data["google_map_url"]
    for idx, court in enumerate(response_data["stadium_courts"]):
        assert court["name"] == put_data["stadium_courts"][idx]["name"]
    assert response_data["available_times"]["weekdays"] == put_data["available_times"]["weekdays"]
    assert response_data["available_times"]["start_time"] == put_data["available_times"]["start_time"]
    assert response_data["available_times"]["end_time"] == put_data["available_times"]["end_time"]
    assert response.json()["message"] == "success"
    # update updated data with original value
    # stadium
    stadium_obj = crud.stadium.get_by_stadium_id(db=db_conn, stadium_id=put_data["id"])
    stadium_obj.name = "體育館與戶外場地"
    stadium_obj.venue_name = "新生籃球場"
    stadium_obj.address = "臺北市大安區羅斯福路四段1號"
    stadium_obj.picture = None
    stadium_obj.area = 920
    stadium_obj.description = "週一至六提供夜間照明至晚上10點，週日無提供夜間照明；遇雨或場地濕滑暫停使用"
    stadium_obj.max_number_of_people = 10
    stadium_obj.google_map_url = None
    db_conn.add(stadium_obj)
    # stadium_court
    stadium_court_objs = db_conn.query(models.stadium_court.StadiumCourt).filter(models.stadium_court.StadiumCourt.stadium_id == put_data["id"]).all()
    for stadium_court in stadium_court_objs:
        stadium_court.name = stadium_court.name[2:]
        db_conn.add(stadium_court)
    # delete all first
    db_conn.query(models.stadium_available_time.StadiumAvailableTime).filter(models.stadium_available_time.StadiumAvailableTime.stadium_id == put_data["id"]).delete()
    # create new available_times
    for weekday in put_data["available_times"]["weekdays"]:
        create_available_time = models.stadium_available_time.StadiumAvailableTime(
            stadium_id = put_data["id"],
            weekday = weekday,
            start_time = put_data["available_times"]["start_time"],
            end_time = put_data["available_times"]["end_time"]
        )
        db_conn.add(create_available_time)
    db_conn.commit()

def test_update_stadium_not_logged_in(db_conn, test_client):
    email = "cloudnativeg23@gmail.com"
    put_data = {
                    "id": 2,
                    "name": "新的體育館與戶外場地",
                    "venue_name": "新的新生籃球場",
                    "address": "新的臺北市大安區羅斯福路四段1號",
                    "picture": "test picture value",
                    "area": 9200, # 920
                    "description": "新的週一至六提供夜間照明至晚上10點，週日無提供夜間照明；遇雨或場地濕滑暫停使用",
                    "max_number_of_people": 10, # 12
                    "google_map_url": "https://www.google.com", # null
                    "stadium_courts": [
                        {
                            "id": 7,
                            "name": "新的A場"
                        },
                        {
                            "id": 8,
                            "name": "新的B場"
                        },
                        {
                            "id": 9,
                            "name": "新的C場"
                        },
                    ],
                    "available_times": {
                        "weekdays": [
                            1,2,3,4,5,6,7
                        ],
                        "start_time": 7, # 8 
                        "end_time": 23 # 22
                    }
    }
    response = test_client.put(
        f"{settings.API_V1_STR}/stadium",
        json=put_data,
        # headers=get_user_authentication_headers(db_conn, email)
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_update_stadium_stadium_not_exist_logged_in(db_conn, test_client):
    email = "cloudnativeg23@gmail.com"
    put_data = {
                   "id": 100,
                    "name": "新的體育館與戶外場地",
                    "venue_name": "新的新生籃球場",
                    "address": "新的臺北市大安區羅斯福路四段1號",
                    "picture": "test picture value",
                    "area": 9200, # 920
                    "description": "新的週一至六提供夜間照明至晚上10點，週日無提供夜間照明；遇雨或場地濕滑暫停使用",
                    "max_number_of_people": 10, # 12
                    "google_map_url": "https://www.google.com", # null
                    "stadium_courts": [
                        {
                            "id": 7,
                            "name": "新的A場"
                        },
                        {
                            "id": 8,
                            "name": "新的B場"
                        },
                        {
                            "id": 9,
                            "name": "新的C場"
                        },
                    ],
                    "available_times": {
                        "weekdays": [
                            1,2,3,4,5,6,7
                        ],
                        "start_time": 7, # 8 
                        "end_time": 23 # 22
                    }
    }
    response = test_client.put(
        f"{settings.API_V1_STR}/stadium",
        json=put_data,
        headers=get_user_authentication_headers(db_conn, email)
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Fail to update stadium. No stadium data with stadium_id = {}.".format(put_data["id"])

def test_update_stadium_add_new_court_logged_in(db_conn, test_client):
    email = "cloudnativeg23@gmail.com"
    put_data = {
                   "id": 2,
                    "name": "體育館與戶外場地",
                    "venue_name": "新生籃球場",
                    "max_number_of_people": 12,
                    "stadium_courts": [
                        {
                            "id": 7,
                            "name": "A場"
                        },
                        {
                            "id": 8,
                            "name": "B場"
                        },
                        {
                            "id": 9,
                            "name": "C場"
                        },
                        {
                            "name": "D場"
                        }
                    ],
                    "available_times": {
                        "weekdays": [
                            1,2,3,4,5,6,7
                        ],
                        "start_time": 8,
                        "end_time": 22
                    }
    }
    response = test_client.put(
        f"{settings.API_V1_STR}/stadium",
        json=put_data,
        headers=get_user_authentication_headers(db_conn, email)
    )
    response_data = response.json()["data"]
    assert response.status_code == 200
    assert response_data["name"] == put_data["name"]
    assert response_data["venue_name"] == put_data["venue_name"]
    assert response_data["max_number_of_people"] == put_data["max_number_of_people"]
    for idx, court in enumerate(response_data["stadium_courts"]):
        assert court["name"] == put_data["stadium_courts"][idx]["name"]
    assert response_data["available_times"]["weekdays"] == put_data["available_times"]["weekdays"]
    assert response_data["available_times"]["start_time"] == put_data["available_times"]["start_time"]
    assert response_data["available_times"]["end_time"] == put_data["available_times"]["end_time"]
    assert response.json()["message"] == "success"
    # update updated data with original value
    # stadium_court
    stadium_court_objs = db_conn.query(models.stadium_court.StadiumCourt).filter(models.stadium_court.StadiumCourt.stadium_id == put_data["id"]).all()
    # temp = [x for x in put_data["stadium_courts"]]
    # print('temp >>> ', temp)
    orig_stadium_court_ids = [x["id"] for x in put_data["stadium_courts"] if "id" in x.keys()]
    for stadium_court in stadium_court_objs:
        if stadium_court.id not in orig_stadium_court_ids:
            db_conn.query(models.stadium_court.StadiumCourt).filter(models.stadium_court.StadiumCourt.id == stadium_court.id).delete()
    db_conn.commit()

# def test_update_stadium_exception(db_conn, test_client):
#     email = "cloudnativeg23@gmail.com"
#     put_data = {
#                    "id": 2,
#                     "name": "新的體育館與戶外場地",
#                     "venue_name": "新的新生籃球場",
#                     "address": "新的臺北市大安區羅斯福路四段1號",
#                     "picture": "test picture value",
#                     "area": 9200, # 920
#                     "description": "新的週一至六提供夜間照明至晚上10點，週日無提供夜間照明；遇雨或場地濕滑暫停使用",
#                     "max_number_of_people": 10, # 12
#                     "google_map_url": "https://www.google.com", # null
#                     "stadium_courts": [
#                         {
#                             "id": 7,
#                             "name": "新的A場"
#                         },
#                         {
#                             "id": 8,
#                             "name": "新的B場"
#                         },
#                         {
#                             "id": 9,
#                             "name": "新的C場"
#                         },
#                     ],
#                     "available_times": {
#                         "weekdays": [
#                             1,2,3,4,5,6,7
#                         ],
#                         "start_time": 7, # 8 
#                         "end_time": 23 # 22
#                     }
#     }
#     # Mock the CRUD operation to raise an exception
#     with patch('app.crud.stadium_court.get_all_by_stadium_id', side_effect=Exception("Simulated Failure")):
#         response = test_client.put(
#             f"{settings.API_V1_STR}/stadium",
#             json=put_data,
#             headers=get_user_authentication_headers(db_conn, email),
#         )

#     # Assert that an HTTPException with a 500 status code was raised
#     assert response.status_code == 500
#     assert "Simulated Failure" in response.json()["detail"]

def test_get_stadium_availability(db_conn, test_client):
        # Prepare authentication and request data
    #stadium 1
    email = "test1@gmail.com"
    # Prepare requset data
    stadium_id = 1
    query_date = "2023-11-14"
    headcount = 3
    level_requirement = "EASY"

    # Make the POST request
    with patch('app.crud.stadium_disable.delete_by_stadium_id_and_session', return_value=None):
        response = test_client.post(
                f"{settings.API_V1_STR}/stadium/timetable/?stadium_id={stadium_id}&query_date={query_date}&headcount={headcount}&level_requirement={level_requirement}",
                headers=get_user_authentication_headers(db_conn, email),
            )

    # Assert exception
    assert response.status_code == 200

    stadium_id = 300000
    with patch('app.crud.stadium_disable.delete_by_stadium_id_and_session', return_value=None):
        response = test_client.post(
                f"{settings.API_V1_STR}/stadium/timetable/?stadium_id={stadium_id}&query_date={query_date}&headcount={headcount}&level_requirement={level_requirement}",
                headers=get_user_authentication_headers(db_conn, email),
            )
    assert response.status_code == 404


def test_get_stadium_availability_for_provider(db_conn, test_client):
        # Prepare authentication and request data
    #stadium 1
    email = "test1@gmail.com"
    # Prepare requset data
    stadium_id = 1
    query_date = "2023-11-14"
    headcount = 3
    level_requirement = "EASY"

    # Make the POST request
    with patch('app.crud.stadium_disable.delete_by_stadium_id_and_session', return_value=None):
        response = test_client.post(
                f"{settings.API_V1_STR}/stadium/providertimetable/?stadium_id={stadium_id}&query_date={query_date}",
                headers=get_user_authentication_headers(db_conn, email),
            )

    # Assert exception
    assert response.status_code == 200

    stadium_id = 300000
    with patch('app.crud.stadium_disable.delete_by_stadium_id_and_session', return_value=None):
        response = test_client.post(
                f"{settings.API_V1_STR}/stadium/providertimetable/?stadium_id={stadium_id}&query_date={query_date}",
                headers=get_user_authentication_headers(db_conn, email),
            )
    assert response.status_code == 404