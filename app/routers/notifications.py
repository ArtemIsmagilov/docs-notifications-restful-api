import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorClientSession
from fastapi import status, HTTPException

from ..dependency import get_object_id
from ..schema import NotificationIn
from ..sql_app.crud import Notification, User
from ..sql_app.database import get_db
from ..worker.tasks import only_send_email

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.post("/create",
             status_code=status.HTTP_201_CREATED,
             responses={
                 201: {
                     "description": "Cоздает новое уведомление",
                     "content": {
                         "application/json": {
                             "example": {
                                 "success": True,
                             }
                         }
                     }
                 }
             })
async def create_notification(
        n: NotificationIn,
        background_tasks: BackgroundTasks,
        session: AsyncIOMotorClientSession = Depends(get_db),
) -> dict:
    """
- user_id - строка на 24 символа (является ObjectID документа пользователя которому отправляется уведомление)
- target_id - строка на 24 символа (является ObjectID документа сущности, к которой относится уведомление) (Может отсутствовать)
- key - ключ уведомления enum
    * registration (Только отправит пользователю Email)
    * new_message (только создаст запись в документе пользователя)
    * new_post (только создаст запись в документе пользователя)
    * new_login (Создаст запись в документе пользователя и отправит email)
- data - произвольный объект из пар ключ/значение (Может отсутствовать)
"""
    user = await User.get_user(session, get_object_id(n.user_id))
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'User with user_id=%s doesn\'t exists.' % n.user_id)

    match n.key:
        case "registration":
            background_tasks.add_task(only_send_email, user['email'])
        case "new_message" | "new_post":
            await Notification.insert_notification(session, n, user)
        case "new_login":
            background_tasks.add_task(only_send_email, user['email'])
            await Notification.insert_notification(session, n, user)
        case _:
            HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    return {
        "success": True,
    }


@router.get("/list", responses={
    200: {
        "description": "Производит листинг уведомлений пользователя",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "data": {
                        "elements": 23,
                        "new": 12,
                        "request": {
                            "user_id": "638f394d4b7243fc0399ea67",
                            "skip": 0,
                            "limit": 10,
                        },
                        "list": [
                            {
                                "id": "some_notification_id",
                                "timestamp": 1698138241,
                                "is_new": False,
                                "user_id": "638f394d4b7243fc0399ea67",
                                "key": "new_message",
                                "target_id": "0399ea67638f394d4b7243fc",
                                "data": {
                                    "some_field": "some_value"
                                },
                            },
                        ]
                    }
                }

            }
        }
    }
})
async def get_list_notifications(
        user_id: str,
        skip: int | None = None,
        limit: int | None = None,
        session: AsyncIOMotorClientSession = Depends(get_db),
) -> dict:
    """
- user_id [string] - идентификатор пользователя
- skip [int] - кол-во уведомлений, которые следует пропустить
- limit [int] - кол-во уведомлений которые следует вернуть
"""
    request = {'user_id': user_id, "skip": skip, 'limit': limit}

    async with asyncio.TaskGroup() as tg:
        elements = tg.create_task(Notification.count_notifications(session, user_id))
        new = tg.create_task(Notification.count_new_notifications(session, user_id))

    n_docs_list = [n_doc async for n_doc in Notification.list_notifications(session, **request)]

    return {
        "success": True,
        "data": {
            "elements": elements.result(),
            "new": new.result(),
            "request": request,
            "list": n_docs_list,
        }
    }


@router.post("/read", responses={
    200: {
        "description": "Cоздает отметку о прочтении уведомления",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                }
            }
        }
    }
})
async def read_notification(
        user_id: str,
        notification_id: str,
        session: AsyncIOMotorClientSession = Depends(get_db)
):
    """
- user_id [string] - идентификатор пользователя
- notification_id [string] - Идентификатор уведомления
"""
    await Notification.make_read_notification(session, user_id, get_object_id(notification_id))
    return {
        "success": True,
    }
