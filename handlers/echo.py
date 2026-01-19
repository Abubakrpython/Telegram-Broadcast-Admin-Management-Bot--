from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def echo_all(message: Message):
    """
    Fallback handler that echoes any incoming message.
    Useful for testing and debugging purposes.
    """

    # Text message
    if message.text:
        await message.answer(message.text)
        return

    # Photo
    if message.photo:
        await message.answer_photo(
            message.photo[-1].file_id,
            caption=message.caption or ""
        )
        return

    # Video
    if message.video:
        await message.answer_video(
            message.video.file_id,
            caption=message.caption or ""
        )
        return

    # Document (pdf, zip, etc.)
    if message.document:
        await message.answer_document(
            message.document.file_id,
            caption=message.caption or ""
        )
        return

    # Audio
    if message.audio:
        await message.answer_audio(
            message.audio.file_id,
            caption=message.caption or ""
        )
        return

    # Voice message
    if message.voice:
        await message.answer_voice(
            message.voice.file_id
        )
        return

    # Video note (round video)
    if message.video_note:
        await message.answer_video_note(
            message.video_note.file_id
        )
        return

    # Sticker
    if message.sticker:
        await message.answer_sticker(
            message.sticker.file_id
        )
        return
