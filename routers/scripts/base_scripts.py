import re

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keybords.inline_keyboards import days_keyboard, lessons_keyboard, week_keyboard, teachers_days_keyboard, \
    cancel_keyboard
from gs.gs_api import get_by_day, get_by_group, get_free_classroom, get_by_teacher, get_teacher_by_day, \
    check_colon_with_spaces

router = Router()


class Form(StatesGroup):
    select_group = State()
    select_day = State()
    select_lesson = State()
    select_teacher = State()


@router.message(F.text == "📅 Получить расписание")
async def start_schedule(message: types.Message, state: FSMContext):
    await message.answer("📝 Введи название своей группы"
                         "\nНапиример ИВТ-13БО:")
    await state.set_state(Form.select_group)


@router.message(Form.select_group)
async def process_group(message: types.Message, state: FSMContext):
    await state.update_data(group=message.text, id=message.from_user.id)
    await message.answer("📅 Теперь выбери день недели:", reply_markup=week_keyboard)
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
                # if not re.search(r':[^-]*-', response):
                #     response += "ПАР НЕТ\n"
                response += f"{item}:\n\n"
            else:
                if item[0][1] or (item[0][1] == "" and item[1] != "full"):
                    if item[1] == "first":
                        response += "--------------\n"
                        response += f"⏰ <b>{item[0][0]}/Числитель</b>: {item[0][1]} - <b>Числитель</b>\n\n"
                    elif item[1] == "second":
                        response += f"⏰ <b>{item[0][0]}/Знаменатель</b>: {item[0][1]} - <b>Знаменатель</b>\n"
                        response += "--------------\n"
                    else:
                        response += f"⏰ <b>{item[0][0]}</b>: {item[0][1]}\n\n"
            if check_colon_with_spaces(response):
                response += "ПАР НЕТ"

        await callback.message.edit_text(text=response, parse_mode="HTML")
        await state.clear()

    except Exception as e:
        await callback.message.edit_text(
            text="❌ Произошла ошибка. Проверь название группы\nи введите заново:",
            reply_markup=cancel_keyboard)
        await state.set_state(Form.select_group)


@router.message(F.text == "🚪 Найти свободные аудитории")
async def start_free_classrooms(message: types.Message, state: FSMContext):
    await message.answer("📅 Выбери день недели:", reply_markup=days_keyboard)
    await state.set_state(Form.select_day)


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


@router.message(F.text == "👩‍💻 Расписание преподавателей")
async def start_teacher(message: types.Message, state: FSMContext):
    await message.answer("📝 Введите ФИО преподавателя"
                         "\nНапиример Иванов И.И. или просто фамилию:")
    await state.set_state(Form.select_teacher)


@router.message(Form.select_teacher)
async def process_teacher(message: types.Message, state: FSMContext):
    await state.update_data(teacher=message.text, id=message.from_user.id)
    await message.answer("📅 Теперь выбери день недели:", reply_markup=teachers_days_keyboard)
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
                # if not re.search(r':[^-]*-', response):
                #     response += "ПАР НЕТ\n"
                response += f"- {item}:\n\n"
            else:
                if item[0][1] or (item[0][1] == "" and item[1] != "full"):
                    if item[1] == "first":
                        response += "--------------\n"
                        response += f"⏰ <b>{item[0][0]}/Числитель</b>: {item[0][1]} - <b>Числитель</b>\n\n"
                    elif item[1] == "second":
                        response += f"⏰ <b>{item[0][0]}/Знаменатель</b>: {item[0][1]} - <b>Знаменатель</b>\n"
                        response += "--------------\n"
                    else:
                        response += f"⏰ <b>{item[0][0]}</b>: {item[0][1]}\n\n"
            if check_colon_with_spaces(response):
                response += "ПАР НЕТ"

        await callback.message.edit_text(text=response, parse_mode="HTML")
        await state.clear()

    except Exception as e:
        await callback.message.edit_text(
            text="❌ Произошла ошибка. Проверь ФИО\nи введите заново:",
            reply_markup=cancel_keyboard)
        await state.set_state(Form.select_teacher)


@router.callback_query(F.data.startswith("cancel"))
async def cancel(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(f"Действие отменено")
    await state.clear()
