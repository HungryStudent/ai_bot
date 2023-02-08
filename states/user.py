from aiogram.dispatcher.filters.state import StatesGroup, State


class EnterPromt(StatesGroup):
    gpt_prompt = State()
    mdjrny_prompt = State()
