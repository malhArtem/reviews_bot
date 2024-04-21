from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllChatAdministrators, BotCommandScopeChat

from bot.utils.config_reader import config

admin_id = config.admin_id


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='запуск бота'
        ),

    # ]
    #
    # chats_commands = [
    #     BotCommand(
    #         command='add_whitelist',
    #         description='добавить в белый список'
    #     ),
    #     BotCommand(
    #         command='rm_whitelist',
    #         description='удалить из белого списка'
    #     )
    # ]
    #
    # admin_commands = [
    #     BotCommand(
    #         command='tariffs',
    #         description='настройка тарифов'
    #     ),
    #     BotCommand(
    #         command='promocodes',
    #         description='настройка промокодов'
    #     ),
    #     BotCommand(
    #         command='send_all',
    #         description='рассылка'
    #     )
    ]

    await bot.set_my_commands(commands, BotCommandScopeAllPrivateChats())
    # await bot.set_my_commands(chats_commands, BotCommandScopeAllChatAdministrators())
    # await bot.set_my_commands(commands + admin_commands, BotCommandScopeChat(chat_id=admin_id))
