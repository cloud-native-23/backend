import datetime

from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.database import base  # noqa: F401
from app.models.gr_member import GR_Member
from app.models.group import Group
from app.models.matching_room import MatchingRoom
from app.models.mr_liked_hated_member import MR_Liked_Hated_Member
from app.models.mr_member import MR_Member
from app.models.notification import Notification
from app.models.notification_template import NotificationTemplate
from app.models.tag import Tag
from app.models.user import User

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


# init users
def init_user(db: Session):
    init_users = {
        "user_uuid": [
            "397d0336-3df4-4325-a1b3-cc4ef8e8e0ab",
            "2be6b063-8914-42b6-9e8d-1bbe14317cc2",
            "2a3c5a50-a70c-42d2-9689-af8a67423153",
            "70528b75-1ebc-4117-b3dc-c6127264fcff",
        ],
        "email": [
            settings.ADMIN_EMAIL,
            "temp_user1@gmail.com",
            "temp_user2@gmail.com",
            "sdm2023.no2@gmail.com",
        ],
        "name": [settings.ADMIN_NAME, "temp_user1", "temp_user2", "sdm2023"],
        "line_id": ["fakelineid1", "fakelineid3", "fakelineid2", "sdm2023"],
        "is_admin": [True, False, False, True],
        "is_google_sso": [True, True, True, True],
    }
    for i in range(len(init_users["email"])):
        user = crud.user.get_by_email(db, email=init_users["email"][i])
        if not user:
            db_obj = User(
                user_uuid=init_users["user_uuid"][i],
                email=init_users["email"][i],
                name=init_users["name"][i],
                line_id=init_users["line_id"][i],
                is_admin=init_users["is_admin"][i],
                is_google_sso=init_users["is_google_sso"][i],
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)


# init matching room
def init_matching_room(db: Session):
    init_matching_rooms = {
        "room_uuid": [
            "15b14b78-7b33-4274-868f-e3aca152bd80",
            "58102867-1773-4c68-a78f-d6da7124bb2d",
            "6891704b-a2e8-4fce-b971-b3fe3928dfd6",
        ],
        "room_id": ["IR001", "sdm001", "test_matching_room001"],
        "name": ["IR", "sdm", "test_matching_room"],
        "due_time": [
            datetime.datetime.now() - datetime.timedelta(days=1),
            datetime.datetime.now() - datetime.timedelta(days=1),
            datetime.datetime.now() - datetime.timedelta(days=1),
        ],
        "min_member_num": [3, 3, 3],
        "description": [
            "desc of IR001",
            "desc of sdm001",
            "desc of test_matching_room",
        ],
        "is_forced_matching": [False, False, False],
        "created_time": [
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
        ],
        "is_closed": [False, False, False],
        "finish_time": [
            datetime.date(2023, 8, 30),
            datetime.date(2023, 7, 30),
            datetime.date(2023, 6, 30),
        ],
    }
    for i in range(len(init_matching_rooms["room_id"])):
        matching_room = crud.matching_room.get_by_room_id(
            db, room_id=init_matching_rooms["room_id"][i]
        )
        if not matching_room:
            db_obj = MatchingRoom(
                room_uuid=init_matching_rooms["room_uuid"][i],
                name=init_matching_rooms["name"][i],
                room_id=init_matching_rooms["room_id"][i],
                due_time=init_matching_rooms["due_time"][i],
                min_member_num=init_matching_rooms["min_member_num"][i],
                description=init_matching_rooms["description"][i],
                is_forced_matching=init_matching_rooms["is_forced_matching"][i],
                created_time=init_matching_rooms["created_time"][i],
                is_closed=init_matching_rooms["is_closed"][i],
                finish_time=init_matching_rooms["finish_time"][i],
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)


