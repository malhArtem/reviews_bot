import datetime

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.config_reader import config
from bot.utils.keyboard import TariffCallbackFactory, ProfileCallbackFactory
from db.models.payments import Payments
from db.models.tariffs import Tariffs
from db.models.users import Users
from utils.parse_texts import texts

router = Router()
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


@router.callback_query(F.data == 'kassa')
# отлов события нажатия на кнопку выбора тарифа
async def order(callback_query: types.CallbackQuery, state: FSMContext, session):
    state_data = await state.get_data()
    await callback_query.answer()
    await callback_query.message.delete()
    tariff = await Tariffs.get_tariff(state_data.get('tariff_id'), session)
    # формирование клавиатуры
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Заплатить {tariff.price} RUB", pay=True)
    builder.button(text="Назад", callback_data=TariffCallbackFactory(id=state_data.get('tariff_id')))
    builder.adjust(1)


    # настройки платежа
    invoice = await callback_query.bot.send_invoice(
        chat_id=callback_query.message.chat.id,
        title=texts.title_invoice,
        description=f"Подписка на премиум на {tariff.duration} дней",
        payload=str(tariff.duration),
        need_email=True,
        send_email_to_provider=True,
        provider_token=config.YOU_KASSA_TOKEN,
        currency="rub",
        prices=[types.LabeledPrice(
            label=f"Подписка на {tariff.duration} дней",
            amount=tariff.price * 100
        )],
        # provider_data=json.dumps(provider_data),
        reply_markup=builder.as_markup()
    )
    await state.update_data(invoice_id=invoice.message_id)


@router.pre_checkout_query()
# подтверждение платежа
async def pre_checkout_handler(pre_checkout: types.PreCheckoutQuery):
    await pre_checkout.answer(ok=True)


@router.message(F.successful_payment)
# отлов успешного платежа
async def payment_handler(message: types.Message, session, state: FSMContext):
    # получение сохраненных данных о чате
    state_data = await state.get_data()
    await Payments.add_payment(message.successful_payment.provider_payment_charge_id, 'youkassa', message.from_user.id, message.successful_payment.total_amount//100, 'paid', session)
    # удаление сообщения с кнопкой оплаты
    await message.bot.delete_message(message.chat.id, state_data.get("invoice_id"))

    premium = None

    print(message.successful_payment.invoice_payload)

    # if message.successful_payment.invoice_payload == "Duration.three_days":
    #     premium = datetime.timedelta(days=3)
    # elif message.successful_payment.invoice_payload == "week":
    #     premium = datetime.timedelta(days=7)
    # elif message.successful_payment.invoice_payload == "mounts":
    #     premium = datetime.timedelta(days=30)

    await Users.update_user(message.from_user.id, session, premium=datetime.timedelta(days=int(message.successful_payment.invoice_payload)))
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data=ProfileCallbackFactory(user_id=str(message.from_user.id)))
    text = f"Вы приобрели премиум на {message.successful_payment.invoice_payload} дня (дней)"

    await message.answer(text, reply_markup=builder.as_markup())

