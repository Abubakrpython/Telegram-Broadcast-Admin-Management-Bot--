from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery


class BlockGroupMessagesMiddleware(BaseMiddleware):
    """
    Middleware that blocks all messages and callbacks
    coming from groups and supergroups.
    """

    async def __call__(self, handler, event, data):

        chat = None

        # Message event
        if isinstance(event, Message):
            chat = event.chat

        # CallbackQuery event
        elif isinstance(event, CallbackQuery):
            if event.message:
                chat = event.message.chat

        # Block execution if the chat is a group or supergroup
        if chat and chat.type in ("group", "supergroup"):
            return  # ❌ Handler will not be executed

        # Otherwise, continue processing
        return await handler(event, data)
