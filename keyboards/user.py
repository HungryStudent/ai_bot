from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove, WebAppInfo

from urllib import parse

withdraw_ref_menu = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("На банковскую карту", callback_data='withdraw_ref:bank_card')).add(
    InlineKeyboardButton("QIWI", callback_data="withdraw_ref:qiwi"),
    InlineKeyboardButton("На баланс", callback_data="withdraw_ref:balance")
)

about = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton("📢Канал проекта", url="https://t.me/NeuronAgent"),
                                              InlineKeyboardButton("🆘Помощь", url="https://t.me/NeuronSupportBot"))

cancel = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(KeyboardButton("Отмена"))

top_up_balance = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("💰Пополнить баланс", callback_data="top_up_balance"))

partner = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("↗️Перейти и подписаться", url="https://t.me/NeuronAgent"),
    InlineKeyboardButton("✅Я подписался", callback_data="check_sub"))

back_to_choose = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🔙Назад", callback_data="back_to_choose_balance"))

clear_content = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Завершить диалог", callback_data="clear_content"))


def get_account(lang):
    lang_text = {"en": "ENG", "ru": "RUS"}
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("💰Пополнить баланс", callback_data="top_up_balance"),
        InlineKeyboardButton(f"Ответы ChatGPT: {lang_text[lang]}", callback_data=f"change_lang:{lang}"))


def get_try_prompt(ai_type):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🔄 Другой вариант", callback_data=f"try_prompt:{ai_type}"))


def get_menu(default_ai):
    if default_ai == "chatgpt":
        return ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(KeyboardButton("💬ChatGPT✅"),
                                                                          KeyboardButton("🎨Midjourney"),
                                                                          KeyboardButton("⚙Аккаунт"),
                                                                          KeyboardButton("👨🏻‍💻Поддержка"),
                                                                          KeyboardButton("🤝Партнерская программа"))
    elif default_ai == "image":
        return ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(KeyboardButton("💬ChatGPT"),
                                                                          KeyboardButton("🎨Midjourney✅"),
                                                                          KeyboardButton("⚙Аккаунт"),
                                                                          KeyboardButton("👨🏻‍💻Поддержка"),
                                                                          KeyboardButton("🤝Партнерская программа"))
    else:
        return ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(KeyboardButton("💬ChatGPT"),
                                                                          KeyboardButton("🎨Midjourney"),
                                                                          KeyboardButton("⚙Аккаунт"),
                                                                          KeyboardButton("👨🏻‍💻Поддержка"),
                                                                          KeyboardButton("🤝Партнерская программа"))


def get_pay(user_id, stock=0):
    if stock == 0:
        stock_text = ""
    else:
        stock_text = f" (+{stock}%)"
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton("200₽" + stock_text, callback_data="select_amount:200"),
        InlineKeyboardButton("500₽" + stock_text, callback_data="select_amount:500"),
        InlineKeyboardButton("1000₽" + stock_text, callback_data="select_amount:1000")).add(
        InlineKeyboardButton("💰Другая сумма" + stock_text, callback_data="other_amount")).add(
        InlineKeyboardButton("🔙Назад", callback_data="back_to_profile")
    )


def get_pay_urls(urls):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Банковская карта", web_app=WebAppInfo(url=urls["lava"])),
        InlineKeyboardButton("СБП(Переводом)", web_app=WebAppInfo(url=urls["freekassa"])),
        InlineKeyboardButton("Криптовалюта", web_app=WebAppInfo(url=urls["payok"])),
        InlineKeyboardButton("Другие способы", web_app=WebAppInfo(url=urls["freekassa"])),
        InlineKeyboardButton("🔙Назад", callback_data="back_to_choose_balance"))


def get_ref_menu(url):
    text_url = parse.quote(url)
    url = f'https://t.me/share/url?url={text_url}'
    return InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('📩Поделится ссылкой', url=url),
                                                 InlineKeyboardButton('💳Вывод средств',
                                                                      callback_data='withdraw_ref_menu'),
                                                 InlineKeyboardButton('🔙Назад', callback_data='check_sub'))


def get_try_prompt_or_choose(buttonMessageId, mj_api, include_try=False):
    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("u1", callback_data=f"choose_image:{buttonMessageId}:1:{mj_api}"),
        InlineKeyboardButton("u2", callback_data=f"choose_image:{buttonMessageId}:2:{mj_api}"),
        InlineKeyboardButton("u3", callback_data=f"choose_image:{buttonMessageId}:3:{mj_api}"),
        InlineKeyboardButton("u4", callback_data=f"choose_image:{buttonMessageId}:4:{mj_api}"))
    if include_try:
        kb.add(InlineKeyboardButton("🔄 Ещё варианты", callback_data=f"try_prompt:image"))
    return kb


def get_choose(buttonMessageId):
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("🪄 Vary (Subtle)", callback_data=f"change_image:vary:subtle:{buttonMessageId}"),
        InlineKeyboardButton("🪄 Vary (Strong)", callback_data=f"change_image:vary:strong:{buttonMessageId}"),
        InlineKeyboardButton("🔍 Zoom Out 2x", callback_data=f"change_image:zoom:2:{buttonMessageId}"),
        InlineKeyboardButton("🔍 Zoom Out 1.5x", callback_data=f"change_image:zoom:1.5:{buttonMessageId}"))
