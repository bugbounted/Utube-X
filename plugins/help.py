from aiogram import types
from aiogram.dispatcher.filters import Command

from bot.config import SESSION_NAME


async def help_command(message: types.Message):
    """
    Handle the /help command
    """
    # Build the message with available commands and descriptions
    commands = [
        {"command": "/start", "description": "Start the bot"},
        {"command": "/upload", "description": "Upload a video to YouTube"},
        {"command": "/cancel", "description": "Cancel the current upload"},
        {"command": "/help", "description": "Show help information"},
    ]
    msg = f"Available commands:\n"
    for cmd in commands:
        msg += f"{cmd['command']}: {cmd['description']}\n"

    # Include instructions for authenticated users
    if message.chat.id in message.bot.auth_users:
        msg += f"\nYou are authenticated as {message.from_user.full_name} ({message.from_user.username})."
        msg += f"\nTo upload a video, simply send a video file or a link to the video file."

    # Send the message
    await message.answer(msg)


# Register the command handler
def register_help(dp):
    dp.register_message_handler(help_command, Command("help"), state="*")
