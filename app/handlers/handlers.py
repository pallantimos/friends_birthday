from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from aiohttp import request
from pydantic import ValidationError

from app.database.request import get_person_by_id, delete_person
from app.handlers import kb
from app.database.models import async_main
from app.handlers.states import Add, Show
from app.database import request as db


router = Router()


@router.message(Command("help"))
async def help_command(message: Message):
    """ "Логика работы /help"""
    help_text = """
<b>Доступные команды:</b>

/start - Начать работу с ботом
/help - Получить справку по командам
/add - Добавить друга в список
/list - Показать всех друзей
/birthdays - Ближайшие дни рождения

<b>Особенности:</b>
• Бот автоматически напоминает о днях рождения
• Уведомления приходят в 9:00
• Напоминает за 3 дня до события

<b>Как пользоваться:</b>
1. Добавьте друзей командой /add
2. Бот будет автоматически отслеживать дни рождения
3. Получайте уведомления заранее
"""
    await message.answer(help_text, parse_mode="HTML")


@router.message(CommandStart())
async def start(message: Message):
    """ "Логика команды /start"""
    await async_main()
    await message.answer(text=f"Привет", reply_markup=kb.section)


@router.callback_query(F.data == "exit")
async def back(callback_query: CallbackQuery, state: FSMContext):
    """ "Логика кнопки 'Выйти'"""
    await state.clear()
    await callback_query.message.answer(
        "Что ты хочешь сделать?", reply_markup=kb.section
    )
    await callback_query.answer()


@router.message(Command("add"))
@router.callback_query(StateFilter(None), F.data == "add")
async def add_handler(event: Message | CallbackQuery, state: FSMContext):
    """ "Логика команды /add и кнопки Добавить день рождения"""
    await state.set_state(Add.name)

    if isinstance(event, Message):
        await event.answer("Введите имя человека", reply_markup=kb.exit)
    else:
        await event.message.answer("Введите имя человека", reply_markup=kb.exit)
        await event.answer()


@router.message(Command("list"))
@router.callback_query(StateFilter(None), F.data == "show")
async def show_list(event: Message | CallbackQuery, state: FSMContext):
    """ "Логика команды /list и кнопки 'Показать дни рождения'"""
    if isinstance(event, Message):
        user_id = event.from_user.id
        message_func = event.answer
        is_callback = False
    else:
        user_id = event.from_user.id
        message_func = event.message.edit_text
        is_callback = True
        await event.answer()

    people_birthdays = await db.get_birthday(user_id)

    if not people_birthdays:
        await message_func("У вас нет записанных дат", reply_markup=kb.exit)
        return

    show_birthday = "Список дней рождения:\n\n"
    for person in people_birthdays:
        show_birthday += f"{person.name} - {person.date_birth.strftime('%d.%m.%Y')}\n"

    full_text = show_birthday + "\nПоказаны все записанные даты"

    await message_func(full_text, reply_markup=kb.exit)


@router.message(Add.name)
async def add_name(message: Message, state: FSMContext):
    """ "Ввод даты рождения"""
    try:
        await state.update_data(name=message.text)
        await state.set_state(Add.date_birth)
        await message.answer(
            "Введите дату рождения в формате dd:mm:yyyy", reply_markup=kb.exit
        )
    except ValueError:
        await message.answer("Я вас не понял")


@router.message(Add.date_birth)
async def add_date_birth(message: Message, state: FSMContext):
    """ "Добавление введенных данных в базу"""
    result = ""
    await state.update_data(date_birth=message.text)
    data = await state.get_data()

    result = await db.add(user_id=message.from_user.id, data=data)
    await message.answer(result, reply_markup=kb.section)
    await state.clear()


@router.callback_query(F.data == "delete_menu")
async def delete_menu(query: CallbackQuery, state: FSMContext):
    """ "Логика кнопки 'Удалить день рождения'"""
    people = await db.get_birthday(query.from_user.id)

    if not people:
        await query.message.answer("У вас нет записанных дат")
        return

    await query.message.edit_text(
        "Выберите дату для удаления:", reply_markup=kb.get_people_keyboard(people)
    )

    await query.answer()


@router.callback_query(F.data.startswith("delete_"))
async def delete_person_handler(callback: CallbackQuery):
    """Обработчик удаления конкретного человека"""
    person_id = int(callback.data.split("_")[1])

    person = await get_person_by_id(person_id)
    name = person[0].name

    if not person:
        await callback.answer("❌ Друг не найден!", show_alert=True)
        return

    success = await delete_person(person_id)

    if success:
        await callback.message.edit_text(
            f"✅ {name} удален из списка!:", reply_markup=kb.exit
        )
    else:
        await callback.answer("❌ Ошибка при удалении!", show_alert=True)
