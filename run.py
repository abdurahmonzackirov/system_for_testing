import os

import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.client import client
from app.admin import admin
from app.database.models import init_models

from dotenv import load_dotenv


async def main():
    load_dotenv()
    
    bot = Bot(token=os.getenv('TOKEN'))
    
    dp = Dispatcher()
    dp.include_routers(admin, client)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    

async def startup(dispatcher: Dispatcher):
    await init_models()
    print('Bot starting up...')

async def shutdown(dispatcher: Dispatcher):
    print('Bot shutting down...')
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')