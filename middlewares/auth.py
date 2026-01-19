from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


class AdminMiddleware(BaseMiddleware):
    """
    Middleware that allows access only to admins.
    """

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:

        db = data["db"]      # ⭐ get database instance from context
        user_id = event.from_user.id

        # Check if the user is an admin
        is_admin = await db.is_admin(user_id)

        if not is_admin:
            if isinstance(event, Message):
                await event.answer(
                    "❌ You do not have permission to perform this action."
                )
            else:
                await event.answer(
                    "❌ You do not have permission to perform this action.",
                    show_alert=True
                )
            return

        # User is admin → continue handler execution
        return await handler(event, data)

class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware that injects the database instance into handler context.
    """

    def __init__(self, db):
        self.db = db

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ):
        # Inject database instance into context
        data["db"] = self.db
        return await handler(event, data)