# init mr_member
def init_mr_member(db: Session):
    init_mr_members = {
        "user_uuid": [
            "397d0336-3df4-4325-a1b3-cc4ef8e8e0ab",
            "397d0336-3df4-4325-a1b3-cc4ef8e8e0ab",
            "397d0336-3df4-4325-a1b3-cc4ef8e8e0ab",
            "2be6b063-8914-42b6-9e8d-1bbe14317cc2",
            "2be6b063-8914-42b6-9e8d-1bbe14317cc2",
            "2be6b063-8914-42b6-9e8d-1bbe14317cc2",
            "2a3c5a50-a70c-42d2-9689-af8a67423153",
            "2a3c5a50-a70c-42d2-9689-af8a67423153",
            "2a3c5a50-a70c-42d2-9689-af8a67423153",
            "70528b75-1ebc-4117-b3dc-c6127264fcff",
            "70528b75-1ebc-4117-b3dc-c6127264fcff",
            "70528b75-1ebc-4117-b3dc-c6127264fcff",
        ],
        "room_uuid": [
            "6891704b-a2e8-4fce-b971-b3fe3928dfd6",
            "15b14b78-7b33-4274-868f-e3aca152bd80",
            "58102867-1773-4c68-a78f-d6da7124bb2d",
            "6891704b-a2e8-4fce-b971-b3fe3928dfd6",
            "15b14b78-7b33-4274-868f-e3aca152bd80",
            "58102867-1773-4c68-a78f-d6da7124bb2d",
            "6891704b-a2e8-4fce-b971-b3fe3928dfd6",
            "15b14b78-7b33-4274-868f-e3aca152bd80",
            "58102867-1773-4c68-a78f-d6da7124bb2d",
            "6891704b-a2e8-4fce-b971-b3fe3928dfd6",
            "15b14b78-7b33-4274-868f-e3aca152bd80",
            "58102867-1773-4c68-a78f-d6da7124bb2d",
        ],
        "join_time": [
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
        ],
        "grouped_time": [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ],
        "is_grouped": [
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        ],
        "is_bound": [
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        ],
        "bind_uuid": [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ],
    }
    for i in range(len(init_mr_members["user_uuid"])):
        db_obj = MR_Member(
            user_uuid=init_mr_members["user_uuid"][i],
            room_uuid=init_mr_members["room_uuid"][i],
            join_time=init_mr_members["join_time"][i],
            grouped_time=init_mr_members["grouped_time"][i],
            is_grouped=init_mr_members["is_grouped"][i],
            is_bound=init_mr_members["is_bound"][i],
            bind_uuid=init_mr_members["bind_uuid"][i],
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)


# init group
def init_group(db: Session):
    init_groups = {
        "group_uuid": [
            "47f011f2-cde8-4200-8cee-f6c3ab2524bc",
            "d8b7199c-1dbf-4a01-9c3f-93dd4b02c2b7",
            "fd8bc58a-e77d-4c9a-b2c7-6398c9ecf065",
        ],
        "room_uuid": [
            "6891704b-a2e8-4fce-b971-b3fe3928dfd6",
            "15b14b78-7b33-4274-868f-e3aca152bd80",
            "58102867-1773-4c68-a78f-d6da7124bb2d",
        ],
        "create_time": [
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
        ],
        "group_id": ["test_matching_room-group1", "IR001-group1", "sdm001-group1"],
        "name": ["test_matching_room-group001", "IR-group001", "sdm001-group001"],
    }
    for i in range(len(init_groups["group_uuid"])):
        group = (
            db.query(Group)
            .filter(Group.group_uuid == init_groups["group_uuid"][i])
            .first()
        )
        if not group:
            db_obj = Group(
                group_uuid=init_groups["group_uuid"][i],
                room_uuid=init_groups["room_uuid"][i],
                create_time=init_groups["create_time"][i],
                group_id=init_groups["group_id"][i],
                name=init_groups["name"][i],
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)


