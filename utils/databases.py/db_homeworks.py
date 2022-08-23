from . import database, GetDoc

from umongo.fields import *
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance as Instance
from umongo.frameworks.motor_asyncio import MotorAsyncIODocument as Document

instance = Instance(database)


@instance.register
class Homework(Document, GetDoc):
    subject = StringField(required=True)
    assignment = StringField(required=True)

    expiration_date = DateTimeField()

    class Meta:
        collection_name = 'Homeworks'
