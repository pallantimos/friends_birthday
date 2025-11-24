from aiogram.fsm.state import State, StatesGroup


class Add(StatesGroup):
    name = State()
    date_birth = State()


class Delete(StatesGroup):
    name = State()
    date_birth = State()


class Show(StatesGroup):
    name = State()
    date_birth = State()