# init gr_member
def init_gr_member(db: Session):
    init_gr_members = {
        "member_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "group_uuid": [
            "47f011f2-cde8-4200-8cee-f6c3ab2524bc",
            "d8b7199c-1dbf-4a01-9c3f-93dd4b02c2b7",
            "fd8bc58a-e77d-4c9a-b2c7-6398c9ecf065",
            "47f011f2-cde8-4200-8cee-f6c3ab2524bc",
            "d8b7199c-1dbf-4a01-9c3f-93dd4b02c2b7",
            "fd8bc58a-e77d-4c9a-b2c7-6398c9ecf065",
            "47f011f2-cde8-4200-8cee-f6c3ab2524bc",
            "d8b7199c-1dbf-4a01-9c3f-93dd4b02c2b7",
            "fd8bc58a-e77d-4c9a-b2c7-6398c9ecf065",
            "47f011f2-cde8-4200-8cee-f6c3ab2524bc",
            "d8b7199c-1dbf-4a01-9c3f-93dd4b02c2b7",
            "fd8bc58a-e77d-4c9a-b2c7-6398c9ecf065",
        ],
        "join_time": [
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
            datetime.datetime.now(),
        ],
    }
    for i in range(len(init_gr_members["group_uuid"])):
        member = (
            db.query(GR_Member)
            .filter(GR_Member.member_id == init_gr_members["member_id"][i])
            .first()
        )
        group = (
            db.query(GR_Member)
            .filter(GR_Member.group_uuid == init_gr_members["group_uuid"][i])
            .first()
        )
        if not member or not group:
            db_obj = GR_Member(
                member_id=init_gr_members["member_id"][i],
                group_uuid=init_gr_members["group_uuid"][i],
                join_time=init_gr_members["join_time"][i],
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)


# init notification
def init_notification(db: Session):
    init_notifications = {
        "notification_uuid": [
            "aff39261-cff2-4647-b30e-87362fffe72b",
            "4ed31f73-4058-4a46-b606-164edddbeec3",
        ],
        "receiver_uuid": [
            "397d0336-3df4-4325-a1b3-cc4ef8e8e0ab",
            "70528b75-1ebc-4117-b3dc-c6127264fcff",
        ],
        "sender_uuid": [
            "2a3c5a50-a70c-42d2-9689-af8a67423153",
            "2a3c5a50-a70c-42d2-9689-af8a67423153",
        ],
        "send_time": [datetime.datetime.now(), datetime.datetime.now()],
        "template_uuid": [
            "9c1dc87f-e938-4fa1-9900-9b4ebd5701da",
            "9c1dc87f-e938-4fa1-9900-9b4ebd5701da",
        ],
        "f_string": ["配對活動1", "配對活動1"],
    }
    for i in range(len(init_notifications["notification_uuid"])):
        notification = (
            db.query(Notification)
            .filter(
                Notification.notification_uuid
                == init_notifications["notification_uuid"][i]
            )
            .first()
        )
        if not notification:
            db_obj = Notification(
                notification_uuid=init_notifications["notification_uuid"][i],
                receiver_uuid=init_notifications["receiver_uuid"][i],
                sender_uuid=init_notifications["sender_uuid"][i],
                send_time=init_notifications["send_time"][i],
                template_uuid=init_notifications["template_uuid"][i],
                f_string=init_notifications["f_string"][i],
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)


# init notification template
def init_notification_template(db: Session):
    init_notification_templates = {
        "template_uuid": ["9c1dc87f-e938-4fa1-9900-9b4ebd5701da"],
        "template_id": ["matching_result"],
        "text": ["{0}的配對結果已完成，可於我的群組內查看配對結果"],
    }
    for i in range(len(init_notification_templates["template_uuid"])):
        notification_template = (
            db.query(NotificationTemplate)
            .filter(
                NotificationTemplate.template_uuid
                == init_notification_templates["template_uuid"][i]
            )
            .first()
        )
        if not notification_template:
            db_obj = NotificationTemplate(
                template_uuid=init_notification_templates["template_uuid"][i],
                template_id=init_notification_templates["template_id"][i],
                text=init_notification_templates["text"][i],
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)


