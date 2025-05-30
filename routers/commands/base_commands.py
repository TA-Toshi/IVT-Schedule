from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from gs.db import add_to_db, del_from_db, get_groups_by_user_id, del_all_from_db
from gs.gs_api import get_groups, group_match
from keybords.reply_keyboards import main_keyboard
from states.states import Form

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
    await message.answer(text=(""
                               "🎓 *Инструкция по использованию бота*\n\n"

                               "📅 *Расписание группы:*\n"
                               "1. Выбери «Получить расписание»\n"
                               "2. Укажи название группы\n"
                               "3. Выбери день недели\n\n"

                               "🚪 *Свободные аудитории:*\n"
                               "1. Нажми «Найти свободные аудитории»\n"
                               "2. Укажи день недели\n"
                               "3. Выбери номер пары\n\n"

                               "👩🏫 *Расписание преподавателя:*\n"
                               "1. Выбери «Расписание преподавателей»\n"
                               "2. Введи ФИО (например: *Иванов А.А.*)\n"
                               "3. Укажи день недели\n\n"

                               "🔔 *Подписка на обновления:*\n"
                               "1. Введи `/sub [группа]` (пример: `/sub ИВТ-11`)\n"
                               "2. *Важно:* название группы строго по шаблону\n\n"

                               "🔕 *Отмена подписки:*\n"
                               "1. Введи `/unsub`\n"
                               "2. Выбери группу из списка")
                         )


@router.message(Command("sub"))
async def cmd_sub(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Укажите группу для подписки")
    await state.set_state(Form.pre_sub)


@router.message(Command("unsub"))
async def cmd_unsub(message: types.Message, state: FSMContext):
    await state.clear()
    subs = await get_groups_by_user_id(message.from_user.id)
    try:
        if subs:
            keyboard = []
            for i in range(0, len(subs), 2):
                row = subs[i:i + 2]
                keyboard_row = [
                    InlineKeyboardButton(text=name, callback_data=name)
                    for name in row
                ]
                keyboard.append(keyboard_row)
            keyboard.append([
                InlineKeyboardButton(text="Все", callback_data="all")
            ])
            await message.answer(
                text="От кого выхотите отписаться?",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
            await state.set_state(Form.unsub)
        else:
            raise Exception("Список пуст")
    except Exception as e:
        await message.answer(
            text=f"❌ У вас нет подписок")
        await state.clear()


@router.message(Form.pre_sub)
async def ft_cmd_sub(message: types.Message, state: FSMContext):
    try:
        match = group_match(message.text)
        if len(match) > 1:
            keyboard = []
            for i in range(0, len(match), 2):
                row = match[i:i + 2]
                keyboard_row = [
                    InlineKeyboardButton(text=name, callback_data=name)
                    for name in row
                ]
                keyboard.append(keyboard_row)
            await message.answer(
                text="Уточните группу",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
            await state.set_state(Form.sub)
        elif len(match) == 1:
            await add_to_db(message.from_user.id, match[0])
            await message.answer(text=f"Подписка на обновления гуппы - {match[0]}")
            await state.clear()
        else:
            raise Exception("Группы нет в списке")
    except Exception as e:
        await message.answer(
            text=f"❌ Произошла ошибка. Проверьте название группы\nи введите команду заново:")
        await state.set_state(Form.pre_sub)


@router.callback_query(Form.sub)
async def match_sub(callback: types.CallbackQuery, state: FSMContext):
    group = callback.data
    await add_to_db(callback.from_user.id, group)
    await callback.message.edit_text(text=f"Подписка на обновления группы - {group}")
    await state.clear()


@router.callback_query(Form.unsub)
async def match_unsub(callback: types.CallbackQuery, state: FSMContext):
    group = callback.data
    if group == "all":
        await del_all_from_db(callback.from_user.id)
        await callback.message.edit_text(text=f"Вы отписались от всех групп")
        await state.clear()
    else:
        await del_from_db(callback.from_user.id, group)
        await callback.message.edit_text(text=f"Вы отписались от {group}")
        await state.clear()
