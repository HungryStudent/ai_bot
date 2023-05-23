from aiogram.types import Message, CallbackQuery, ChatActions
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from utils import db, ai, more_api
from states import user as states
import keyboards.user as user_kb
from config import bot_url
from create_bot import dp


@dp.message_handler(state="*", commands='start')
async def start_message(message: Message, state: FSMContext):
    await state.finish()

    user = db.get_user(message.from_user.id)
    if user is None:
        inviter_id = message.get_args()
        if inviter_id in ["", str(message.from_user.id)]:
            inviter_id = 0

        db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name, inviter_id)
    await message.answer("""<b>NeuronAgent</b>🤖 - <i>Искусственный Интеллект.</i>

<b>Текстовый формат или создание изображения?</b>""", reply_markup=user_kb.get_menu(message.from_user.id))


@dp.callback_query_handler(text="check_sub")
async def check_sub(call: CallbackQuery):
    user = db.get_user(call.from_user.id)
    if user is None:
        db.add_user(call.from_user.id, call.from_user.username, call.from_user.first_name, 0)
    await call.message.answer("""<b>NeuronAgent</b>🤖 - <i>Искусственный Интеллект.</i>

<b>Текстовый формат или создание изображения?</b>""", reply_markup=user_kb.get_menu(call.from_user.id))
    await call.answer()


@dp.message_handler(text="🤝Партнерская программа")
async def ref_menu(message: Message):
    ref_data = db.get_ref_stat(message.from_user.id)
    if ref_data['all_income'] is None:
        ref_data['all_income'] = 0
    await message.answer_photo(more_api.get_qr_photo(bot_url + '?start=' + str(message.from_user.id)),
                               caption=f'''<b>🤝 Партнёрская программа</b>
         
<i>Приводи друзей и зарабатывай 15% с их пополнений, пожизненно!</i>

<b>⬇️ Твоя реферальная ссылка:</b>
└ {bot_url}?start={message.from_user.id}

<b>🏅 Статистика:</b>
├ Лично приглашённых: <b>{ref_data["count_refs"]}</b>
├ Количество оплат: <b>{ref_data["orders_count"]}</b>
├ Всего заработано: <b>{ref_data["all_income"]}</b> рублей
└ Доступно к выводу: <b>{ref_data["available_for_withdrawal"]}</b> рублей

Ваша реферальная ссылка: ''',
                               reply_markup=user_kb.get_ref_menu(f'{bot_url}?start={message.from_user.id}'))


@dp.message_handler(state="*", text="⚙Аккаунт")
async def show_profile(message: Message, state: FSMContext):
    await state.finish()
    user = db.get_user(message.from_user.id)
    await message.answer(f"""🆔: <code>{message.from_user.id}</code>
💰Баланс: {user['balance']} руб.""", reply_markup=user_kb.top_up_balance)


@dp.callback_query_handler(text="back_to_profile")
async def back_to_profile(call: CallbackQuery):
    user = db.get_user(call.from_user.id)
    await call.message.edit_text(f"""id: {call.from_user.id}
Баланс: {user['balance']} руб.""", reply_markup=user_kb.top_up_balance)


@dp.callback_query_handler(text="top_up_balance")
async def choose_amount(call: CallbackQuery):
    await call.message.edit_text("Выберите сумму пополнения", reply_markup=user_kb.get_pay(call.from_user.id))


@dp.callback_query_handler(text="back_to_choose_balance", state="*")
async def back_to_choose_balance(call: CallbackQuery):
    await call.message.edit_text("Выберите сумму пополнения", reply_markup=user_kb.get_pay(call.from_user.id))


@dp.callback_query_handler(text="other_amount")
async def enter_other_amount(call: CallbackQuery):
    await call.message.edit_text("""Введите сумму пополнения баланса в рублях:

<b>Минимальный платеж 200 рублей</b>""", reply_markup=user_kb.back_to_choose)
    await states.EnterAmount.enter_amount.set()


@dp.message_handler(state="*", text="💬Текст✅")
@dp.message_handler(state="*", text="💬Текст")
async def ask_question(message: Message, state: FSMContext):
    await state.finish()
    db.change_default_ai(message.from_user.id, "chatgpt")

    await message.answer("""<b>Введите запрос</b>

Например: <code>Напиши сочинение на тему: Как я провёл это лето</code>

<i>Английский язык бот понимает лучше.</i>

Например: <code>Write a blog post about the environmental benefits of segregated waste collection for a broad audience</code>""",
                         reply_markup=user_kb.get_menu(message.from_user.id))


@dp.message_handler(state="*", text="👨🏻‍💻Поддержка")
async def support(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Ответы на многие вопросы можно найти в нашем <a href="https://t.me/NeuronAgent">канале</a>.',
                         disable_web_page_preview=True, reply_markup=user_kb.about)


