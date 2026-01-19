from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from middlewares import AdminMiddleware
from keyboards import cancel_keyboard, main_admin_menu
from utils import AdminStates
import html
import config
import asyncio
from datetime import datetime

router = Router()
router.message.middleware(AdminMiddleware())

MAX_LEN = 3800  # Safe Telegram message limit


# ===================== 🗑 DELETE CHAT (WITH PIN) =====================
@router.message(F.text == "🗑 Delete Chat")
async def delete_chat_start(message: Message, state: FSMContext, db):
    """
    Start chat deletion process (super admin only).
    """
    if not await db.is_super_admin(message.from_user.id):
        return await message.answer(
            "⛔ This action is allowed for <b>Super Admins</b> only!",
            parse_mode="HTML",
            reply_markup=main_admin_menu()
        )

    await message.answer(
        "🗑 <b>Delete chat</b>\n\n"
        "Please send the chat ID you want to delete:\n"
        "Example: <code>-1001234567890</code>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.delete_chat_id)


@router.message(AdminStates.delete_chat_id)
async def get_chat_id_for_delete(message: Message, state: FSMContext, db):
    """
    Receive chat ID and validate it.
    """
    if message.text == "❌ Cancel":
        await message.answer(
            "❌ Operation cancelled.",
            reply_markup=main_admin_menu()
        )
        await state.clear()
        return

    try:
        chat_id = int(message.text)
    except ValueError:
        await message.answer("❌ Chat ID must be a number!")
        return

    chat = await db.get_chat_by_id(chat_id)

    if not chat:
        await message.answer("❌ Chat not found!")
        await state.clear()
        return

    await state.update_data(chat_id=chat_id)

    await message.answer(
        f"⚠️ <b>The following chat will be deleted:</b>\n\n"
        f"📛 Title: <b>{html.escape(chat['title'])}</b>\n"
        f"🆔 ID: <code>{chat_id}</code>\n\n"
        f"🔐 Enter your PIN code to continue:",
        parse_mode="HTML"
    )

    await state.set_state(AdminStates.delete_chat_pin)


@router.message(AdminStates.delete_chat_pin, F.text.regexp(r"^\d{4}$"))
async def confirm_delete_with_pin(message: Message, state: FSMContext, db):
    """
    Confirm chat deletion using PIN code.
    """
    if not await db.is_super_admin(message.from_user.id):
        await message.answer(
            "⛔ This action is allowed for <b>Super Admins</b> only!",
            reply_markup=main_admin_menu(),
            parse_mode="HTML"
        )
        await state.clear()
        return

    admin_id = message.from_user.id
    pin = message.text.strip()

    data = await state.get_data()
    chat_id = data["chat_id"]

    if not await db.verify_pin(admin_id, pin):
        await message.answer(
            "❌ Invalid PIN!",
            reply_markup=main_admin_menu()
        )
        await state.clear()
        return

    chat = await db.get_chat_by_id(chat_id)

    # Delete chat from database
    await db.delete_chat(chat_id)

    # Make bot leave the chat
    try:
        await message.bot.leave_chat(chat_id)
        leave_text = "✅ Bot has left the chat."
    except Exception:
        leave_text = "⚠️ Bot could not leave the chat."

    await message.answer(
        f"✅ <b>Chat deleted successfully!</b>\n\n"
        f"📛 {html.escape(chat['title'])}\n"
        f"🆔 <code>{chat_id}</code>\n"
        f"{leave_text}",
        reply_markup=main_admin_menu(),
        parse_mode="HTML"
    )

    # ================= LOG =================
    log_text = (
        "🗑 <b>CHAT DELETED</b>\n\n"
        f"👤 Deleted by: {message.from_user.full_name}\n"
        f"🆔 Admin ID: <code>{admin_id}</code>\n"
        f"📛 Chat: <b>{html.escape(chat['title'])}</b>\n"
        f"🆔 Chat ID: <code>{chat_id}</code>\n"
        f"📌 Type: <b>{chat['chat_type']}</b>\n"
        f"🕒 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    await message.bot.send_message(config.LOG_CHANNEL_ID, log_text, parse_mode="HTML")

    super_admins = await db.get_all_super_admins()
    for sa in super_admins:
        try:
            await message.bot.send_message(sa["user_id"], log_text, parse_mode="HTML")
        except Exception:
            pass

    await state.clear()


@router.message(AdminStates.delete_chat_pin)
async def wrong_pin_format(message: Message):
    """
    Handle incorrect PIN format.
    """
    await message.answer("❌ PIN must consist of exactly 4 digits!")


# ===================== MAINTENANCE COMMANDS =====================

@router.message(F.text == "/clean_chats")
async def clean_inactive_chats(message: Message, db):
    """
    Remove inactive chats from the database.
    """
    deleted = await db.execute(
        "DELETE FROM chats WHERE is_active = FALSE"
    )

    await message.answer(
        f"🧹 Cleanup completed!\n\n"
        f"Deleted chats: {deleted}"
    )


@router.message(F.text == "/no_write_chats")
async def no_write_chats(message: Message, bot, db):
    """
    Check chats where the bot does not have write permissions.
    (Super admin only)
    """
    if not await db.is_super_admin(message.from_user.id):
        return await message.answer("⛔ Only super admins can view this information!")

    chats = await db.get_all_chats()
    no_access = []

    async def check_chat(chat):
        chat_id = chat["chat_id"]
        title = chat.get("title") or "Unknown"
        chat_type = chat.get("chat_type")

        try:
            bot_member = await asyncio.wait_for(
                bot.get_chat_member(chat_id, bot.id),
                timeout=5
            )

            status = bot_member.status
            rights = getattr(bot_member, "privileges", None)

            if status != "administrator":
                return chat_id, title, chat_type, "Bot is not an admin"

            if not rights:
                return chat_id, title, chat_type, "Permissions could not be determined"

            if chat_type == "channel" and not rights.can_post_messages:
                return chat_id, title, chat_type, "No permission to post messages"

            if chat_type in ("group", "supergroup") and not rights.can_send_messages:
                return chat_id, title, chat_type, "No permission to send messages"

            return None

        except asyncio.TimeoutError:
            return chat_id, title, chat_type, "Request timed out"

        except Exception as e:
            err = str(e).lower()

            if "kicked" in err:
                reason = "Bot was kicked"
            elif "forbidden" in err:
                reason = "Bot was blocked"
            elif "not enough rights" in err:
                reason = "Insufficient permissions"
            elif "chat not found" in err:
                reason = "Chat not found"
            else:
                reason = "Unknown error"

            return chat_id, title, chat_type, reason

    tasks = [check_chat(chat) for chat in chats]
    results = await asyncio.gather(*tasks)

    for item in results:
        if item:
            no_access.append(item)

    if not no_access:
        return await message.answer("✅ The bot has write permissions in all chats.")

    header = "🚫 <b>CHATS WITH NO WRITE PERMISSION</b>\n\n"
    text = header

    for i, (cid, title, chat_type, reason) in enumerate(no_access, 1):
        block = (
            f"{i}. <b>{html.escape(title)}</b>\n"
            f"🆔 <code>{cid}</code>\n"
            f"📌 Type: {chat_type}\n"
            f"⚠ Reason: {reason}\n\n"
        )

        if len(text) + len(block) > MAX_LEN:
            await message.answer(text, parse_mode="HTML")
            text = header

        text += block

    if text.strip() != header.strip():
        await message.answer(text, parse_mode="HTML")

    await message.answer(
        f"📊 Total: <b>{len(no_access)}</b> chats where the bot cannot write.",
        parse_mode="HTML"
    )
