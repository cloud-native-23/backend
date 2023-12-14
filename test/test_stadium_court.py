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

def test_get_rent_info_available_to_rent_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent-info?stadium_id=2&date=2023-11-18&start_time=20&headcount=2&level_requirement=hard",
        headers=get_user_authentication_headers(db_conn, email),
    )
    response_data = response.json()["data"][0]
    assert response.status_code == 200
    assert response_data["stadium_court_id"] == 7
    assert response_data["name"] == "A場"
    assert response_data["is_enabled"] == True
    assert response_data["renter_name"] == None
    assert response_data["team_id"] == None
    assert response_data["current_member_number"] == None
    assert response_data["max_number_of_member"] == None
    assert response_data["level_requirement"] == None
    assert response_data["status"] == "租借"
    assert response_data["status_description"] == ""
    assert response.json()["message"] == "success"

def test_get_rent_info_current_user_is_renter_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent-info?stadium_id=2&date=2023-11-16&start_time=20&headcount=2&level_requirement=hard",
        headers=get_user_authentication_headers(db_conn, email),
    )
    response_data = response.json()["data"][0]
    assert response.status_code == 200
    assert response_data["stadium_court_id"] == 7
    assert response_data["name"] == "A場"
    assert response_data["is_enabled"] == True
    assert response_data["renter_name"] == "王小明"
    assert response_data["team_id"] == 16
    assert response_data["current_member_number"] == 1
    assert response_data["max_number_of_member"] == 6
    assert response_data["level_requirement"] == ["中級", "高級"]
    assert response_data["status"] == "無法加入"
    assert response_data["status_description"] == "該時段租借者即為使用者"
    assert response.json()["message"] == "success"

def test_get_rent_info_current_user_is_not_renter_logged_in(db_conn, test_client):
    email = "test2@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent-info?stadium_id=2&date=2023-11-16&start_time=20&headcount=2&level_requirement=hard",
        headers=get_user_authentication_headers(db_conn, email),
    )
    response_data = response.json()["data"][0]
    assert response.status_code == 200
    assert response_data["stadium_court_id"] == 7
    assert response_data["name"] == "A場"
    assert response_data["is_enabled"] == True
    assert response_data["renter_name"] == "王小明"
    assert response_data["team_id"] == 16
    assert response_data["current_member_number"] == 1
    assert response_data["max_number_of_member"] == 6
    assert response_data["level_requirement"] == ["中級", "高級"]
    assert response_data["status"] == "加入"
    assert response_data["status_description"] == ""
    assert response.json()["message"] == "success"

def test_get_rent_info_current_user_is_already_in_team_logged_in(db_conn, test_client):
    email = "test2@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent-info?stadium_id=2&date=2023-11-17&start_time=15&headcount=2&level_requirement=medium",
        headers=get_user_authentication_headers(db_conn, email),
    )
    response_data = response.json()["data"][0]
    assert response.status_code == 200
    assert response_data["stadium_court_id"] == 7
    assert response_data["name"] == "A場"
    assert response_data["is_enabled"] == True
    assert response_data["renter_name"] == "露比"
    assert response_data["team_id"] == 19
    assert response_data["current_member_number"] == 3
    assert response_data["max_number_of_member"] == 10
    assert response_data["level_requirement"] == ["初級", "中級", "高級"]
    assert response_data["status"] == "無法加入"
    assert response_data["status_description"] == "使用者已加入該隊伍"
    assert response.json()["message"] == "success"

def test_get_rent_info_level_requirement_not_match_logged_in(db_conn, test_client):
    email = "test2@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent-info?stadium_id=1&date=2023-11-15&start_time=11&headcount=2&level_requirement=hard",
        headers=get_user_authentication_headers(db_conn, email),
    )
    response_data = response.json()["data"][0]
    assert response.status_code == 200
    assert response_data["stadium_court_id"] == 1
    assert response_data["name"] == "A桌"
    assert response_data["is_enabled"] == True
    assert response_data["renter_name"] == "王小明"
    assert response_data["team_id"] == 3
    assert response_data["current_member_number"] == 2
    assert response_data["max_number_of_member"] == 4
    assert response_data["level_requirement"] == ["中級"]
    assert response_data["status"] == "無法加入"
    assert response_data["status_description"] == "能力程度不符"
    assert response.json()["message"] == "success"

