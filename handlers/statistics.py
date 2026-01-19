from aiogram import Router, F
from aiogram.types import Message
from middlewares import AdminMiddleware
import html

router = Router()
router.message.middleware(AdminMiddleware())

MAX_LEN = 3900  # Safe limit (Telegram max is 4096)


@router.message(F.text == "📊 Statistics")
async def show_statistics(message: Message, db):
    """
    Show overall bot statistics.
    """
    chat_stats = await db.get_chat_type_counts()
    broadcast_stats = await db.get_total_broadcast_stats()
    admins = await db.get_all_admins()
    time_stats = await db.get_time_based_broadcast_stats()
    today_admins = await db.get_today_broadcast_admins()

    stats_text = f"""
📊 <b>BOT STATISTICS</b>

💬 <b>Chats:</b>
├ 📺 Channels: <b>{chat_stats['channels']}</b>
├ 👥 Groups: <b>{chat_stats['groups']}</b>
├ 🔥 Supergroups: <b>{chat_stats['supergroups']}</b>
└ 📋 Total: <b>{chat_stats['total']}</b>

📨 <b>Broadcasts by time:</b>
├ 📅 Today: <b>{time_stats['today']}</b>
├ 🗓 This week: <b>{time_stats['week']}</b>
├ 📆 This month: <b>{time_stats['month']}</b>
└ 🧮 Total: <b>{time_stats['total']}</b>

📢 <b>Broadcast results:</b>
├ 📨 Total: <b>{broadcast_stats['total_broadcasts'] or 0}</b>
├ ✅ Successful: <b>{broadcast_stats['total_success'] or 0}</b>
└ ❌ Failed: <b>{broadcast_stats['total_failed'] or 0}</b>

👨‍💼 <b>Total admins:</b> <b>{len(admins)}</b>
"""

    # Admins who sent broadcasts today
    if today_admins:
        stats_text += "\n📅 <b>Admins who sent broadcasts today:</b>\n"

        for admin in today_admins:
            full_name = html.escape(admin.get("full_name") or "Unknown")
            username = f"@{admin['username']}" if admin.get("username") else "no username"
            stats_text += f"• {full_name} — {username}\n"
    else:
        stats_text += "\n📅 No broadcasts were sent today.\n"

    stats_text += (
        f"\n🕒 <b>Last updated:</b> "
        f"{message.date.strftime('%Y-%m-%d %H:%M')}"
    )

    await message.answer(stats_text, parse_mode="HTML")


@router.message(F.text == "📋 Channels")
async def show_channels(message: Message, db):
    """
    Show list of channels.
    """
    channels = await db.get_chats_by_type("channel")

    if not channels:
        return await message.answer(
            "📺 No channels found yet.\n\n"
            "Add the bot as an admin to your channel."
        )

    header = "📺 <b>CHANNELS LIST</b>\n\n"
    text = header

    for idx, channel in enumerate(channels, 1):
        title = html.escape(channel["title"])
        username = f"@{html.escape(channel['username'])}" if channel["username"] else "no username"

        block = (
            f"{idx}. <b>{title}</b>\n"
            f"   🆔 ID: <code>{channel['chat_id']}</code>\n"
            f"   🔗 Username: {username}\n"
            f"   📅 Added on: {channel['added_date'].strftime('%Y-%m-%d')}\n\n"
        )

        if len(text) + len(block) > MAX_LEN:
            await message.answer(text, parse_mode="HTML")
            text = header

        text += block

    if text.strip() != header.strip():
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "👥 Groups")
async def show_groups(message: Message, db):
    """
    Show list of groups.
    """
    groups = await db.get_chats_by_type("group")

    if not groups:
        return await message.answer(
            "👥 No groups found yet.\n\n"
            "Add the bot as an admin to your group."
        )

    header = "👥 <b>GROUPS LIST</b>\n\n"
    text = header

    for idx, group in enumerate(groups, 1):
        title = html.escape(group["title"])
        username = f"@{html.escape(group['username'])}" if group["username"] else "no username"

        block = (
            f"{idx}. <b>{title}</b>\n"
            f"   🆔 ID: <code>{group['chat_id']}</code>\n"
            f"   🔗 Username: {username}\n"
            f"   📅 Added on: {group['added_date'].strftime('%Y-%m-%d')}\n\n"
        )

        if len(text) + len(block) > MAX_LEN:
            await message.answer(text, parse_mode="HTML")
            text = header

        text += block

    if text.strip() != header.strip():
        await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🔥 Supergroups")
async def show_supergroups(message: Message, db):
    """
    Show list of supergroups.
    """
    supergroups = await db.get_chats_by_type("supergroup")

    if not supergroups:
        return await message.answer(
            "🔥 No supergroups found yet.\n\n"
            "Add the bot as an admin to your supergroup."
        )

    header = "🔥 <b>SUPERGROUPS LIST</b>\n\n"
    text = header

    for idx, group in enumerate(supergroups, 1):
        title = html.escape(group["title"])
        username = f"@{html.escape(group['username'])}" if group.get("username") else "no username"

        block = (
            f"{idx}. <b>{title}</b>\n"
            f"   🆔 ID: <code>{group['chat_id']}</code>\n"
            f"   🔗 Username: {username}\n"
            f"   📅 Added on: {group['added_date'].strftime('%Y-%m-%d')}\n\n"
        )

        if len(text) + len(block) > MAX_LEN:
            await message.answer(text, parse_mode="HTML")
            text = header

        text += block

    if text.strip() != header.strip():
        await message.answer(text, parse_mode="HTML")
