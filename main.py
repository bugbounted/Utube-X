import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from plugins.authentication import authenticated_user
from plugins.help import help_text
from plugins.start import start_text
from plugins.upload import upload_video
from plugins.cancel import cancel_upload
from config import (
    BOT_TOKEN, API_ID, API_HASH, CLIENT_ID,
    CLIENT_SECRET, BOT_OWNER, AUTH_USERS,
    VIDEO_CATEGORY, VIDEO_DESCRIPTION,
    VIDEO_TITLE_PREFIX, VIDEO_TITLE_SUFFIX,
    UPLOAD_MODE
)

# Enable logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Initialize Google API credentials
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
creds = None
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret.json", SCOPES)
        creds = flow.run_local_server(port=0)
    with open("token.json", "w") as token:
        token.write(creds.to_json())

# Register handlers
@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(start_text)

@dp.message_handler(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(help_text)

@dp.message_handler(Command("upload"))
@authenticated_user
async def cmd_upload(message: types.Message, state: FSMContext):
    await message.answer("Please send the video file or provide the direct link to the video.")
    await upload_video.set()
    await state.update_data(
        video_title_prefix=VIDEO_TITLE_PREFIX,
        video_title_suffix=VIDEO_TITLE_SUFFIX,
        video_description=VIDEO_DESCRIPTION,
        video_category=VIDEO_CATEGORY,
        upload_mode=UPLOAD_MODE
    )

@dp.message_handler(content_types=["video", "document", "text"], state=upload_video)
async def process_video(message: types.Message, state: FSMContext):
    await bot.send_chat_action(message.chat.id, types.ChatActions.UPLOAD_VIDEO)
    data = await state.get_data()
    title_prefix = data.get("video_title_prefix", "")
    title_suffix = data.get("video_title_suffix", "")
    description = data.get("video_description", "")
    category = data.get("video_category", "")
    mode = data.get("upload_mode", "private")
    await message.forward(chat_id=BOT_OWNER)
    await bot.send_message(
        BOT_OWNER,
        f"Upload video: <code>{title_prefix}{message.caption or message.document.file_name or ''}{title_suffix}</code>\n\nPlease wait while I upload the video...",
        disable_web_page_preview=True
    )
    await state.finish()
    await upload_video.set()
    await state.update_data(
        message_id=message.message_id,
        chat_id=message.chat.id,
        title_prefix=title_prefix,
        title_suffix=title_suffix,
        description=description,
        category=category,
        mode=mode
    )

@dp.callback_query_handler(lambda c: c.data == "cancel_upload")
async def cancel_upload_cb_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """Handler for cancelling the upload process."""
    await bot.answer_callback_query(callback_query.id, text="Upload process cancelled")
    async with state.proxy() as data:
        data.pop("upload_job_id", None)
        data.pop("upload_cancelled", False)
    await state.finish()
