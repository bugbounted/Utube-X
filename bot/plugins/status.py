import asyncio
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import dp
from bot.helpers import get_upload_progress


@dp.message_handler(Command("status"))
async def cmd_status(message: types.Message, state: FSMContext):
    """
    This handler will be called when user sends `/status` command.
    """
    user_data = await state.get_data()
    task_id = user_data.get('upload_task_id')
    if not task_id:
        await message.reply("No ongoing upload task found.")
        return

    # Get the upload progress from the task ID
    progress = await get_upload_progress(task_id)

    # Create the message text and reply keyboard
    keyboard = [[InlineKeyboardButton(text="Cancel Upload", callback_data="cancel_upload")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_text = f"Uploading: 『{progress}%』\n"
    message_text += f"{'|' * int(progress/5)}{'░' * int(20 - progress/5)}\n"
    message_text += f"┏━🚀 Speed: {progress['speed']}\n"
    message_text += f"┃ ┠─✅ Done: {progress['done']}\n"
    message_text += f"┃ ┠─💽 Size: {progress['total']}\n"
    message_text += f"┃ ┗━⏰ ETA: {progress['eta']}\n"

    # Get the task creation time
    created_time = user_data.get('task_created_time')

    if created_time:
        elapsed_time = datetime.now() - created_time
        elapsed_time_str = f"{elapsed_time.seconds // 60} minutes and {elapsed_time.seconds % 60} seconds"
        message_text += f"\nElapsed Time: {elapsed_time_str}\n"

    # Reply with the message and keyboard
    await message.reply(message_text, reply_markup=reply_markup)
