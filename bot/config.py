import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_NAME = os.environ.get("SESSION_NAME", "tg2tubebot")
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
BOT_OWNER = int(os.environ.get("BOT_OWNER"))
AUTH_USERS = [int(user_id) for user_id in os.environ.get("AUTH_USERS", "").split(",") if user_id]
VIDEO_DESCRIPTION = os.environ.get("VIDEO_DESCRIPTION", "")
VIDEO_CATEGORY = os.environ.get("VIDEO_CATEGORY", "")
VIDEO_TITLE_PREFIX = os.environ.get("VIDEO_TITLE_PREFIX", "")
VIDEO_TITLE_SUFFIX = os.environ.get("VIDEO_TITLE_SUFFIX", "")
UPLOAD_MODE = os.environ.get("UPLOAD_MODE", "private")
DEBUG = os.environ.get("DEBUG", "").lower() in ["true", "yes", "1"]
