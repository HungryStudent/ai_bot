from aiogram.dispatcher.filters.state import StatesGroup, State


class Mailing(StatesGroup):
    enter_text = State()
