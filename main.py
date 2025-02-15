import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from database.models import async_main
from handlers.base_handlers import cmd_router
from handlers.quiz_builder import quiz_builder_router
from handlers.quiz_selector import quiz_selector_router

load_dotenv()
TOKEN = os.environ.get("API_TOKEN")


async def main() -> None:
    if TOKEN is None:
        raise ValueError("Please provide a token")
    await async_main()
    dispatcher = Dispatcher()
    dispatcher.include_router(router=cmd_router)
    dispatcher.include_router(router=quiz_builder_router)
    dispatcher.include_router(router=quiz_selector_router)
    if TOKEN is None:
        raise ValueError("Please provide a token")
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    finally:
        logging.shutdown()
