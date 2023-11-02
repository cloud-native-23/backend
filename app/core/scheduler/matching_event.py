import asyncio
import atexit
import json

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import HTTPException
from loguru import logger
from sqlalchemy import event
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database.session import SessionLocal
from app.models.matching_room import MatchingRoom
from app.notifier import notify

"""
Matching event scheduler
"""
scheduler = BackgroundScheduler()
scheduler.start()


async def matching_event(db: Session, matching_room: MatchingRoom):
    logger.info("call matching_event service in scheduler")

    if matching_room.is_closed:
        raise HTTPException(
            status_code=400,
            detail="Matching room is already closed.",
        )
    """
    Call matching event micro-service
    """
    url = "http://matching:8001/matching/create"
    payload = json.dumps(
        {
            "room_id": matching_room.room_id,
            "group_choice": "random",
            "slot_choice": "fixed_min",
            "params": {
                # "num_groups": 3,
                # "max_users": 6,
                "min_users": matching_room.min_member_num
            },
        }
    )
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=payload)

    # return
    if response.status_code == 200:
        # Close matching room
        matching_room = crud.matching_room.close_by_room_id(
            db=db, room_id=matching_room.room_id
        )

        """
        Create Group and GR_Member
        """
        result = json.loads(response.text)["groups"]

        # Get notify template_uuid
        notification_template = crud.notification_template.get_by_template_id(
            db=db, template_id="matching_result"
        )

        group_list = []
        group_id = 0
        for group in result:
            # Create Group
            group_id += 1
            new_group_schema = schemas.GroupCreate(
                name=matching_room.name + "_" + str(group_id),
                group_id=matching_room.room_id + "_" + str(group_id),
                room_uuid=matching_room.room_uuid,
            )
            new_group = crud.group.create(db=db, obj_in=new_group_schema)

            gr_mem_list = []
            for gr_member in result[group]:
                # Create GR_member
                new_gr_mem_schema = schemas.GR_MemberCreate(
                    member_id=gr_member,
                    group_uuid=new_group.group_uuid,
                    join_time=new_group.create_time,
                )
                new_gr_mem = crud.gr_member.create(db=db, obj_in=new_gr_mem_schema)

                """
                Call notification method for every Group Member
                """
                gr_user = crud.mr_member.get_by_member_id(
                    db=db, member_id=new_gr_mem.member_id
                )
                gr_mem_list.append(gr_user.member_id)
                # logger.info(gr_user)
                # Create notify send object
                notification_send_object = (
                    schemas.NotificationSendObjectModelWithGroupID(
                        receiver_uuid=gr_user.user_uuid,
                        template_uuid=notification_template.template_uuid,
                        f_string=matching_room.name,
                        group_id=new_group.group_id,
                    )
                )
                await notify(db, notification_send_object)
            group_list.append(gr_mem_list)
        return {"message": "success", "data": group_list}

    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=json.loads(response.text)["detail"],
        )


def schedule_matching_event(matching_room: MatchingRoom, db: Session = SessionLocal()):
    if scheduler.running:
        logger.info("scheduler running")

    scheduler.add_job(
        lambda: asyncio.run(matching_event(db, matching_room)),
        "date",
        run_date=matching_room.due_time,
    )

    return


@event.listens_for(MatchingRoom, "after_insert")
def schedule_matching_room(mapper, connection, matching_room):
    "listen for the 'after_insert' event"
    schedule_matching_event(matching_room=matching_room)


@atexit.register
def shutdown_scheduler():
    scheduler.shutdown()
