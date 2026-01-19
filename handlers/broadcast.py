import asyncio
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import config
from keyboards import (
    broadcast_menu,
    cancel_keyboard,
    main_admin_menu,
    confirm_broadcast,
    chat_selection_keyboard,
    chat_type_selection_keyboard
)
from utils import BroadcastStates
from middlewares import AdminMiddleware

router = Router()
router.message.middleware(AdminMiddleware())

# ======================================================================
# MAIN BROADCAST MENU
# ======================================================================

@router.message(F.text == "📢 Send broadcast")
async def broadcast_menu_handler(message: Message):
    await message.answer(
        "📢 <b>Broadcast message</b>\n\n"
        "Choose where you want to send the message:",
        reply_markup=broadcast_menu()
    )

# ======================================================================
# TARGET SELECTION
# ======================================================================

@router.message(F.text == "📢 Send to all")
async def broadcast_to_all(message: Message, state: FSMContext):
    await message.answer("📝 Send your message.", reply_markup=cancel_keyboard())
    await state.set_state(BroadcastStates.waiting_for_message)
    await state.update_data(target="all")


@router.message(F.text == "📺 Channels only")
async def broadcast_to_channels(message: Message, state: FSMContext, db):
    channels = await db.get_chats_by_type("channel")

    if not channels:
        return await message.answer("❌ No channels found!")

    await message.answer(
        f"📺 Message will be sent to {len(channels)} channels.\n\n"
        "📝 Send your message.",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(BroadcastStates.waiting_for_message)
    await state.update_data(target="channels")


@router.message(F.text == "👥 Groups only")
async def broadcast_to_groups(message: Message, state: FSMContext, db):
    groups = await db.get_chats_by_type("group")

    if not groups:
        return await message.answer("❌ No groups found!")

    await message.answer(
        f"👥 Message will be sent to {len(groups)} groups.\n\n"
        "📝 Send your message.",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(BroadcastStates.waiting_for_message)
    await state.update_data(target="groups")


@router.message(F.text == "🔥 Supergroups only")
async def broadcast_to_supergroups(message: Message, state: FSMContext, db):
    supergroups = await db.get_chats_by_type("supergroup")

    if not supergroups:
        return await message.answer("❌ No supergroups found!")

    await message.answer(
        f"🔥 Message will be sent to {len(supergroups)} supergroups.\n\n"
        "📝 Send your message.",
        reply_markup=cancel_keyboard()
    )
    await state.set_state(BroadcastStates.waiting_for_message)
    await state.update_data(target="supergroups")


@router.message(F.text == "🎯 Select manually")
async def broadcast_select_type(message: Message, state: FSMContext):
    await message.answer(
        "🎯 Select chat type:",
        reply_markup=chat_type_selection_keyboard()
    )
    await state.set_state(BroadcastStates.selecting_chats)

# ======================================================================
# CHAT SELECTION (INLINE)
# ======================================================================

@router.callback_query(BroadcastStates.selecting_chats, F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer("❌ Cancelled")
    await callback.message.edit_text("❌ Process cancelled.")
    await callback.message.answer(
        "📋 Main menu:",
        reply_markup=main_admin_menu()
    )
    await state.clear()


@router.callback_query(BroadcastStates.selecting_chats, F.data == "select_channels")
async def select_channels(callback: CallbackQuery, state: FSMContext, db):
    channels = await db.get_chats_by_type("channel")
    await callback.answer()

    if not channels:
        return await callback.message.edit_text("❌ No channels found!")

    await state.update_data(available_chats=channels, selected_chat_ids=[])
    await callback.message.edit_text(
        f"📺 Channels ({len(channels)}):",
        reply_markup=chat_selection_keyboard(channels, [])
    )


@router.callback_query(BroadcastStates.selecting_chats, F.data == "select_groups")
async def select_groups(callback: CallbackQuery, state: FSMContext, db):
    groups = await db.get_chats_by_type("group")
    await callback.answer()

    if not groups:
        return await callback.message.edit_text("❌ No groups found!")

    await state.update_data(available_chats=groups, selected_chat_ids=[])
    await callback.message.edit_text(
        f"👥 Groups ({len(groups)}):",
        reply_markup=chat_selection_keyboard(groups, [])
    )


@router.callback_query(BroadcastStates.selecting_chats, F.data == "select_all_chats")
async def select_all_chats(callback: CallbackQuery, state: FSMContext, db):
    chats = await db.get_all_chats()
    await callback.answer()

    if not chats:
        return await callback.message.edit_text("❌ No chats found!")

    await state.update_data(available_chats=chats, selected_chat_ids=[])
    await callback.message.edit_text(
        f"📋 All chats ({len(chats)}):",
        reply_markup=chat_selection_keyboard(chats, [])
    )

# ======================================================================
# TOGGLE CHAT SELECTION
# ======================================================================

@router.callback_query(
    BroadcastStates.selecting_chats,
    F.data.startswith("toggle_chat_")
)
async def toggle_chat(callback: CallbackQuery, state: FSMContext):
    chat_id = int(callback.data.split("_")[2])

    data = await state.get_data()
    selected = data["selected_chat_ids"]
    available = data["available_chats"]

    if chat_id in selected:
        selected.remove(chat_id)
        await callback.answer("❌ Removed")
    else:
        selected.append(chat_id)
        await callback.answer("✅ Selected")

    await state.update_data(selected_chat_ids=selected)

    await callback.message.edit_text(
        f"Selected: {len(selected)} chats",
        reply_markup=chat_selection_keyboard(available, selected)
    )

# ======================================================================
# CONFIRM CHAT SELECTION
# ======================================================================

@router.callback_query(BroadcastStates.selecting_chats, F.data == "confirm_selected")
async def confirm_selected(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data["selected_chat_ids"]

    if not selected:
        return await callback.answer(
            "❌ No chats selected!",
            show_alert=True
        )

    await state.update_data(target="selected")

    await callback.message.edit_text(
        f"✅ {len(selected)} chats selected.\n📝 Send your message."
    )
    await callback.message.answer(
        "Send message:",
        reply_markup=cancel_keyboard()
    )

    await state.set_state(BroadcastStates.waiting_for_message)

# ======================================================================
# MESSAGE RECEIVING + ALBUM PROTECTION
# ======================================================================

album_block_cache = {}  # { user_id: expire_time }


def clean_album_cache():
    now = datetime.now()
    for uid in list(album_block_cache.keys()):
        if album_block_cache[uid] < now:
            del album_block_cache[uid]


@router.message(BroadcastStates.waiting_for_message)
async def receive_message(message: Message, state: FSMContext, db):
    user_id = message.from_user.id

    clean_album_cache()

    # ❌ Album detected
    if message.media_group_id:
        if user_id not in album_block_cache:
            album_block_cache[user_id] = datetime.now() + timedelta(seconds=8)

            await state.clear()
            await message.answer(
                "❌ <b>Album messages are not supported.</b>\n\n"
                "Please send only one message, photo, video or file.",
                parse_mode="HTML",
                reply_markup=main_admin_menu()
            )
        return

    album_block_cache.pop(user_id, None)
    return await finalize_input(message, state, db)

# ======================================================================
# FINALIZE MESSAGE & PIN CONFIRMATION
# ======================================================================

async def finalize_input(message: Message, state: FSMContext, db):
    if message.text == "❌ Cancel":
        await message.answer(
            "❌ Process cancelled.",
            reply_markup=main_admin_menu()
        )
        await state.clear()
        return

    data = await state.get_data()
    target = data["target"]

    if target == "all":
        chats = await db.get_all_chats()
        target_text = "all chats"
    elif target == "channels":
        chats = await db.get_chats_by_type("channel")
        target_text = "channels"
    elif target == "groups":
        chats = await db.get_chats_by_type("group")
        target_text = "groups"
    elif target == "supergroups":
        chats = await db.get_chats_by_type("supergroup")
        target_text = "supergroups"
    else:
        ids = data["selected_chat_ids"]
        available = data["available_chats"]
        chats = [c for c in available if c["chat_id"] in ids]
        target_text = f"{len(chats)} selected chats"

    if not chats:
        await state.clear()
        return await message.answer("❌ No chats found!")

    await state.update_data(
        broadcast_message=message,
        album_group=None
    )

    await message.answer(
        f"🔐 Message will be sent to <b>{target_text}</b>.\n\n"
        "Enter your PIN code:",
        reply_markup=cancel_keyboard()
    )

    await state.set_state(BroadcastStates.waiting_for_pin)
