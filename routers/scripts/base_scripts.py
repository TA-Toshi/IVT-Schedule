from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from gs.db import get_groups_by_user_id
from keybords.inline_keyboards import days_keyboard, lessons_keyboard, week_keyboard, teachers_days_keyboard
from gs.gs_api import get_by_day, get_by_group, get_free_classroom, get_by_teacher, get_teacher_by_day, \
    check_namesake, group_match, process_schedule
from states.states import Form

router = Router()


@router.message(F.text == "📅 Получить расписание")
async def start_schedule(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("📝 Введи название своей группы"
                         "\nНапример ИВТ-13БО:")
    await state.set_state(Form.select_group)


@router.message(F.text == "🚪 Найти свободные аудитории")
async def start_free_classrooms(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("📅 Выбери день недели:", reply_markup=days_keyboard)
    await state.set_state(Form.select_day)


@router.message(F.text == "👩‍💻 Расписание преподавателей")
async def start_teacher(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("📝 Введите ФИО преподавателя"
                         "\nНапример Иванов И.И. или просто фамилию:")
    await state.set_state(Form.select_teacher)


@router.message(F.text == "Подписки")
async def subs_list(message: types.Message, state: FSMContext):
    keyboard = []
    subs = await get_groups_by_user_id(message.from_user.id)
    if subs:
        for i in range(0, len(subs), 2):
            row = subs[i:i + 2]
            keyboard_row = [
                InlineKeyboardButton(text=name, callback_data=name)
                for name in row
            ]
            keyboard.append(keyboard_row)
        await message.answer(
            text="Подписки",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await state.set_state(Form.group_match)
    else:
        await message.answer(text=f"Нет подписок")
        await state.clear()


@router.message(Form.select_group)
async def process_group(message: types.Message, state: FSMContext):
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
                text="Для точного поиска, уточните группу",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
            await state.set_state(Form.group_match)
        elif len(match) == 1:
            await state.update_data(group=match[0])
            await message.answer("📅 Теперь выбери день недели:", reply_markup=week_keyboard)
            await state.set_state(Form.select_day)
        else:
            raise Exception("Группы нет в списке")
    except Exception as e:
        await message.answer(
            text="❌ Произошла ошибка. Проверьте название группы\nи введите заново:")
        await state.set_state(Form.select_group)


@router.callback_query(Form.group_match)
async def match_days(callback: types.CallbackQuery, state: FSMContext):
    group = callback.data
    await state.update_data(group=group)
    await callback.message.edit_text("📅 Теперь выбери день недели:", reply_markup=week_keyboard)
    await state.set_state(Form.select_day)


@router.callback_query(F.data.startswith("week_"), Form.select_day)
async def process_day(callback: types.CallbackQuery, state: FSMContext):
    day = callback.data.split("_")[1]
    data = await state.get_data()

    try:
        if day == "неделя":
            schedule = get_by_group(data['group'])
        else:
            schedule = get_by_day(data['group'], day)
        response = f"📅 Расписание для {data['group']} ({day.capitalize()}):\n\n"
        for item in schedule:
            if type(item) is str:
                response += f"- {item}:\n\n"
            else:
                if item[0][1] or (item[0][1] == "" and item[1] != "full"):
                    check = item[0][1]
                    if item[0][1] == "":
                        check = "нет пар"
                    if item[1] == "first":
                        response += "--------------\n"
                        response += f"⏰ <b>{item[0][0]}/Числитель</b>: {check}\n\n"
                    elif item[1] == "second":
                        response += f"⏰ <b>{item[0][0]}/Знаменатель</b>: {check}\n"
                        response += "--------------\n"
                    else:
                        response += f"⏰ <b>{item[0][0]}</b>: {item[0][1]}\n\n"
        response = process_schedule(response)
        await callback.message.edit_text(text=response, parse_mode="HTML")
        await state.clear()

    except Exception as e:
        print(e)
        await callback.message.edit_text(
            text="❌ Произошла ошибка. Проверь название группы\nи введите заново:")
        await state.set_state(Form.select_group)


@router.callback_query(F.data.startswith("day_"), Form.select_day)
async def process_free_day(callback: types.CallbackQuery, state: FSMContext):
    day = callback.data.split("_")[1]
    await state.update_data(day=day)
    await callback.message.edit_text("🔢 Выбери номер пары:", reply_markup=lessons_keyboard)
    await state.set_state(Form.select_lesson)


@router.callback_query(F.data.startswith("lesson_"), Form.select_lesson)
async def process_lesson(callback: types.CallbackQuery, state: FSMContext):
    lesson_number = int(callback.data.split("_")[1])
    data = await state.get_data()

    try:
        time, free_rooms = get_free_classroom(data['day'], lesson_number)
        response = (
            f"🚪 Свободные аудитории:\n"
            f"📅 День: {data['day'].capitalize()}\n"
            f"⏰ Время: {time}\n\n"
        )

        for room in free_rooms:
            response += f"🔑 Ауд. {room[0]}\n"
            if room[1]:
                response += f"Информация:\n{room[1]}\n\n"
            else:
                response += f"Информация отсутствует\n\n"

        await callback.message.edit_text(response)
        await state.clear()

    except Exception as e:
        await callback.message.edit_text("❌❌❌ Произошла ошибка. Попробуй еще раз")
        await state.clear()


@router.message(Form.select_teacher)
async def check_ns(message: types.Message, state: FSMContext):
    try:
        teacher_namesake = check_namesake(message.text)
        if len(teacher_namesake) > 1:
            keyboard = []
            for name in teacher_namesake:
                keyboard.append([InlineKeyboardButton(
                    text=name,
                    callback_data=name
                )])
            await message.answer(
                text="Для точного поиска, укажите полное ФИО преподавателя",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
            await state.set_state(Form.check_namesake)
        elif len(teacher_namesake) == 1:
            await state.update_data(teacher=teacher_namesake[0])
            await message.answer("📅 Теперь выбери день недели:", reply_markup=teachers_days_keyboard)
            await state.set_state(Form.select_day)
        else:
            raise Exception("Фамилии нет в списке")
    except Exception as e:
        print(e)
        await message.answer(
            text="❌ Произошла ошибка. Проверь ФИО\nи введите заново:")
        await state.set_state(Form.select_teacher)


@router.callback_query(Form.check_namesake)
async def process_teacher(callback: types.CallbackQuery, state: FSMContext):
    teacher = callback.data
    await state.update_data(teacher=teacher)
    await callback.message.edit_text("📅 Теперь выбери день недели:", reply_markup=teachers_days_keyboard)
    await state.set_state(Form.select_day)


@router.callback_query(F.data.startswith("teach_"), Form.select_day)
async def process_teacher_day(callback: types.CallbackQuery, state: FSMContext):
    day = callback.data.split("_")[1]
    data = await state.get_data()

    try:
        if day == "неделя":
            schedule = get_by_teacher(data['teacher'])
        else:
            schedule = get_teacher_by_day(data['teacher'], day)
        response = f"📅 Расписание для {data['teacher']} ({day.capitalize()}):\n\n"

        for item in schedule:
            if type(item) is str:
                response += f"- {item}:\n\n"
            else:
                if item[0][1] or (item[0][1] == "" and item[1] != "full"):
                    check = item[0][1]
                    if item[0][1] == "":
                        check = "нет пар"
                    if item[1] == "first":
                        response += "--------------\n"
                        response += f"⏰ <b>{item[0][0]}/Числитель</b>: {check}\n\n"
                    elif item[1] == "second":
                        response += f"⏰ <b>{item[0][0]}/Знаменатель</b>: {check}\n"
                        response += "--------------\n"
                    else:
                        response += f"⏰ <b>{item[0][0]}</b>: {item[0][1]}\n\n"
        response = process_schedule(response)
        await callback.message.edit_text(text=response, parse_mode="HTML")
        await state.clear()

    except Exception as e:
        print(e)
        await callback.message.edit_text(
            text="❌ Произошла ошибка. Проверь ФИО\nи введите заново:")
        await state.set_state(Form.select_teacher)


@router.callback_query(F.data.startswith("cancel"))
async def cancel(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(f"Действие отменено")
    await state.clear()
