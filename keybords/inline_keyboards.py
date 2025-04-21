from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

week_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Понедельник", callback_data="week_понедельник"),
         InlineKeyboardButton(text="Вторник", callback_data="week_вторник")],
        [InlineKeyboardButton(text="Среда", callback_data="week_среда"),
         InlineKeyboardButton(text="Четверг", callback_data="week_четверг")],
        [InlineKeyboardButton(text="Пятница", callback_data="week_пятница"),
         InlineKeyboardButton(text="Суббота", callback_data="week_суббота")],
        [InlineKeyboardButton(text="Вся Неделя", callback_data="week_неделя")]
    ]
)
lessons_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=str(i), callback_data=f"lesson_{i}") for i in range(1, 6)]
    ]
)

days_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Понедельник", callback_data="day_понедельник"),
         InlineKeyboardButton(text="Вторник", callback_data="day_вторник")],
        [InlineKeyboardButton(text="Среда", callback_data="day_среда"),
         InlineKeyboardButton(text="Четверг", callback_data="day_четверг")],
        [InlineKeyboardButton(text="Пятница", callback_data="day_пятница"),
         InlineKeyboardButton(text="Суббота", callback_data="day_суббота")],
    ]
)


teachers_days_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Понедельник", callback_data="teach_понедельник"),
         InlineKeyboardButton(text="Вторник", callback_data="teach_вторник")],
        [InlineKeyboardButton(text="Среда", callback_data="teach_среда"),
         InlineKeyboardButton(text="Четверг", callback_data="teach_четверг")],
        [InlineKeyboardButton(text="Пятница", callback_data="teach_пятница"),
         InlineKeyboardButton(text="Суббота", callback_data="teach_суббота")],
        [InlineKeyboardButton(text="Вся Неделя", callback_data="teach_неделя")]
    ]
)