def test_get_rent_info_headcount_over_available_member_num_logged_in(db_conn, test_client):
    email = "test2@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent-info?stadium_id=1&date=2023-11-15&start_time=11&headcount=3&level_requirement=medium",
        headers=get_user_authentication_headers(db_conn, email),
    )
    response_data = response.json()["data"][0]
    assert response.status_code == 200
    assert response_data["stadium_court_id"] == 1
    assert response_data["name"] == "A桌"
    assert response_data["is_enabled"] == True
    assert response_data["renter_name"] == "王小明"
    assert response_data["team_id"] == 3
    assert response_data["current_member_number"] == 2
    assert response_data["max_number_of_member"] == 4
    assert response_data["level_requirement"] == ["中級"]
    assert response_data["status"] == "無法加入"
    assert response_data["status_description"] == "欲加入人數大於隊伍剩餘可加入人數"
    assert response.json()["message"] == "success"

def test_get_rent_info_not_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent-info?stadium_id=2&date=2023-11-16&start_time=20&headcount=2&level_requirement=hard",
        # headers=get_user_authentication_headers(db_conn, email),
    )
    response_data = response.json()["data"][0]
    assert response.status_code == 200
    assert response_data["stadium_court_id"] == 7
    assert response_data["name"] == "A場"
    assert response_data["is_enabled"] == True
    assert response_data["renter_name"] == "王小明"
    assert response_data["team_id"] == 16
    assert response_data["current_member_number"] == 1
    assert response_data["max_number_of_member"] == 6
    assert response_data["level_requirement"] == ["中級", "高級"]
    assert response_data["status"] == "加入"
    assert response_data["status_description"] == ""
    assert response.json()["message"] == "success"

def test_get_rent_info_stadium_not_exist_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent-info?stadium_id=5&date=2023-11-16&start_time=20&headcount=2&level_requirement=hard",
        headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Fail to find stadium with stadium_id = {}.".format(5)

def test_get_rent_info_stadium_not_exist_not_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent-info?stadium_id=5&date=2023-11-16&start_time=20&headcount=2&level_requirement=hard",
        # headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Fail to find stadium with stadium_id = {}.".format(5)

def test_rent_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    post_data = {
                    "stadium_court_id": 1,
                    "date": "2023-11-15",
                    "start_time": 20,
                    "end_time": 21,
                    "current_member_number": 2,
                    "max_number_of_member": 4,
                    "is_matching": True,
                    "level_requirement": ["初級", "中級", "高級"],
                    "team_member_emails": [
                        "test2@gmail.com"
                    ]
                }
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent",
        json=post_data,
        headers=get_user_authentication_headers(db_conn, email),
    )
    response_data = response.json()["data"]
    assert response.status_code == 200
    assert response_data["stadium_court_id"] == post_data["stadium_court_id"]
    assert response_data["date"] == post_data["date"]
    assert response_data["start_time"] == post_data["start_time"]
    assert response_data["end_time"] == post_data["end_time"]
    assert response_data["current_member_number"] == post_data["current_member_number"]
    assert response_data["max_number_of_member"] == post_data["max_number_of_member"]
    assert response_data["is_matching"] == post_data["is_matching"]
    assert response_data["level_requirement"] == post_data["level_requirement"]
    assert response_data["team_members"][0]['email'] == post_data["team_member_emails"][0]
    assert response.json()["message"] == "success"
    # delete created data
    obj = crud.order.get_by_order_id(
        db=db_conn, order_id=response.json()["data"]["id"]
    )
    db_conn.delete(obj)
    db_conn.commit()

