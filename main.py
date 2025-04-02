import asyncio
import logging

from aiogram import Bot, Dispatcher
from routers.commands.base_commands import router as base_command_router
from routers.scripts.base_scripts import router as base_script_router

import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

dp.include_router(base_command_router)
dp.include_router(base_script_router)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
