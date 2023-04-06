from aiogram import types
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware


class AuthMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self):
        super().__init__()
        self.auth_users = [int(user_id) for user_id in os.getenv("AUTH_USERS", "").split(",") if user_id]

    async def pre_process(self, obj, data, *args):
        if not isinstance(obj, types.Update):
            return
        if obj.message and obj.message.from_user.id not in self.auth_users:
            await obj.message.reply("You are not authorized to use this bot.")
            raise CancelHandler()
        if obj.callback_query and obj.callback_query.from_user.id not in self.auth_users:
            await obj.callback_query.answer("You are not authorized to use this bot.")
            raise CancelHandler()
