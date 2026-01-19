import asyncio
from typing import List, Dict
from aiogram import Bot
from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest


async def send_copy(bot: Bot, chat_id: int, msg: Message):
    """
    Send a message as a COPY (without forwarding metadata).
    Supports text, photo, video and document.
    """

    if msg.photo:
        return await bot.send_photo(
            chat_id=chat_id,
            photo=msg.photo[-1].file_id,
            caption=msg.caption or "",
            parse_mode="HTML"
        )

    if msg.video:
        return await bot.send_video(
            chat_id=chat_id,
            video=msg.video.file_id,
            caption=msg.caption or "",
            parse_mode="HTML"
        )

    if msg.document:
        return await bot.send_document(
            chat_id=chat_id,
            document=msg.document.file_id,
            caption=msg.caption or "",
            parse_mode="HTML"
        )

    if msg.text:
        return await bot.send_message(
            chat_id=chat_id,
            text=msg.text,
            parse_mode="HTML"
        )

    return None


async def send_forward(bot: Bot, chat_id: int, msg: Message):
    """
    Send a message using Telegram FORWARD (keeps original metadata).
    """
    return await bot.forward_message(
        chat_id=chat_id,
        from_chat_id=msg.chat.id,
        message_id=msg.message_id
    )


async def send_message_to_chat(
    bot: Bot,
    chat_id: int,
    message: Message,
    send_mode: str = "copy",  # "copy" | "forward"
    album_group: List[Message] | None = None
) -> bool:
    """
    Universal message sender.
    Returns True if the message was sent successfully, otherwise False.
    """

    try:
        # ❌ Media groups (albums) are not supported
        if album_group and len(album_group) > 1:
            return False

        # 1) Force FORWARD mode
        if send_mode == "forward":
            await send_forward(bot, chat_id, message)
            return True

        # 2) Default COPY mode
        await send_copy(bot, chat_id, message)
        return True

    except (TelegramForbiddenError, TelegramBadRequest):
        # Bot has no permission or chat is unavailable
        return False

    except Exception as e:
        return False


async def broadcast_message(
    bot: Bot,
    chats: List[Dict],
    message: Message,
    send_mode: str = "copy",
    album_group: List[Message] | None = None
) -> Dict[str, int]:
    """
    Send a message to multiple chats.
    Returns statistics about success and failure counts.
    """

    success = 0
    failed = 0

    for chat in chats:
        chat_id = chat["chat_id"]

        if await send_message_to_chat(
            bot=bot,
            chat_id=chat_id,
            message=message,
            send_mode=send_mode,
            album_group=album_group
        ):
            success += 1
        else:
            failed += 1

        # Rate limiting to avoid Telegram flood limits
        await asyncio.sleep(0.05)

    return {
        "total": len(chats),
        "success": success,
        "failed": failed
    }


async def broadcast_to_selected(
    bot: Bot,
    chat_ids: List[int],
    message: Message,
    album_group: List[Message] | None = None
) -> Dict[str, int]:
    """
    Send a message to a specific list of chat IDs.
    """

    success = 0
    failed = 0

    for chat_id in chat_ids:
        if await send_message_to_chat(
            bot=bot,
            chat_id=chat_id,
            message=message,
            album_group=album_group
        ):
            success += 1
        else:
            failed += 1

        await asyncio.sleep(0.05)

    return {
        "total": len(chat_ids),
        "success": success,
        "failed": failed
    }
