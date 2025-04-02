from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Получить расписание"),
         KeyboardButton(text="🚪 Найти свободные аудитории")],
    ],
    resize_keyboard=True
)
