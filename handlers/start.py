from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards import main_admin_menu, get_official_channels_keyboard
import config

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, bot, db):
    """
    Handle /start command.
    Registers user, detects role (admin / super admin / user)
    and sends the appropriate welcome message.
    """
    user = message.from_user

    # 1️⃣ Save or update user in database
    is_new = await db.add_user(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name
    )

    # 2️⃣ Load admins and super admins
    admins = await db.get_all_admins()
    super_admins = await db.get_all_super_admins()

    # 3️⃣ Notify admins about a new user
    if is_new:
        for admin in admins:
            try:
                await bot.send_message(
                    admin["user_id"],
                    (
                        "🟢 <b>New user started the bot</b>\n\n"
                        f"👤 Name: {user.full_name}\n"
                        f"🆔 ID: <code>{user.id}</code>\n"
                        f"🔗 Username: @{user.username or 'none'}"
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                pass

    # 4️⃣ Check roles
    is_admin = await db.is_admin(user.id)
    is_super_admin = await db.is_super_admin(user.id)

    # 5️⃣ ADMIN / SUPER ADMIN FLOW
    if is_admin or is_super_admin:
        text = (
            f"👋 Welcome, {user.full_name}!\n\n"
            f"✅ You have logged in as "
            f"{'SUPER ADMIN' if is_super_admin else 'ADMIN'}."
        )

        await message.answer(
            text,
            reply_markup=main_admin_menu()
        )

        # Notify other admins about admin login
        for admin in admins:
            if admin["user_id"] != user.id:
                try:
                    await bot.send_message(
                        admin["user_id"],
                        (
                            "🔵 <b>Admin logged in</b>\n\n"
                            f"👤 Name: {user.full_name}\n"
                            f"🆔 ID: <code>{user.id}</code>\n"
                            f"🔗 Username: @{user.username or 'none'}\n"
                            f"⭐ Role: {'SUPER ADMIN' if is_super_admin else 'ADMIN'}"
                        ),
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

        return  # ⛔ Important: stop further processing

    # 6️⃣ REGULAR USER FLOW
    await message.answer(
        (
            "<b>👋 Welcome!</b>\n\n"
            "Dear user, here is a list of official educational "
            "and informational channels for you."
        ),
        reply_markup=get_official_channels_keyboard(),
        parse_mode="HTML"
    )

    # 7️⃣ Notify admins about regular user login
    for admin in admins:
        try:
            await bot.send_message(
                admin["user_id"],
                (
                    "👤 <b>Regular user started the bot</b>\n\n"
                    f"Name: {user.full_name}\n"
                    f"ID: <code>{user.id}</code>\n"
                    f"Username: @{user.username or 'none'}"
                ),
                parse_mode="HTML"
            )
        except Exception:
            pass


@router.message(F.text == "🔙 Back")
async def back_to_menu(message: Message, db):
    """
    Return to the main admin menu.
    """
    is_admin = await db.is_admin(message.from_user.id)

    if not is_admin:
        return await message.answer("❌ You do not have admin permissions.")

    await message.answer(
        "📋 Main menu:",
        reply_markup=main_admin_menu()
    )


@router.message(F.text == "❓ Help")
async def help_command(message: Message):
    """
    Show help information.
    """
    help_text = """
❓ <b>H E L P</b>

<b>📌 Bot features:</b>

1️⃣ <b>Channels, Groups and Supergroups</b>
   • Automatically added when the bot becomes an admin  
   • 📋 Channels list  
   • 👥 Groups list  
   • 🔥 Supergroups list  

2️⃣ <b>Broadcast messaging</b>
   • 📢 Send to all  
   • 📺 Channels only  
   • 👥 Groups only  
   • 🔥 Supergroups only  
   • 🎯 Manual selection  
   • 🔄 Forward or 📄 Copy mode  
   • 🖼 Photos, videos and documents supported  
   • 🔐 Protected with PIN code  

3️⃣ <b>Statistics</b>
   • 📊 Chat statistics  
   • 📨 Broadcast history  
   • 👨‍💼 Admins who sent messages today  

4️⃣ <b>Admin panel</b>
   • 👨‍💼 Admin list — “Admins” button  
   • 🔐 PIN management:  
        • View: /my_pin  
        • Change: /change_pin  

⚠️ <b>About PIN:</b>  
• PIN consists of 4 digits  
• Used for security during broadcasts  
• Each admin has a unique PIN  

🤖 <b>If you find a bug or an issue, please contact the super admin.</b>
"""
    await message.answer(help_text, parse_mode="HTML")
