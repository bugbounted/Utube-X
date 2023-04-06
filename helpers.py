import os
import time
import logging
import mimetypes
from datetime import timedelta

from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CallbackContext

from .config import Config


logger = logging.getLogger(__name__)


def bytes_to_human_readable(size_bytes: int) -> str:
    """Converts bytes to human readable format.

    Args:
        size_bytes (int): The size in bytes.

    Returns:
        str: The human readable format of size.
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(pow(1024, int(math.log(size_bytes, 1024))))
    p = pow(1024, int(math.log(size_bytes, 1024)))
    size = round(size_bytes/p, 2)
    return f"{size} {size_name[int(math.log(i, 1024))]}"


def upload_to_youtube(file_path: str, title: str, description: str, privacy_status: str, category_id: str) -> str:
    """Uploads a video to YouTube.

    Args:
        file_path (str): The path to the video file.
        title (str): The title of the video.
        description (str): The description of the video.
        privacy_status (str): The privacy status of the video.
        category_id (str): The category ID of the video.

    Returns:
        str: The video ID of the uploaded video.
    """
    # Authenticate with Google API
    credentials = Credentials.from_authorized_user_info(info=Config.CREDENTIALS_INFO)
    youtube = build("youtube", "v3", credentials=credentials)

    try:
        # Get video file size
        file_size = os.path.getsize(file_path)
        logger.info(f"Video size: {bytes_to_human_readable(file_size)}")

        # Initialize video metadata
        media = MediaFileUpload(file_path, chunksize=1024*1024, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "categoryId": category_id,
                    "title": title,
                    "description": description,
                },
                "status": {
                    "privacyStatus": privacy_status,
                },
            },
            media_body=media,
        )

        # Upload video
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.debug(f"Upload progress: {progress}%")
                logger.debug(f"Upload speed: {bytes_to_human_readable(status.resumable_progress.last_chunk_size)} per second")
                logger.debug(f"Bytes transferred: {bytes_to_human_readable(status.total_size_uploaded)} of {bytes_to_human_readable(file_size)}")
                logger.debug(f"Time elapsed: {timedelta(seconds=status.progress() * (time.monotonic() - status.resumable_progress.started))}")
                keyboard = [
                    [
                        InlineKeyboardButton("Cancel upload", callback_data="cancel_upload"),
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message = f"Uploading: 『{progress}%』\n"
                message += f"|{'░' * progress}{'░' * (100 - progress)}| "
            message += f"\n┏━🚀 Speed: {status.speed() / (1024 * 1024):.2f} MiB/sec "
            message += f"\n┃ ┠─✅ Done: {status.resumable_progress / (1024):.2f} KiB "
            message += f"\n┃ ┠─💽 Size: {status.total_size / (1024 * 1024 * 1024):.2f} GiB "
            message += f"\n┃ ┗━⏰ ETA: {status.eta} seconds"
            await bot.edit_message_text(chat_id=upload_status.chat_id, message_id=upload_status.message_id, text=message, reply_markup=reply_markup)

    if "id" in response:
        return True
    else:
        logger.error(f"Error occurred while uploading video: {response}")
        return False
