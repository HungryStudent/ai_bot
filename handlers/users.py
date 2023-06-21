from datetime import datetime

import requests
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, ChatActions
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from utils import db, ai, more_api, pay
from states import user as states
import keyboards.user as user_kb
from config import bot_url, TOKEN, NOTIFY_URL
from create_bot import dp


async def check_promocode(user_id, code, bot: Bot):
    print("ladjsnkajsdvn")
    promocode = await db.get_promocode_by_code(code)
    if promocode is None:
        return
    user_promocode = await db.get_user_promocode_by_promocode_id_and_user_id(promocode["promocode_id"],
                                                                             user_id)
    all_user_promocode = await db.get_all_user_promocode_by_promocode_id(promocode["promocode_id"])
    print("tut")
    print(user_promocode)
    print(user_promocode is not None)
    print(len(all_user_promocode) < promocode["uses_count"])
    if user_promocode is None and len(all_user_promocode) < promocode["uses_count"]:
        await db.create_user_promocode(promocode["promocode_id"], user_id)
        await db.add_balance(user_id, promocode['amount'], is_promo=True)
        await bot.send_message(user_id, f"Начислено {promocode['amount']} рублей за промокод")


async def remove_balance(bot: Bot, user_id):
    await db.remove_balance(user_id)
    user = await db.get_user(user_id)
    if user["balance"] <= 50:
        await db.update_stock_time(user_id, int(datetime.now().timestamp()))
        await bot.send_message(user_id, """⚠️Заканчивается баланс!

Успей пополнить в течении 24 часов и получи на счёт +10% от суммы пополнения ⤵️""",
                               reply_markup=user_kb.get_pay(user_id, 10))


async def not_enough_balance(bot: Bot, user_id):
    user = await db.get_user(user_id)
    if not user["is_pay"]:
        requests.post(NOTIFY_URL + f"/stock/{user_id}")
    await bot.send_message(user_id, """<i>Упс.. 
Недостаточно средств

1 запрос - 10 рублей</i>

Для продолжения необходимо пополнить баланс ⤵""", reply_markup=user_kb.top_up_balance)


async def get_mj(prompt, user_id, bot: Bot):
    await bot.send_message(user_id, "Ожидайте, генерирую изображение..🕙",
                           reply_markup=await user_kb.get_menu(user_id))
    await bot.send_chat_action(user_id, ChatActions.UPLOAD_PHOTO)

    res = await ai.get_mdjrny(prompt, user_id)

    if not res["status"]:
        msg_text = "Произошла ошибка, повторите попытку позже"
        if res["error"] == "banned word error":
            msg_text = "Запрещённое слово"
        await bot.send_message(user_id, msg_text)
    if res["mj_api"] == "reserve":
        await db.update_task_id(user_id, res["task_id"])


@dp.message_handler(state="*", commands='start')
async def start_message(message: Message, state: FSMContext):
    await state.finish()

    msg_args = message.get_args().split("_")
    inviter_id = 0
    code = None
    for msg_arg in msg_args:
        print(msg_arg)
        if msg_arg[0] == "r":
            try:
                inviter_id = int(msg_arg[1:])
            except ValueError:
                continue
            if inviter_id != str(message.from_user.id):
                inviter_id = msg_arg[1:]
        elif msg_arg[0] == "p":
            code = msg_arg[1:]

    user = await db.get_user(message.from_user.id)
    if user is None:
        await db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name,
                          int(inviter_id))

    if code is not None:
        await check_promocode(message.from_user.id, code, message.bot)

    await message.answer("""<b>NeuronAgent</b>🤖 - <i>Искусственный Интеллект.</i>

<b>Текстовый формат или создание изображения?</b>""", reply_markup=await user_kb.get_menu(message.from_user.id))


@dp.callback_query_handler(text="check_sub")
async def check_sub(call: CallbackQuery):
    user = await db.get_user(call.from_user.id)
    if user is None:
        await db.add_user(call.from_user.id, call.from_user.username, call.from_user.first_name, 0)
    await call.message.answer("""<b>NeuronAgent</b>🤖 - <i>Искусственный Интеллект.</i>

<b>Текстовый формат или создание изображения?</b>""", reply_markup=await user_kb.get_menu(call.from_user.id))
    await call.answer()


