import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.utils.message_texts import get_text_publication
from bot.utils.keyboard import ParticipationCallbackFactory, ReservationCallbackFactory
from bot.utils.logger import logger
from db.models.publications import get_publication_with_parameters, Publication
from db.models.subscription import search_subscriptions
from db.models.users import get_users_for_events, get_all_users


async def event_mailing(bot: Bot, session_maker, publication_id):
    publication = await get_publication_with_parameters(publication_id, session_maker)
    text = get_text_publication(publication)
    users = await get_users_for_events(session_maker)
    text = "Новое мероприятие:\n\n" + text
    builder = InlineKeyboardBuilder()
    builder.button(text="Пойти на мероприятие", callback_data=ParticipationCallbackFactory(event_id=publication.id))

    for user in users:
        if user.user_id != publication.user_id:

            try:
                if publication.photo is not None and len(publication.photo) > 5:
                    await bot.send_photo(chat_id=user.chat_id, photo=publication.photo, caption=text, reply_markup=builder.as_markup())

                else:
                    await bot.send_message(chat_id=user.chat_id, text=text, reply_markup=builder.as_markup())
                await asyncio.sleep(0.2)

            except TelegramRetryAfter:
                await asyncio.sleep(1)
                if publication.photo is not None and len(publication.photo) > 5:
                    await bot.send_photo(chat_id=user.chat_id, photo=publication.photo, caption=text,
                                         reply_markup=builder.as_markup())

                else:
                    await bot.send_message(chat_id=user.chat_id, text=text, reply_markup=builder.as_markup())

            except TelegramForbiddenError:
                pass

            except Exception as e:
                logger.error(e)


async def lot_mailing(publication_id, bot: Bot, session_maker):
    publication = await get_publication_with_parameters(publication_id, session_maker)
    text = get_text_publication(publication)
    text = "Новый лот по вашей подписке:\n\n" + text
    builder = InlineKeyboardBuilder()
    builder.button(text="Забронировать", callback_data=ReservationCallbackFactory(publication_id=publication.id,
                                                                                  user_id=publication.user_id))
    subscriptions = await search_subscriptions(text, session_maker)
    for subscription in subscriptions:
        try:
            if publication.photo is not None and len(publication.photo) > 5:
                await bot.send_photo(subscription.user_id, photo=publication.photo, caption=text, reply_markup=builder.as_markup())
            else:
                await bot.send_message(subscription.user_id, text, reply_markup=builder.as_markup())
            await asyncio.sleep(0.2)

        except TelegramRetryAfter:
            await asyncio.sleep(1)

            if publication.photo is not None and len(publication.photo) > 5:
                await bot.send_photo(subscription.user_id, photo=publication.photo, caption=text, reply_markup=builder.as_markup())
            else:
                await bot.send_message(subscription.user_id, text, reply_markup=builder.as_markup())

        except TelegramForbiddenError:
            pass

        except Exception as e:
            logger.error(e)


async def sending_text(text, bot: Bot, session_maker):
    users = await get_all_users(session_maker)
    print(text),

    for user in users:
        print(user.name)
        try:
            await bot.send_message(user.chat_id, text)
            await asyncio.sleep(0.2)
        except TelegramRetryAfter:
            await asyncio.sleep(1)
            await bot.send_message(user.chat_id, text)

        except TelegramForbiddenError:
            pass

        except Exception as e:
            logger.error(e)


async def edit_event_mailing(publication_id, bot: Bot, session_maker):
    publication = await get_publication_with_parameters(publication_id, session_maker)
    text = get_text_publication(publication)
    text = "Мероприятие изменено:\n\n" + text
    builder = InlineKeyboardBuilder()
    # builder.button(text="Пойти на мероприятие", callback_data=ParticipationCallbackFactory(event_id=publication.id))

    for user in publication.reserved:
        if user != publication.user_id:

            try:
                if publication.photo is not None and len(publication.photo) > 5:
                    await bot.send_photo(chat_id=user, photo=publication.photo, caption=text, reply_markup=builder.as_markup())

                else:
                    await bot.send_message(chat_id=user, text=text, reply_markup=builder.as_markup())
                await asyncio.sleep(0.2)

            except TelegramRetryAfter:
                await asyncio.sleep(1)
                if publication.photo is not None and len(publication.photo) > 5:
                    await bot.send_photo(chat_id=user, photo=publication.photo, caption=text,
                                         reply_markup=builder.as_markup())

                else:
                    await bot.send_message(chat_id=user, text=text, reply_markup=builder.as_markup())

            except TelegramForbiddenError:
                pass

            except Exception as e:
                logger.error(e)