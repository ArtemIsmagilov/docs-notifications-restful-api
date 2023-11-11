import time
from typing import AsyncGenerator
from bson.objectid import ObjectId
from fastapi import HTTPException
from fastapi import status
from motor.motor_asyncio import AsyncIOMotorClientSession

from ..schema import NotificationIn
from ..sql_app.database import col_users, col_notifications


class User:

    @classmethod
    async def get_user(cls, s: AsyncIOMotorClientSession, user_id: str) -> dict:
        return await col_users.find_one({'_id': ObjectId(user_id)}, session=s)


class Notification:

    @classmethod
    async def insert_notification(cls, s: AsyncIOMotorClientSession, n: NotificationIn):
        user = await User.get_user(s, n.user_id)

        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, 'User with user_id=%s doesn\'t exists.' % n.user_id)

        n_doc = n.model_dump(mode='json')
        n_doc.update(timestamp=time.time(), is_new=True)

        result = await col_notifications.insert_one(n_doc, session=s)

        limit_notifications = user['limit_notifications']

        latest_ns_limit = await (
            col_notifications
            .find({'user_id': n.user_id}, session=s).sort('timestamp', -1).limit(limit_notifications)
            .to_list(limit_notifications)
        )

        if len(latest_ns_limit) >= limit_notifications:
            latest_timestamp = latest_ns_limit[-1]['timestamp']
            col_notifications.delete_many({'user_id': n.user_id, 'timestamp': {'$lt': latest_timestamp}}, session=s)

        return result.inserted_id

    @classmethod
    async def list_notifications(
            cls,
            s: AsyncIOMotorClientSession,
            user_id: str,
            skip: int | None = None,
            limit: int | None = None,
    ) -> AsyncGenerator[dict, None]:

        if skip and limit:
            async_generator = col_notifications.find({'user_id': user_id}, session=s).skip(skip).limit(limit)
        elif skip:
            async_generator = col_notifications.find({'user_id': user_id}, session=s).skip(skip)
        elif limit:
            async_generator = col_notifications.find({'user_id': user_id}, session=s).limit(limit)
        else:
            async_generator = col_notifications.find({'user_id': user_id}, session=s)

        async for n_doc in async_generator:
            yield {
                'id': str(n_doc['_id']),
                'user_id': n_doc['user_id'],
                'key': n_doc['key'],
                'target_id': n_doc['target_id'],
                'timestamp': n_doc['timestamp'],
                'is_new': n_doc['is_new'],
                'data': n_doc['data'],
            }

    @classmethod
    async def count_notifications(cls, s: AsyncIOMotorClientSession, user_id: str) -> int:
        result = await col_notifications.count_documents({'user_id': user_id}, session=s)
        return result

    @classmethod
    async def count_new_notifications(cls, s: AsyncIOMotorClientSession, user_id) -> int:
        result = await col_notifications.count_documents({'user_id': user_id, 'is_new': True}, session=s)
        return result

    @classmethod
    async def make_read_notification(cls, s: AsyncIOMotorClientSession, user_id: str, notification_id: str) -> int:
        result = await col_notifications.update_one(
            {'_id': ObjectId(notification_id), 'user_id': user_id}, {"$set": {"is_new": False}}, session=s
        )
        return result.modified_count
