from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Получить расписание"),
         KeyboardButton(text="🚪 Найти свободные аудитории")],
        [KeyboardButton(text="👩‍💻 Расписание преподавателей")]
    ],
    resize_keyboard=True
)
