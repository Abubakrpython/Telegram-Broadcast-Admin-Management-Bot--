from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from keyboards import (
    admin_list_keyboard,
    main_admin_menu,
    cancel_keyboard
)
from utils import AdminStates
from middlewares import AdminMiddleware

router = Router()
router.message.middleware(AdminMiddleware())

# ======================================================================
# ADMIN LIST
# ======================================================================

@router.message(F.text == "👨‍💼 Admins")
async def show_admins(message: Message, db):
    admins = await db.get_all_admins()
    super_admins = await db.get_all_super_admins()

    super_admin_ids = {a["user_id"] for a in super_admins}

    if not admins:
        return await message.answer("❌ No admins found!")

    text = "👨‍💼 <b>ADMINS LIST</b>\n\n"

    for idx, admin in enumerate(admins, 1):
        username = admin.get("username")
        full_name = admin.get("full_name") or "Unknown"
        user_id = admin["user_id"]
        date = admin["added_date"].strftime("%d.%m.%Y")

        text += f"{idx}. "
        text += f"@{username}" if username else full_name
        text += f"\n🆔 <code>{user_id}</code>\n📅 Added: {date}\n"

        if user_id in super_admin_ids:
            text += "👑 <b>Super Admin</b>\n"

        text += "\n"

    text += (
        "\n➕ Add admin: /add_admin\n"
        "➖ Remove admin: /remove_admin\n"
    )

    await message.answer(text, parse_mode="HTML")

# ======================================================================
# SUPER ADMINS LIST
# ======================================================================

@router.message(F.text == "/list_superadmins")
async def list_super_admins(message: Message, db):
    super_admins = await db.get_all_super_admins()

    if not super_admins:
        return await message.answer("❌ No super admins found!")

    text = "👑 <b>SUPER ADMINS</b>\n\n"

    for i, admin in enumerate(super_admins, 1):
        text += (
            f"{i}. 🆔 <code>{admin['user_id']}</code>\n"
            f"📅 Added: {admin['added_date'].strftime('%d.%m.%Y')}\n\n"
        )

    await message.answer(text, parse_mode="HTML")

# ======================================================================
# ADD ADMIN
# ======================================================================

