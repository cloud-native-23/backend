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
    data = response.json()

    # Assert the structure of the response
    assert 'team_joint_list' in data
    assert isinstance(data['team_joint_list'], list)

    # Assert the content of the first team in the list
    first_team = data['team_joint_list'][0]
    assert 'team_id' in first_team
    assert 'order_time' in first_team
    assert 'start_time' in first_team
    assert 'end_time' in first_team
    assert 'stadium_name' in first_team
    assert 'venue_name' in first_team
    assert 'court_name' in first_team
    assert 'current_member_number' in first_team
    assert 'max_number_of_member' in first_team
    assert 'renter_name' in first_team
    assert 'renter_email' in first_team
    assert 'join_status' in first_team
    assert 'team_members' in first_team
    assert isinstance(first_team['team_members'], list)

    # Add specific assertions for the actual values in the response
    assert first_team['team_id'] == 2
    assert first_team['order_time'] == '2023-11-13'
    assert first_team['start_time'] == 13
    assert first_team['end_time'] == 14
    assert first_team['stadium_name'] == '綜合體育館'
    assert first_team['venue_name'] == '桌球室'
    assert first_team['court_name'] == 'C桌'
    assert first_team['current_member_number'] == 4
    assert first_team['max_number_of_member'] == 4
    assert first_team['renter_name'] == '吳暖暖'
    assert first_team['renter_email'] == 'test3@gmail.com'
    assert first_team['join_status'] == '已加入'

    # Assert the content of the team members
    assert len(first_team['team_members']) == 2
    assert first_team['team_members'][0] == {'name': '李美美', 'email': 'test2@gmail.com'}
    assert first_team['team_members'][1] == {'name': '馬力歐', 'email': 'test4@gmail.com'}

def test_get_rent_list_not_logged_in(db_conn, test_client):
    # Make the POST request
    response = test_client.post(
       f"{settings.API_V1_STR}/team/my-join-list/",
    )

    # Assert response status code
    assert response.status_code == 401

    # Assert response data
    response_data = response.json()
    assert response_data["detail"] == "Not authenticated"
