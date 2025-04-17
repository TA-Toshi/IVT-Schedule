import asyncio
import logging

from aiogram import Bot, Dispatcher

from gs.db import get_all_users
from gs.gs_api import check_spreadsheet_changes
from routers.commands.base_commands import router as base_command_router
from routers.scripts.base_scripts import router as base_script_router

import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

dp.include_router(base_command_router)
dp.include_router(base_script_router)


async def send_notifications(upds):
    users = await get_all_users()
    upd_group = set()
    for upd in upds:
        upd_group.add(upd[3])
    message = "Обнаружены изменения в расписании\n"
    message += "\n"
    message += f"{upd[3]} ({upd[-1]})\n"
    message += f"{upd[-2]}\n"
    message += f"{upd[2]}\n"

    for chat_id, group in users:
        if group in upd_group:
            message = "🔔 Внимание! Изменения в расписании! 🔔\n"
            for upd in upds:
                if group == upd[3] and upd[2] not in message:
                    message += "\n"
                    message += f"{upd[3]} ({upd[-1]})\n"
                    message += f"🕘 {upd[-2]}\n"
                    message += f"📚 {upd[2]}\n"

            try:
                await bot.send_message(chat_id, message)
            except Exception as e:
                print(f"Ошибка отправки сообщения {chat_id}: {e}")


async def periodic_check():
    while True:
        await asyncio.sleep(10)
        changes = check_spreadsheet_changes()
        if changes:
            await send_notifications(changes)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await asyncio.gather(
        dp.start_polling(bot),
        periodic_check()
    )


if __name__ == "__main__":
    asyncio.run(main())
