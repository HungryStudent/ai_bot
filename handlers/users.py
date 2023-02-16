from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ChatActions

import keyboards.admin as admin_kb
from states import user as states
import keyboards.user as user_kb
from create_bot import dp
from utils import db, ai


@dp.message_handler(state="*", commands='start')
async def start_message(message: Message, state: FSMContext):
    await state.finish()
    user = db.get_user(message.from_user.id)
    if user is None:
        db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await message.answer("Здравствуйте, вам начислено 10 запросов", reply_markup=user_kb.menu)


@dp.message_handler(text="Поддержка")
async def support(message: Message):
    await message.answer("По всем вопросам: @efanov_n")


@dp.message_handler(state="*", text="Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Ввод остановлен", reply_markup=user_kb.menu)


@dp.message_handler(text="Задать вопрос")
async def ask_question(message: Message):
    user = db.get_user(message.from_user.id)
    if user["tokens"] == 0:
        await message.answer("У вас закончились запросы, купите их", reply_markup=user_kb.get_pay(message.from_user.id))
        return
    await message.answer("Введите ваш вопрос", reply_markup=user_kb.cancel)
    await states.EnterPromt.gpt_prompt.set()


@dp.message_handler(text="Сгенерировать изображение")
async def gen_img(message: Message):
    user = db.get_user(message.from_user.id)
    if user["tokens"] == 0:
        await message.answer("У вас закончились запросы, купите их", reply_markup=user_kb.get_pay(message.from_user.id))
        return
    await message.answer("Введите описание фото", reply_markup=user_kb.cancel)
    await states.EnterPromt.mdjrny_prompt.set()


@dp.message_handler(state=states.EnterPromt.gpt_prompt)
async def gpt_prompt(message: Message, state: FSMContext):
    db.remove_token(message.from_user.id)
    await message.answer("Ожидайте, генерируется ответ", reply_markup=user_kb.menu)
    await message.answer_chat_action(ChatActions.TYPING)
    await state.finish()
    result = await ai.get_gpt(message.text)
    await message.answer(result)


@dp.message_handler(state=states.EnterPromt.mdjrny_prompt)
async def mdjrny_prompt(message: Message, state: FSMContext):
    db.remove_token(message.from_user.id)
    await message.answer("Ожидайте, изображение генерируется", reply_markup=user_kb.menu)
    await message.answer_chat_action(ChatActions.UPLOAD_PHOTO)
    await state.finish()
    photo_url = await ai.get_mdjrny(message.text)
    await message.answer_photo(photo_url[0])