@router.message(F.text == "/add_admin")
async def add_admin_start(message: Message, state: FSMContext, db):
    if not await db.is_super_admin(message.from_user.id):
        return await message.answer(
            "⛔ Only <b>Super Admin</b> can add admins!",
            parse_mode="HTML"
        )

    await message.answer(
        "👨‍💼 <b>Add new admin</b>\n\n"
        "Send user ID of the new admin:\n"
        "Example: <code>123456789</code>\n\n"
        "❌ Press Cancel or send /cancel",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

    await state.set_state(AdminStates.add_admin)


@router.message(AdminStates.add_admin)
async def process_add_admin(message: Message, state: FSMContext, db):
    if message.text in ["/cancel", "❌ Cancel"]:
        await message.answer(
            "❌ Process cancelled",
            reply_markup=main_admin_menu()
        )
        await state.clear()
        return

    try:
        new_admin_id = int(message.text)
    except ValueError:
        return await message.answer("❌ Invalid ID! Only numbers allowed.")

    if await db.is_admin(new_admin_id):
        return await message.answer("⚠ This user is already an admin!")

    pin = await db.add_admin(new_admin_id)

    await message.answer(
        "✅ <b>Admin successfully added!</b>\n\n"
        f"🆔 ID: <code>{new_admin_id}</code>\n"
        f"🔐 PIN: <code>{pin}</code>",
        parse_mode="HTML",
        reply_markup=main_admin_menu()
    )

    # Notify new admin
    try:
        await message.bot.send_message(
            new_admin_id,
            "🎉 <b>Congratulations!</b>\n\n"
            "You have been added as an <b>Admin</b> ✅\n\n"
            f"🔐 Your PIN code: <code>{pin}</code>\n"
            "❗ Keep your PIN secret!",
            reply_markup=main_admin_menu(),
            parse_mode="HTML"
        )
    except:
        pass

    # Notify super admins
    for admin in await db.get_all_super_admins():
        try:
            await message.bot.send_message(
                admin["user_id"],
                f"🆕 <b>New admin added</b>\n\n"
                f"🆔 ID: <code>{new_admin_id}</code>\n"
                f"➕ Added by: {message.from_user.full_name}",
                parse_mode="HTML"
            )
        except:
            pass

    await state.clear()

# ======================================================================
# REMOVE ADMIN
# ======================================================================

@router.message(F.text == "/remove_admin")
async def remove_admin_start(message: Message, state: FSMContext, db):
    if not await db.is_super_admin(message.from_user.id):
        return await message.answer(
            "⛔ Only <b>Super Admin</b> can remove admins!",
            parse_mode="HTML"
        )

    admins = await db.get_all_admins()
    super_ids = {a["user_id"] for a in await db.get_all_super_admins()}
    removable = [a for a in admins if a["user_id"] not in super_ids]

    if not removable:
        return await message.answer("❌ No removable admins found!")

    text = "👨‍💼 <b>Send admin ID to remove:</b>\n\n"

    for admin in removable:
        text += (
            f"👤 {admin.get('full_name') or 'Unknown'}\n"
            f"🆔 <code>{admin['user_id']}</code>\n\n"
        )

    await message.answer(
        text + "❌ Cancel: /cancel",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

    await state.set_state(AdminStates.remove_admin)


@router.message(AdminStates.remove_admin)
async def process_remove_admin(message: Message, state: FSMContext, db):
    if message.text in ["/cancel", "❌ Cancel"]:
        await message.answer(
            "❌ Cancelled",
            reply_markup=main_admin_menu()
        )
        await state.clear()
        return

    try:
        admin_id = int(message.text)
    except ValueError:
        return await message.answer("❌ Invalid ID format!")

    if await db.is_super_admin(admin_id):
        return await message.answer("⛔ Super Admin cannot be removed!")

    if not await db.is_admin(admin_id):
        return await message.answer("❌ Admin not found!")

    await db.remove_admin(admin_id)

    await message.answer(
        f"✅ <b>Admin removed!</b>\n\n🆔 <code>{admin_id}</code>",
        reply_markup=main_admin_menu(),
        parse_mode="HTML"
    )

    try:
        await message.bot.send_message(
            admin_id,
            "⛔ <b>You have been removed from admin role.</b>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML"
        )
    except:
        pass

    for sa in await db.get_all_super_admins():
        try:
            await message.bot.send_message(
                sa["user_id"],
                f"➖ <b>Admin removed</b>\n\n"
                f"🆔 <code>{admin_id}</code>\n"
                f"👤 Removed by: {message.from_user.full_name}",
                parse_mode="HTML"
            )
        except:
            pass

    await state.clear()

# ======================================================================
# PIN MANAGEMENT
# ======================================================================

@router.message(F.text == "/my_pin")
async def show_my_pin(message: Message, db):
    if not await db.is_admin(message.from_user.id):
        return await message.answer("❌ You are not an admin!")

    pin = await db.get_admin_pin(message.from_user.id)
    await message.answer(
        f"🔐 Your PIN code:\n\n<code>{pin}</code>",
        parse_mode="HTML"
    )


@router.message(F.text == "/change_pin")
async def change_pin_start(message: Message, state: FSMContext, db):
    await message.answer(
        "Enter your current PIN:",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(AdminStates.verify_old_pin)


@router.message(AdminStates.verify_old_pin, F.text.regexp(r"^\d{4}$"))
async def verify_old_pin(message: Message, state: FSMContext, db):
    if not await db.verify_pin(message.from_user.id, message.text):
        return await message.answer("❌ Incorrect PIN!")

    await message.answer("Enter new PIN (4 digits):")
    await state.set_state(AdminStates.change_pin)


@router.message(AdminStates.change_pin, F.text.regexp(r"^\d{4}$"))
async def save_new_pin(message: Message, state: FSMContext, db):
    await db.update_pin(message.from_user.id, message.text)

    await message.answer(
        "✅ PIN updated successfully!",
        reply_markup=main_admin_menu()
    )
    await state.clear()

# ======================================================================
# CANCEL HANDLER
# ======================================================================

@router.message(F.text.in_(["❌ Cancel", "/cancel"]))
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Cancelled.",
        reply_markup=main_admin_menu()
    )