def test_rent_not_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    post_data = {
                    "stadium_court_id": 1,
                    "date": "2023-11-15",
                    "start_time": 20,
                    "end_time": 21,
                    "current_member_number": 2,
                    "max_number_of_member": 4,
                    "is_matching": True,
                    "level_requirement": 6,
                    "team_member_emails": [
                        "test2@gmail.com"
                    ]
                }
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent",
        json=post_data,
        # headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_rent_stadium_court_not_exist_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    post_data = {
                    "stadium_court_id": 100,
                    "date": "2023-11-15",
                    "start_time": 20,
                    "end_time": 21,
                    "current_member_number": 2,
                    "max_number_of_member": 4,
                    "is_matching": True,
                    "level_requirement": ["easy", "medium", "hard"],
                    "team_member_emails": [
                        "test2@gmail.com"
                    ]
                }
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent",
        json=post_data,
        headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Fail to rent stadium_court. No stadium_court data with stadium_court_id = {} or stadium_court is already disabled.".format(post_data["stadium_court_id"])

def test_rent_stadium_court_not_exist_not_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    post_data = {
                    "stadium_court_id": 1,
                    "date": "2023-11-15",
                    "start_time": 20,
                    "end_time": 21,
                    "current_member_number": 2,
                    "max_number_of_member": 4,
                    "is_matching": True,
                    "level_requirement": ["easy", "medium", "hard"],
                    "team_member_emails": [
                        "test2@gmail.com"
                    ]
                }
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent",
        json=post_data,
        # headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_rent_user_not_exist_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    post_data = {
                    "stadium_court_id": 1,
                    "date": "2023-11-15",
                    "start_time": 20,
                    "end_time": 21,
                    "current_member_number": 2,
                    "max_number_of_member": 4,
                    "is_matching": True,
                    "level_requirement": ["easy", "medium", "hard"],
                    "team_member_emails": [
                        "test100@gmail.com"
                    ]
                }
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent",
        json=post_data,
        headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Fail to rent. No user data with email = {}.".format(post_data["team_member_emails"][0])

def test_rent_user_not_exist_not_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    post_data = {
                    "stadium_court_id": 100,
                    "date": "2023-11-15",
                    "start_time": 20,
                    "end_time": 21,
                    "current_member_number": 2,
                    "max_number_of_member": 4,
                    "is_matching": True,
                    "level_requirement": 6,
                    "team_member_emails": [
                        "test100@gmail.com"
                    ]
                }
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/rent",
        json=post_data,
        # headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_join_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    post_data = {
                    "team_id": 11,
                    "team_member_emails": ['test8@gmail.com']
                }
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/join",
        json=post_data,
        headers=get_user_authentication_headers(db_conn, email),
    )
    response_data = response.json()["team"]
    assert response.status_code == 200
    assert response_data["id"] == post_data["team_id"]
    assert response.json()["message"] == "success"
    # delete created data and recover current_member_number of Team
    delete_objs = crud.team_member.get_all_by_team_id(
        db=db_conn, team_id=post_data["team_id"]
    )
    for delete_obj in delete_objs:
        db_conn.delete(delete_obj)
    update_obj = crud.team.get_by_team_id(db=db_conn, team_id=post_data["team_id"])
    update_obj.current_member_number = update_obj.current_member_number-2
    db_conn.add(update_obj)
    db_conn.commit()

def test_join_not_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    post_data = {
                    "team_id": 1,
                    "team_member_emails": ['test5@gmail.com']
                }
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/join",
        json=post_data,
        # headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_join_team_not_exist_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    post_data = {
                    "team_id": 1000,
                    "team_member_emails": ['test8@gmail.com']
                }
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/join",
        json=post_data,
        headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Fail to join. No team data with team_id = {}.".format(post_data["team_id"])

def test_join_team_not_exist_not_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    post_data = {
                    "team_id": 1000,
                    "team_member_emails": ['test8@gmail.com']
                }
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/join",
        json=post_data,
        # headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_join_user_not_exist_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    post_data = {
                    "team_id": 11,
                    "team_member_emails": ['test1000@gmail.com']
                }
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/join",
        json=post_data,
        headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Fail to join. No user data with email = {}.".format(post_data["team_member_emails"][0])

def test_join_user_not_exist_not_logged_in(db_conn, test_client):
    email = "test1@gmail.com"
    post_data = {
                    "team_id": 11,
                    "team_member_emails": ['test1000@gmail.com']
                }
    response = test_client.post(
        f"{settings.API_V1_STR}/stadium-court/join",
        json=post_data,
        # headers=get_user_authentication_headers(db_conn, email),
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"