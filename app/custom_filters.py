from aiogram.filters import Filter
from aiogram.types import Message

ADMINS = [6081940975, 583411442, 295612129, 3120828, 764631801]

class AdminProtect(Filter):
    def __init__(self):
        self.admins = ADMINS

    async def __call__(self, message: Message):
        return message.from_user.id in self.admins