@dp.message_handler(text="🤝Партнерская программа")
async def ref_menu(message: Message):
    ref_data = await db.get_ref_stat(message.from_user.id)
    if ref_data['all_income'] is None:
        all_income = 0
    else:
        all_income = ref_data['all_income']
    await message.answer_photo(more_api.get_qr_photo(bot_url + '?start=' + str(message.from_user.id)),
                               caption=f'''<b>🤝 Партнёрская программа</b>
         
<i>Приводи друзей и зарабатывай 15% с их пополнений, пожизненно!</i>

<b>⬇️ Твоя реферальная ссылка:</b>
└ {bot_url}?start=r{message.from_user.id}

<b>🏅 Статистика:</b>
├ Лично приглашённых: <b>{ref_data["count_refs"]}</b>
├ Количество оплат: <b>{ref_data["orders_count"]}</b>
├ Всего заработано: <b>{all_income}</b> рублей
└ Доступно к выводу: <b>{ref_data["available_for_withdrawal"]}</b> рублей

Ваша реферальная ссылка: ''',
                               reply_markup=user_kb.get_ref_menu(f'{bot_url}?start=r{message.from_user.id}'))


@dp.message_handler(state="*", text="⚙Аккаунт")
async def show_profile(message: Message, state: FSMContext):
    await state.finish()
    user = await db.get_user(message.from_user.id)
    await message.answer(f"""🆔: <code>{message.from_user.id}</code>
💰Баланс: {user['balance']} руб.""", reply_markup=user_kb.get_account(user["chat_gpt_lang"]))


@dp.callback_query_handler(text="back_to_profile")
async def back_to_profile(call: CallbackQuery):
    user = await db.get_user(call.from_user.id)
    await call.message.edit_text(f"""id: {call.from_user.id}
Баланс: {user['balance']} руб.""", reply_markup=user_kb.get_account(user["chat_gpt_lang"]))


@dp.callback_query_handler(Text(startswith="change_lang:"))
async def change_lang(call: CallbackQuery):
    curr_lang = call.data.split(":")[1]
    new_lang = "en" if curr_lang == "ru" else "ru"
    await db.change_chat_gpt_lang(call.from_user.id, new_lang)
    lang_text = {"ru": "русский", "en": "английский"}
    await call.answer(f"Язык изменён на {lang_text[new_lang]}")
    await call.message.edit_reply_markup(reply_markup=user_kb.get_account(new_lang))


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


@dp.message_handler(state="*", text="💬ChatGPT✅")
@dp.message_handler(state="*", text="💬ChatGPT")
async def ask_question(message: Message, state: FSMContext):
    await state.finish()
    await db.change_default_ai(message.from_user.id, "chatgpt")

    await message.answer("""<b>Введите запрос</b>

Например: <code>Напиши сочинение на тему: Как я провёл это лето</code>

<i>Английский язык бот понимает лучше.</i>

Например: <code>Write a blog post about the environmental benefits of segregated waste collection for a broad audience</code>""",
                         reply_markup=await user_kb.get_menu(message.from_user.id))


@dp.message_handler(state="*", text="👨🏻‍💻Поддержка")
async def support(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Ответы на многие вопросы можно найти в нашем <a href="https://t.me/NeuronAgent">канале</a>.',
                         disable_web_page_preview=True, reply_markup=user_kb.about)


@dp.message_handler(state="*", text="🎨Midjourney✅")
@dp.message_handler(state="*", text="🎨Midjourney")
async def gen_img(message: Message, state: FSMContext):
    await state.finish()
    await db.change_default_ai(message.from_user.id, "image")
    await message.answer("""<b>Введите запрос для генерации изображения</b>

<i>Например:</i> <code>Замерзшее бирюзовое озеро вокруг заснеженных горных вершин</code>

<b><i>Для генерации на основе вашего фото:</i></b>

Фото + <code>Нарисуй меня в пустыне, в стиле Клод Воне</code>""",
                         reply_markup=await user_kb.get_menu(message.from_user.id))


@dp.callback_query_handler(Text(startswith="select_amount"))
async def select_amount(call: CallbackQuery):
    amount = int(call.data.split(":")[1])
    urls = {"lava": pay.get_pay_url_lava(call.from_user.id, amount),
            "freekassa": pay.get_pay_url_freekassa(call.from_user.id, amount)}
    await call.message.answer(f"""💰 Сумма: <b>{amount} рублей

♻️ Средства зачислятся автоматически</b>""", reply_markup=user_kb.get_pay_urls(urls))
    await call.answer()


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
        urls = {"lava": pay.get_pay_url_lava(message.from_user.id, amount),
                "freekassa": pay.get_pay_url_freekassa(message.from_user.id, amount)}
        await message.answer(f"""💰 Сумма: <b>{amount} рублей

♻️ Средства зачислятся автоматически</b>""", reply_markup=user_kb.get_pay_urls(urls))
        await state.finish()


