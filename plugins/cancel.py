from aiogram.types import Message
from aiogram.dispatcher.filters import Command

from bot.utubebot import UtubeBot
from bot.config import AUTH_USERS


async def cancel_command(msg: Message):
    user_id = msg.from_user.id
    if user_id not in AUTH_USERS:
        return

    chat_id = msg.chat.id
    bot = UtubeBot.get_instance()

    # Check if there is an ongoing upload for this chat
    if bot.current_uploads.get(chat_id):
        await bot.cancel_upload(chat_id)
        await msg.reply("Upload cancelled!")
    else:
        await msg.reply("No ongoing uploads for this chat.")


def register_cancel_plugin(dp):
    dp.register_message_handler(cancel_command, Command("cancel"), state="*")
