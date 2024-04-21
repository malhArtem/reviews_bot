from sqlalchemy import URL
import asyncio
import logging
from aiogram import Dispatcher, Bot
from bot.handlers import start
from bot.handlers.users import search_user, add_reviews, premium, profile, complaint
from bot.handlers.users.pay import you_cassa_pay, crypto_pay
from bot.handlers.admins import admin, sending, prices, update_user, policy, backup
from bot.utils.config_reader import config
from bot.utils import logger, commands, middlewares
from bot.utils.filters import BlockedFilter
from db import create_async_engine, get_session_maker, proceed_schemas, Base
from db.models.tariffs import Tariffs

bot_token = config.bot_token.get_secret_value()
admin_id = config.admin_id


logger = logger.logger


async def on_startup(bot: Bot):
    # Функция срабатывающая при запуске бота
    await commands.set_commands(bot)
    try:
        await bot.send_message(admin_id, "Бот запущен")
    except Exception as e:
        logger.error(e)


async def polling_main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)


    # Подключение к БД, создание таблиц
    postgres_url = URL.create(
        "postgresql+asyncpg",
        username=config.POSTGRES_USER,
        host=config.POSTGRES_HOST,
        password=config.POSTGRES_PASSWORD.get_secret_value(),
        database=config.POSTGRES_DB,
        port=config.POSTGRES_PORT
    )

    async_engine = create_async_engine(postgres_url)
    session_maker = get_session_maker(async_engine)
    await proceed_schemas(async_engine, Base.metadata)
    await Tariffs.init_tariffs(session_maker)

    # Создание объекта бота и диспетчера
    bot = Bot(bot_token, parse_mode='html')
    dp = Dispatcher()
    dp.message.filter(BlockedFilter())
    dp.callback_query.filter(BlockedFilter())
    dp.message.middleware(middlewares.ThrottlingMiddleware(10000, 10000))
    dp.message.middleware(middlewares.ThrottlingMiddleware(10000, 10000))
    dp.message.middleware(middlewares.CreateSessionMiddleware())
    dp.callback_query.middleware(middlewares.CreateSessionMiddleware())
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(profile.router)
    dp.include_router(premium.router)
    dp.include_router(you_cassa_pay.router)
    dp.include_router(search_user.router)
    dp.include_router(add_reviews.router)
    dp.include_router(sending.router)

    dp.include_router(prices.router)
    dp.include_router(update_user.router)
    dp.include_router(policy.router)
    dp.include_router(complaint.router)
    dp.include_router(crypto_pay.router)
    dp.include_router(backup.router)
    dp.startup.register(on_startup)
    # запуск бота с пропуском сообщений, которые приходили когда он был выключен
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, session_maker=session_maker)
    logger.error("Бот запущен")

if __name__ == '__main__':
    asyncio.run(polling_main())



