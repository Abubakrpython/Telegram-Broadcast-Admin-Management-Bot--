from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def main_admin_menu() -> ReplyKeyboardMarkup:
    """
    Main admin control menu.
    """
    keyboard = [
        [KeyboardButton(text="📊 Statistics"), KeyboardButton(text="📢 Broadcast Message")],
        [KeyboardButton(text="📋 Channels"), KeyboardButton(text="👥 Groups")],
        [KeyboardButton(text="🔥 Supergroups"), KeyboardButton(text="👤 Users")],
        [KeyboardButton(text="👨‍💼 Admins"), KeyboardButton(text="❓ Help")],
        [KeyboardButton(text="🗑 Delete Chat")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="🔧 Admin control panel..."
    )


def broadcast_menu() -> ReplyKeyboardMarkup:
    """
    Broadcast target selection menu.
    """
    keyboard = [
        [KeyboardButton(text="📢 Send to all")],
        [
            KeyboardButton(text="📺 Channels only"),
            KeyboardButton(text="👥 Groups only"),
            KeyboardButton(text="🔥 Supergroups only")
        ],
        [KeyboardButton(text="🎯 Select manually")],
        [KeyboardButton(text="🔙 Back")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Cancel action keyboard.
    """
    keyboard = [[KeyboardButton(text="❌ Cancel")]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def confirm_broadcast() -> InlineKeyboardMarkup:
    """
    Broadcast confirmation (send mode selection).
    """
    keyboard = [
        [
            InlineKeyboardButton(
                text="📨 Forward",
                callback_data="send_forward"
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Copy (no forward)",
                callback_data="send_copy"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="cancel_broadcast"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def chat_selection_keyboard(
    chats: list,
    selected_ids: list | None = None,
    chat_type: str = "all"
) -> InlineKeyboardMarkup:
    """
    Chat selection keyboard (checkbox-style).
    """
    if selected_ids is None:
        selected_ids = []

    keyboard = []

    for chat in chats:
        chat_id = chat.get("chat_id")
        chat_title = chat.get("title", "Unknown")
        chat_type_icon = "📺" if chat.get("chat_type") == "channel" else "👥"

        checkbox = "✅" if chat_id in selected_ids else "⬜"

        keyboard.append([
            InlineKeyboardButton(
                text=f"{checkbox} {chat_type_icon} {chat_title}",
                callback_data=f"toggle_chat_{chat_id}"
            )
        ])

    bottom_buttons = []

    if selected_ids:
        bottom_buttons.append(
            InlineKeyboardButton(
                text=f"✅ Send ({len(selected_ids)})",
                callback_data="confirm_selected"
            )
        )

    bottom_buttons.append(
        InlineKeyboardButton(
            text="❌ Cancel",
            callback_data="cancel_selection"
        )
    )

    if bottom_buttons:
        keyboard.append(bottom_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def chat_type_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Chat type selection keyboard.
    """
    keyboard = [
        [
            InlineKeyboardButton(text="📺 Channels", callback_data="select_channels"),
            InlineKeyboardButton(text="👥 Groups", callback_data="select_groups")
        ],
        [
            InlineKeyboardButton(text="📋 All chats", callback_data="select_all_chats")
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_list_keyboard(admins: list) -> InlineKeyboardMarkup:
    """
    Admin list keyboard.
    """
    keyboard = []

    for admin in admins:
        admin_name = admin.get("username") or admin.get("full_name", "Unknown")
        user_id = admin.get("user_id")

        keyboard.append([
            InlineKeyboardButton(
                text=f"👨‍💼 @{admin_name}" if admin.get("username") else f"👨‍💼 {admin_name}",
                callback_data=f"admin_info_{user_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="➕ Add admin", callback_data="add_admin"),
        InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def pagination_keyboard(page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    """
    Pagination navigation keyboard.
    """
    keyboard = []

    nav_buttons = []

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Previous",
                callback_data=f"{prefix}_page_{page - 1}"
            )
        )

    nav_buttons.append(
        InlineKeyboardButton(
            text=f"{page}/{total_pages}",
            callback_data="current_page"
        )
    )

    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Next ➡️",
                callback_data=f"{prefix}_page_{page + 1}"
            )
        )

    keyboard.append(nav_buttons)
    keyboard.append([
        InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