@dp.message_handler(state="*", text="🎨Изображение✅")
@dp.message_handler(state="*", text="🎨Изображение")
async def gen_img(message: Message, state: FSMContext):
    await state.finish()
    db.change_default_ai(message.from_user.id, "image")
    await message.answer("""<b>Введите запрос для генерации изображения</b>

Например: <code>Замерзшее прозрачное озеро вокруг заснеженных горных вершин</code>

<u><i>Английский язык бот понимает лучше.</i></u>

Например: <code>Cat, psytrance, uhd, detailed, ornate, beautiful, 8k, photography</code>""",
                         reply_markup=user_kb.get_menu(message.from_user.id))


@dp.message_handler(state=states.EnterAmount.enter_amount)
async def create_other_order(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Введите целое число!")
        return
    if amount < 200:
        await message.answer("Минимальная сумма платежа 200 рублей")
    else:
        await message.answer(f"""💰 Сумма: <b>{amount} рублей

♻️ Средства зачислятся автоматически</b>""", reply_markup=user_kb.get_other_pay(message.from_user.id, amount))
        await state.finish()


@dp.message_handler(state="*", text="Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Ввод остановлен", reply_markup=user_kb.get_menu(message.from_user.id))


@dp.callback_query_handler(Text(startswith="choose_image:"))
async def choose_image(call: CallbackQuery):
    buttonMessageId = call.data.split(":")[1]
    image_id = int(call.data.split(":")[2])
    ai.get_choose_mdjrny(buttonMessageId, image_id, call.from_user.id)
    await call.message.answer("Ожидайте, сохраняю изображение в отличном качестве…⏳", reply_markup=user_kb.get_menu(call.from_user.id))
    await call.answer()


@dp.callback_query_handler(Text(startswith="try_prompt"))
async def try_prompt(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ai_type = call.data.split(":")[1]

    user = db.get_user(call.from_user.id)

    if user["default_ai"] == "chatgpt":
        if user["balance"] < 10:
            if user["free_chatgpt"] == 0:
                await call.message.answer("""<i>Упс.. 
Недостаточно средств

1 запрос - 10 рублей</i>

Для продолжения необходимо пополнить баланс ⤵""", reply_markup=user_kb.top_up_balance)
                return
        await call.message.answer("Ожидайте, генерирую ответ..🕙", reply_markup=user_kb.get_menu(call.from_user.id))
        await call.message.answer_chat_action(ChatActions.TYPING)
        result = await ai.get_gpt(data['prompt'])
        await call.message.answer(result, reply_markup=user_kb.get_try_prompt('chatgpt'))
        user = db.get_user(call.from_user.id)
        if user["free_chatgpt"] > 0:
            db.remove_chatgpt(call.from_user.id)
        else:
            db.remove_balance(call.from_user.id)
        db.add_action(call.from_user.id, "chatgpt")
    elif user["default_ai"] == "image":
        if user["balance"] < 10:
            if user["free_image"] == 0:
                await call.message.answer("""<i>Упс.. 
Недостаточно средств

1 запрос - 10 рублей</i>

Для продолжения необходимо пополнить баланс ⤵""", reply_markup=user_kb.top_up_balance)
                return
        await call.message.answer("Ожидайте, генерирую изображение..🕙",
                                  reply_markup=user_kb.get_menu(call.from_user.id))
        await call.message.answer_chat_action(ChatActions.UPLOAD_PHOTO)
        ds_msg_id = await ai.get_mdjrny(data['prompt'])
        db.update_ds_msg_id(call.from_user.id, ds_msg_id)

    await call.answer()


@dp.message_handler()
async def prompt(message: Message, state: FSMContext):
    await state.update_data(prompt=message.text)
    user = db.get_user(message.from_user.id)
    if user["default_ai"] == "chatgpt":
        if user["balance"] < 10:
            if user["free_chatgpt"] == 0:
                await message.answer("""<i>Упс.. 
Недостаточно средств

1 запрос - 10 рублей</i>

Для продолжения необходимо пополнить баланс ⤵""", reply_markup=user_kb.top_up_balance)
                return
        await message.answer("Ожидайте, генерирую ответ..🕙", reply_markup=user_kb.get_menu(message.from_user.id))
        await message.answer_chat_action(ChatActions.TYPING)
        result = await ai.get_gpt(message.text)
        await message.answer(result, reply_markup=user_kb.get_try_prompt('chatgpt'))
        user = db.get_user(message.from_user.id)
        if user["free_chatgpt"] > 0:
            db.remove_chatgpt(message.from_user.id)
        else:
            db.remove_balance(message.from_user.id)
        db.add_action(message.from_user.id, "chatgpt")
    elif user["default_ai"] == "image":
        if user["balance"] < 10:
            if user["free_image"] == 0:
                await message.answer("""<i>Упс.. 
Недостаточно средств

1 запрос - 10 рублей</i>

Для продолжения необходимо пополнить баланс ⤵""", reply_markup=user_kb.top_up_balance)
                return
        await message.answer("Ожидайте, генерирую изображение..🕙", reply_markup=user_kb.get_menu(message.from_user.id))
        await message.answer_chat_action(ChatActions.UPLOAD_PHOTO)
        ds_msg_id = await ai.get_mdjrny(message.text)
        db.update_ds_msg_id(message.from_user.id, ds_msg_id)
