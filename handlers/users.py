from aiogram import Router, F
from aiogram.types import Message

router = Router()

MAX_LEN = 3800  # Safe limit to avoid Telegram message overflow


@router.message(F.text == "👤 Users")
async def list_users(message: Message, db):
    """
    Display the list of all registered users.
    """
    users = await db.get_all_users()

    if not users:
        return await message.answer("❌ No users found in the database.")

    header = "👤 <b>Users list:</b>\n\n"
    text = header

    for idx, user in enumerate(users, 1):
        username = f"@{user['username']}" if user["username"] else "❌ no username"

        line = (
            f"{idx}. 👤 <b>{user['full_name']}</b>\n"
            f"🆔 <code>{user['user_id']}</code>\n"
            f"📛 {username}\n"
            f"⏱ First seen: {user['first_seen']:%Y-%m-%d %H:%M}\n\n"
        )

        # Send partial message if Telegram limit is reached
        if len(text) + len(line) > MAX_LEN:
            await message.answer(text, parse_mode="HTML")
            text = header

        text += line

    # Send remaining part
    if text.strip() != header.strip():
        await message.answer(text, parse_mode="HTML")

    await message.answer(
        f"📊 Total users: <b>{len(users)}</b>",
        parse_mode="HTML"
    )
