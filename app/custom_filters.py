from aiogram.filters import Filter
from aiogram.types import Message
from app.database.models import Admin
import app.database.requests as rq


DEFAULT_ADMINS = [6081940975]

class AdminProtect(Filter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in DEFAULT_ADMINS:
            return True
        admin = await rq.get_admin(message.from_user.id)
        return admin is not None