@dp.message_handler(state="*", text="Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Ввод остановлен", reply_markup=await user_kb.get_menu(message.from_user.id))


@dp.callback_query_handler(Text(startswith="choose_image:"))
async def choose_image(call: CallbackQuery):
    await call.answer()
    buttonMessageId = call.data.split(":")[1]
    image_id = int(call.data.split(":")[2])
    mj_api = call.data.split(":")[3]
    await call.message.answer("Ожидайте, сохраняю изображение в отличном качестве…⏳",
                              reply_markup=await user_kb.get_menu(call.from_user.id))
    res = await ai.get_choose_mdjrny(buttonMessageId, image_id, call.from_user.id, mj_api)
    if not res["status"]:
        await call.message.answer("Произошла ошибка, повторите попытку позже")
    elif mj_api == "reserve":
        await call.message.answer_photo(res["image_url"])


@dp.callback_query_handler(Text(startswith="try_prompt"))
async def try_prompt(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await call.answer()

    user = await db.get_user(call.from_user.id)

    if user["default_ai"] == "chatgpt":
        if user["balance"] < 10:
            if user["free_chatgpt"] == 0:
                await not_enough_balance(call.bot, call.from_user.id)
                return
        await call.message.answer("Ожидайте, генерирую ответ..🕙",
                                  reply_markup=await user_kb.get_menu(call.from_user.id))
        await call.message.answer_chat_action(ChatActions.TYPING)
        result = await ai.get_gpt(data['prompt'], user["chat_gpt_lang"])
        await call.message.answer(result, reply_markup=user_kb.get_try_prompt('chatgpt'))
        user = await db.get_user(call.from_user.id)
        if user["free_chatgpt"] > 0:
            await db.remove_chatgpt(call.from_user.id)
        else:
            await remove_balance(call.bot, call.from_user.id)
        await db.add_action(call.from_user.id, "chatgpt")
    elif user["default_ai"] == "image":
        if user["balance"] < 10:
            if user["free_image"] == 0:
                await not_enough_balance(call.bot, call.from_user.id)
                return
        await get_mj(data['prompt'], call.from_user.id, call.bot)


@dp.message_handler()
async def gen_prompt(message: Message, state: FSMContext):
    await state.update_data(prompt=message.text)
    user = await db.get_user(message.from_user.id)
    if user is None:
        await message.answer("Введите команду /start для перезагрузки бота")
        await message.bot.send_message(796644977, message.from_user.id)
        return
    if user["default_ai"] == "chatgpt":
        if user["balance"] < 10:
            if user["free_chatgpt"] == 0:
                await not_enough_balance(message.bot, message.from_user.id)
                return
        await message.answer("Ожидайте, генерирую ответ..🕙", reply_markup=await user_kb.get_menu(message.from_user.id))
        await message.answer_chat_action(ChatActions.TYPING)
        result = await ai.get_gpt(message.text, user["chat_gpt_lang"])
        await message.answer(result, reply_markup=user_kb.get_try_prompt('chatgpt'))
        user = await db.get_user(message.from_user.id)
        if user["free_chatgpt"] > 0:
            await db.remove_chatgpt(message.from_user.id)
        else:
            await remove_balance(message.bot, message.from_user.id)
        await db.add_action(message.from_user.id, "chatgpt")
    elif user["default_ai"] == "image":
        if user["balance"] < 10:
            if user["free_image"] == 0:
                await not_enough_balance(message.bot, message.from_user.id)
                return
        await get_mj(message.text, message.from_user.id, message.bot)


@dp.message_handler(content_types="photo")
async def photo_imagine(message: Message, state: FSMContext):
    if message.caption is None:
        await message.answer("Добавьте описание к фотографии")
        return
    file = await message.photo[-1].get_file()
    photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
    ds_photo_url = await more_api.upload_photo_to_host(photo_url)
    prompt = ds_photo_url + " " + message.caption
    await state.update_data(prompt=prompt)
    user = await db.get_user(message.from_user.id)
    if user["balance"] < 10:
        if user["free_image"] == 0:
            await not_enough_balance(message.bot, message.from_user.id)
            return

    await get_mj(prompt, message.from_user.id, message.bot)
