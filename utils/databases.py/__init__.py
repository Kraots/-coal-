import os
import motor.motor_asyncio

key = os.getenv('MONGODBKEY')
cluster = motor.motor_asyncio.AsyncIOMotorClient(key)
database = cluster['Școală']


class GetDoc:
    @classmethod
    async def get(cls, id=938097236024360960):
        """|coro|
        This method is a shortcut for ``await .find_one({'_id': id})``
        If the ``id`` isn't given, then it will use the owner's id by default (938097236024360960)
        """

        return await cls.find_one({'_id': id})


__all__ = (

)
