import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers.start import router as start_router
from handlers.admin import router as admin_router
from database import init_db
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")  # یا مستقیم بنویس '123:abc'

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # ثبت handlerها
    dp.include_router(start_router)
    dp.include_router(admin_router)

    # راه‌اندازی دیتابیس
    await init_db()

    print("بات شروع شد...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())