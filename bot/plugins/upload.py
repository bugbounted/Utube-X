import os
import time
import logging
from googleapiclient.errors import HttpError
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from bot.helpers import uploader, downloader
from bot.config import Config
from bot.plugins.cancel import cancel_upload
from bot.plugins.status import upload_status
from bot.plugins.authentication import authenticate_user
from bot.translations import gettext as _

logger = logging.getLogger(__name__)

def register_upload_handlers(dp):
    """Register handlers for video uploads"""
    dp.add_handler(CommandHandler("upload", upload_command))
    dp.add_handler(CommandHandler("setdescription", set_description))
    dp.add_handler(CommandHandler("settitleprefix", set_title_prefix))
    dp.add_handler(CommandHandler("settitlesuffix", set_title_suffix))
    dp.add_handler(CommandHandler("setcategory", set_category))
    dp.add_handler(CommandHandler("setprivacy", set_privacy))
    dp.add_handler(CommandHandler("setmode", set_upload_mode))
    dp.add_handler(CallbackQueryHandler(cancel_upload_cb_handler, pattern="cancel_upload"))
    dp.add_handler(MessageHandler(Filters.video | Filters.document, upload_video))


@run_async
@authenticate_user
def upload_command(update, context):
    """Send instructions for uploading a video"""
    bot = context.bot
    chat_id = update.message.chat_id
    lang = context.user_data.get("language", "en")
    text = _(
        "To upload a video, send me the video file or a link to the video. "
        "Then, you can set the video's title, description, category, "
        "privacy and upload mode using the following commands:\n\n"
        "/settitleprefix <title_prefix> - "
        "Set a prefix to be added to the title of the video\n"
        "/settitlesuffix <title_suffix> - "
        "Set a suffix to be added to the title of the video\n"
        "/setdescription <description> - "
        "Set the description of the video\n"
        "/setcategory <category_id> - "
        "Set the category of the video\n"
        "/setprivacy <private|public|unlisted> - "
        "Set the privacy status of the video\n"
        "/setmode <direct|resumable> - "
        "Set the upload mode to direct or resumable\n\n"
        "You can also cancel the upload at any time by clicking on the 'Cancel Upload' button.\n\n"
        "Note: The maximum file size that can be uploaded is 2GB."
    )

    kb = [[InlineKeyboardButton(_("Cancel Upload"), callback_data="cancel_upload")]]
    keyboard = InlineKeyboardMarkup(kb)
    bot.send_message(chat_id, text=text, reply_markup=keyboard, parse_mode="HTML")
    upload_status(context, _("Waiting for video file or link..."), lang)


@run_async
@authenticate_user
def set_description(update, context):
    """Set the description of the video"""
    lang = context.user_data.get("language", "en")
    user_id = update.effective_user.id

    if "description" in context.user_data:
        del context.user_data["description"]

    if len(context.args) == 0:
        text = _("Please provide a description for the video.")
        context.bot.send_message(user_id, text=text)
        return

    description = " ".join(context.args)
    if len(description) > 1000:
        text = _(
            "The description should not be more than 1000 characters. "
            "Please provide a shorter description."
        )
        context.bot.send_message(user_id, text=text)
        return

    context.user_data["description"] = description
    text = _("The description has been set successfully.")
    context.bot.send_message(user_id, text=text)