# init mr_liked_hated_member
def init_mr_liked_hated_member(db: Session):
    init_mr_liked_hated_members = {
        "member_id": [1, 1, 1, 2, 2, 3],
        "target_member_id": [4, 7, 10, 5, 8, 6],
        "is_liked": [False, True, True, False, False, True],
        "is_hated": [True, False, False, True, True, False],
        "room_uuid": [
            "6891704b-a2e8-4fce-b971-b3fe3928dfd6",
            "6891704b-a2e8-4fce-b971-b3fe3928dfd6",
            "6891704b-a2e8-4fce-b971-b3fe3928dfd6",
            "15b14b78-7b33-4274-868f-e3aca152bd80",
            "15b14b78-7b33-4274-868f-e3aca152bd80",
            "58102867-1773-4c68-a78f-d6da7124bb2d",
        ],
    }
    for i in range(len(init_mr_liked_hated_members["member_id"])):
        member = (
            db.query(MR_Liked_Hated_Member)
            .filter(
                MR_Liked_Hated_Member.member_id
                == init_mr_liked_hated_members["member_id"][i]
            )
            .first()
        )
        target_member = (
            db.query(MR_Liked_Hated_Member)
            .filter(
                MR_Liked_Hated_Member.target_member_id
                == init_mr_liked_hated_members["target_member_id"][i]
            )
            .first()
        )
        room = (
            db.query(MR_Liked_Hated_Member)
            .filter(
                MR_Liked_Hated_Member.room_uuid
                == init_mr_liked_hated_members["room_uuid"][i]
            )
            .first()
        )
        if not member or not target_member or not room:
            db_obj = MR_Liked_Hated_Member(
                member_id=init_mr_liked_hated_members["member_id"][i],
                target_member_id=init_mr_liked_hated_members["target_member_id"][i],
                is_liked=init_mr_liked_hated_members["is_liked"][i],
                is_hated=init_mr_liked_hated_members["is_hated"][i],
                room_uuid=init_mr_liked_hated_members["room_uuid"][i],
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)


# init tag
def init_tag(db: Session):
    init_tag = {
        "tag_uuid": [
            "10eaae67-9ca5-4a5a-affd-90504479cc5e",
            "8f31d735-360e-4704-b832-15c1daacd541",
            "8308f3e1-d32a-4801-bd0d-6dcdb6ec5aed",
            "008bccc5-b0a8-4962-8793-9b1105b50de0",
            "193b2cc1-8a0a-4c4f-8a65-7f941aef0d82",
        ],
        "tag_text": [
            "TAG1",
            "TAG2",
            "TAG3",
            "TAG4",
            "TAG5",
        ],
        "room_uuid": [
            "15b14b78-7b33-4274-868f-e3aca152bd80",
            "15b14b78-7b33-4274-868f-e3aca152bd80",
            "15b14b78-7b33-4274-868f-e3aca152bd80",
            "15b14b78-7b33-4274-868f-e3aca152bd80",
            "15b14b78-7b33-4274-868f-e3aca152bd80",
        ],
        "mentioned_num": [
            5,
            4,
            3,
            2,
            1,
        ],
    }
    for i in range(len(init_tag["tag_uuid"])):
        tag = db.query(Tag).filter(Tag.tag_uuid == init_tag["tag_uuid"][i]).first()
        if not tag:
            db_obj = Tag(
                tag_uuid=init_tag["tag_uuid"][i],
                tag_text=init_tag["tag_text"][i],
                room_uuid=init_tag["room_uuid"][i],
                mentioned_num=init_tag["mentioned_num"][i],
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)


def test_init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    # init user
    init_user(db)

    # init matching room
    init_matching_room(db)

    # init mr member
    init_mr_member(db)

    # init group
    init_group(db)

    # init gr_member
    init_gr_member(db)

    # init notification
    init_notification(db)

    # init notificationteplate
    init_notification_template(db)

    # init mr_liked_hated_member
    init_mr_liked_hated_member(db)

    # init tag
    init_tag(db)
