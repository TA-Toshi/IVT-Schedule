from aiogram import Router, types
from aiogram.filters import Command, CommandObject

from gs.db import add_to_db, del_from_db
from gs.gs_api import get_groups
from keybords.reply_keyboards import main_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        text=f"Привет, {message.from_user.full_name}!\n"
             "Я помогу тебе с расписанием занятий!\n"
             "Выбери действие:",
        reply_markup=main_keyboard
    )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(text=""
                              "❓ Как пользоваться ботом:\n\n"
                              "\n"
                              "📅 Чтобы получить расписание:\n"
                              "\n"
                              "1. Нажми «Получить расписание»\n"
                              "2. Введи название группы\n"
                              "3. Выбери день недели\n\n"
                              "\n"
                              "🚪 Чтобы найти свободные аудитории:\n"
                              "\n"
                              "1. Нажми «Найти свободные аудитории»\n"
                              "2. Выбери день недели\n"
                              "3. Выбери номер пары"
                              "\n"
                              "👩‍💻 Чтобы узнать расписание преподавателя:\n"
                              "\n"
                              "1. Нажми «Расписание преподавателей»\n"
                              "2. Введи ФИО преподавателя\n"
                              "3. Выбери день недели\n\n"
                              "\n"
                              "👍 Чтобы подписаться на обновления в расписании:\n"
                              "\n"
                              "1. Введи /sub <название группы>\n"
                              "2. Важно указать точное название группы без '<>'\n"
                              "\n"
                              "👎 Чтобы отписаться от обновлений в расписании:\n"
                              "\n"
                              "1. Введи /unsub <название группы>\n"
                              "2. Важно указать точное название группы без '<>'\n"
                              "\n"
                         )


@router.message(Command("sub"))
async def cmd_sub(message: types.Message, command: CommandObject):
    if command.args not in get_groups():
        await message.answer(text="❌ Произошла ошибка. Проверь название группы")
    else:
        await add_to_db(message.from_user.id, command.args)
        await message.answer(text=f"{command.args}")


@router.message(Command("unsub"))
async def cmd_sub(message: types.Message, command: CommandObject):
    if command.args not in get_groups():
        await message.answer(text="❌ Произошла ошибка. Проверь название группы")
    else:
        await del_from_db(message.from_user.id, command.args)
        await message.answer(text=f"{command.args}")
