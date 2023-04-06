from aiogram import types
from aiogram.dispatcher.filters import Command

from bot import dp


@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    await message.answer("Hi!\nI'm a bot that can upload videos to YouTube from telegram or direct links. \nUse /help command to see the list of available commands.")
