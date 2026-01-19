from aiogram import Router
from aiogram.types import ChatMemberUpdated

router = Router()


@router.my_chat_member()
async def on_bot_added(event: ChatMemberUpdated, db):
    """
    Handles bot being added to or removed from a chat.
    - When the bot becomes an administrator → saves chat to database and notifies admins
    - When the bot is removed → deletes chat from database and notifies admins
    """

    chat = event.chat
    new_status = event.new_chat_member.status
    old_status = event.old_chat_member.status

    # ❌ Ignore forum groups
    if getattr(chat, "is_forum", False):
        return

    # =========================================================================
    #  ➕ BOT BECAME ADMIN
    # =========================================================================
    if new_status == "administrator" and old_status in ("member", "restricted", "left", "kicked"):

        # Detect chat type
        if chat.type == "channel":
            chat_type = "channel"
            type_name = "Channel"
        elif chat.type == "supergroup":
            chat_type = "supergroup"
            type_name = "Supergroup"
        else:
            chat_type = "group"
            type_name = "Group"

        # Invite link
        invite_link = getattr(chat, "invite_link", None) or "❌ Invite link not available"

        # Description
        description = chat.description or "❌ No description"

        # Save chat to database
        await db.add_chat(
            chat_id=chat.id,
            chat_type=chat_type,
            title=chat.title,
            username=chat.username,
            invite_link=invite_link,
            description=description
        )

        # Statistics
        stats = await db.get_chat_stats()
        total_places = stats["total"]

        username_display = f"@{chat.username}" if chat.username else "❌ No username"
        link = f"https://t.me/{chat.username}" if chat.username else "❌ No link"

        try:
            members = await event.bot.get_chat_member_count(chat.id)
        except Exception:
            members = "❌ Could not fetch"

        text = (
            f"✅ Bot became <b>ADMIN</b> in a <b>{type_name.lower()}</b>!\n\n"
            f"🏷 <b>Title:</b> {chat.title}\n"
            f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
            f"🔗 <b>Username:</b> {username_display}\n"
            f"🌍 <b>Link:</b> {link}\n"
            f"📝 <b>Description:</b> {description}\n"
            f"📨 <b>Invite link:</b> {invite_link}\n"
            f"👥 <b>Members:</b> {members}\n\n"
            f"📊 <b>Total chats in database:</b> {total_places}"
        )

        admins = await db.get_all_admins()
        for admin in admins:
            try:
                await event.bot.send_message(admin["user_id"], text, parse_mode="HTML")
            except Exception:
                pass


    # =========================================================================
    #  ➖ BOT REMOVED FROM CHAT
    # =========================================================================
    elif new_status in ("left", "kicked") and old_status == "administrator":

        if chat.type == "channel":
            type_name = "channel"
        elif chat.type == "supergroup":
            type_name = "supergroup"
        else:
            type_name = "group"

        username_display = f"@{chat.username}" if chat.username else "❌ No username"
        link = f"https://t.me/{chat.username}" if chat.username else "❌ No link"
        description = chat.description or "❌ No description"
        invite_link = getattr(chat, "invite_link", None) or "❌ Invite link not available"

        # Remove chat from database
        await db.delete_chat(chat.id)

        stats = await db.get_chat_stats()
        total_places = stats["total"]

        try:
            members = await event.bot.get_chat_member_count(chat.id)
        except Exception:
            members = "❌ Could not fetch"

        text = (
            f"❌ Bot was <b>REMOVED</b> from a <b>{type_name}</b>!\n\n"
            f"🏷 <b>Title:</b> {chat.title}\n"
            f"🆔 <b>ID:</b> <code>{chat.id}</code>\n"
            f"🔗 <b>Username:</b> {username_display}\n"
            f"🌍 <b>Link:</b> {link}\n"
            f"📝 <b>Description:</b> {description}\n"
            f"📨 <b>Invite link:</b> {invite_link}\n"
            f"👥 <b>Members:</b> {members}\n\n"
            f"📊 <b>Total chats in database:</b> {total_places}"
        )

        admins = await db.get_all_admins()
        for admin in admins:
            try:
                await event.bot.send_message(admin["user_id"], text, parse_mode="HTML")
            except Exception:
                pass

