import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN
from db import connect_db
from user_handlers import user_router
from admin_handlers import admin_router

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(user_router)
    dp.include_router(admin_router)
    await connect_db()
    try:
        await dp.start_polling(bot)
    except Exception:
        logging.exception("Bot polling failed")
        raise
    finally:
        print("Shutting down bot...")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
