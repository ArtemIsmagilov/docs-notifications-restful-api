from motor.motor_asyncio import (
    AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
)

from ..settings import MONGO_URL

client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URL)
db: AsyncIOMotorDatabase = client['artem']
col_users: AsyncIOMotorCollection = db['users']
col_notifications: AsyncIOMotorCollection = db['notifications']


async def ping():
    print(await client.admin.command('ping'))


# Dependency
async def get_db():
    async with await client.start_session() as s:
        async with s.start_transaction():
            yield s
