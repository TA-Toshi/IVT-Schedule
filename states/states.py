from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    select_group = State()
    select_day = State()
    select_lesson = State()
    select_teacher = State()
    check_namesake = State()
    group_match = State()
    sub = State()
    unsub = State()
