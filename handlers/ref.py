from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ChatActions

from config import bot_url
from states import user as states
import keyboards.user as user_kb
from create_bot import dp
from utils import db, ai, more_api

invalid_purse_text = {'qiwi': 'Введите корректный номер телефона. Например: 79111111111',
                      'bank_card': 'Введите корректный номер карты. Например: 4012888812345678'}


@dp.callback_query_handler(text='withdraw_ref_menu')
async def withdraw_ref_menu(call: CallbackQuery):
    user = db.get_user(call.from_user.id)
    if user['ref_balance'] >= 100:
        await call.message.answer(
            'Вы можете вывести средства на банковскую карту, QIWI кошелек, а также использовать для оплаты наших услуг в боте',
            reply_markup=user_kb.withdraw_ref_menu)
    else:
        await call.message.answer('Минимальная сумма для вывода - 100 рублей')
    await call.answer()


@dp.callback_query_handler(Text(startswith='withdraw_ref'))
async def withdraw_ref(call: CallbackQuery, state: FSMContext):
    withdraw_type = call.data.split(':')[1]
    if withdraw_type == 'bank_card':
        await call.message.answer('Введите номер карты. Например: 4012888812345678', reply_markup=user_kb.cancel)
    elif withdraw_type == 'qiwi':
        await call.message.answer('Введите номер телефона. Например: 79111111111', reply_markup=user_kb.cancel)
    elif withdraw_type == 'balance':
        db.add_balance_from_ref(call.from_user.id)
        await call.message.answer('Средства зачислены на баланс')
        return

    await states.EnterWithdrawInfo.purse.set()
    await state.update_data(withdraw_type=withdraw_type)


@dp.message_handler(state=states.EnterWithdrawInfo.purse)
async def finish_withdraw_ref(message: Message, state: FSMContext):
    state_data = await state.get_data()
    withdraw_type = state_data['withdraw_type']
    try:
        purse = int(message.text)
    except ValueError:
        await message.answer(invalid_purse_text[withdraw_type])
        return

    if withdraw_type == 'qiwi':
        if len(str(purse)) != 11:
            await message.answer(invalid_purse_text[withdraw_type])
            return
    elif withdraw_type == 'bank_card':
        if len(str(purse)) != 16:
            await message.answer(invalid_purse_text[withdraw_type])
            return
    user = db.get_user(message.from_user.id)
    withdraw_data = more_api.withdraw_ref_balance(purse, user['ref_balance'], withdraw_type)
    if withdraw_data['status'] == 'error':
        if withdraw_data['desc'].startswith('Invalid Purse'):
            await message.answer(invalid_purse_text[withdraw_type])
            return
        else:
            await message.answer(f'Произошла ошибка, отправьте её администратору: {withdraw_data["desc"]}')

    db.add_withdraw(message.from_user.id, user['ref_balance'])
    db.reset_ref_balance(message.from_user.id)
    await message.answer('Деньги будут скоро зачислены')
