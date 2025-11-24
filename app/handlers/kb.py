from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
)
from aiogram.utils.keyboard import KeyboardBuilder, InlineKeyboardBuilder

section = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Добавить день рождения", callback_data="add")],
        [
            InlineKeyboardButton(
                text="Удалить день рождения", callback_data="delete_menu"
            )
        ],
        [InlineKeyboardButton(text="Показать дни рождения", callback_data="show")],
    ]
)

exit = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Выйти", callback_data="exit")],
    ]
)


def get_people_keyboard(people):
    """ "Создать клавиатуру из людей"""
    builder = InlineKeyboardBuilder()

    for person in people:
        date_str = person.date_birth.strftime("%d/%m/%Y")
        button_text = f"{person.name} {date_str}"

        builder.button(text=button_text, callback_data=f"delete_{person.id}")

    builder.adjust(1)
    return builder.as_markup()
