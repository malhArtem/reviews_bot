import datetime

from aiocryptopay import AioCryptoPay, Networks
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.config_reader import config
from bot.utils.keyboard import TariffCallbackFactory, CheckInvoiceCallbackFactory, ProfileCallbackFactory
from db.models.payments import Payments
from db.models.tariffs import Tariffs
from db.models.users import Users
from utils.parse_texts import texts

crypto = AioCryptoPay(token=config.CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)


async def create_invoice(user_id, bot, tariff):
    fiat_invoice = await crypto.create_invoice(amount=tariff.price, fiat='RUB', currency_type='fiat', payload=f"{tariff.duration}", paid_btn_name="openBot", paid_btn_url=f"https://t.me/{(await bot.me()).username}?start=invc_{user_id}")
    return fiat_invoice


async def check_invoice(user_id, invoice_id, session):
    invoice = await crypto.get_invoices(invoice_ids=invoice_id)
    if invoice.status == 'paid':
        payment = await Payments.get_payment(invoice_id, 'crypto_bot', session)
        if payment.status == 'active':
            duration = invoice.payload
            await Payments.update_payment(payment.id, session)
            await Users.update_user(str(user_id), session, premium=datetime.timedelta(days=int(duration)))
            return True

    return False


async def check_user_payments(user_id, session):
    active_payments = await Payments.get_user_active_payments(user_id, session)
    invoices = await crypto.get_invoices(invoice_ids=active_payments)
    days = 0
    for invoice in invoices:
        if invoice.status == 'paid':
            duration = invoice.payload
            days += int(duration)
            await Payments.update_payment(invoice.id, session)
            await Users.update_user(user_id, session, premium=datetime.timedelta(days=int(duration)))
    return days

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")



@router.callback_query(F.data == 'crypto_bot')
async def crypto_pay(callback: types.CallbackQuery, state: FSMContext, session):
    state_data = await state.get_data()
    tariff = await Tariffs.get_tariff(state_data.get('tariff_id'), session)
    invoice = await create_invoice(callback.from_user.id,callback.bot, tariff)
    await Payments.add_payment(payment_id=invoice.invoice_id, provider='crypto_bot', user_id=str(callback.from_user.id), price=tariff.price, status='active', session=session)
    builder = InlineKeyboardBuilder()
    builder.button(text="Оплатить", url=invoice.bot_invoice_url)
    builder.button(text="Проверить платеж", callback_data=CheckInvoiceCallbackFactory(id=invoice.invoice_id))
    builder.button(text=texts.back_button, callback_data=TariffCallbackFactory(id=tariff.id))
    builder.adjust(1)
    text = texts.crypto_bot
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(CheckInvoiceCallbackFactory.filter())
async def check_invoice(callback_query: types.CallbackQuery, callback_data: CheckInvoiceCallbackFactory, session):
    builder = InlineKeyboardBuilder()
    print(callback_query)
    print(callback_query.from_user)
    # check = await check_invoice(callback_query.from_user.id, callback_data.id, session)
    invoice = await crypto.get_invoices(invoice_ids=callback_data.id)
    print(invoice)
    if invoice.status == 'paid':
        payment = await Payments.get_payment(invoice.invoice_id, 'crypto_bot', session)
        if payment.status == 'active':
            duration = invoice.payload
            await Payments.update_payment(payment.id, session)
            await Users.update_user(str(callback_query.from_user.id), session, premium=datetime.timedelta(days=int(duration)))
            text = texts.success_invoice
            builder.button(text=texts.back_button, callback_data=ProfileCallbackFactory(user_id=str(callback_query.from_user.id)))
            await callback_query.answer()
            await callback_query.message.edit_text(text, )
    else:
        await callback_query.answer(texts.crypto_boy_false, show_alert=True)


@router.callback_query(F.data == 'check_payments')
async def check_payments(callback: types.CallbackQuery, session):
    days = await check_user_payments(str(callback.from_user.id), session)
    if days:
        text = f"{texts.success_invoice} на {days} дней"
    else:
        text = f"Нет новых оплаченных платежей"
    await callback.answer(text, show_alert=True)
