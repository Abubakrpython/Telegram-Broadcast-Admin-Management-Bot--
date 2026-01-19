from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    """
    States used during the broadcast workflow.
    """
    waiting_for_message = State()
    waiting_for_pin = State()
    select_target = State()
    selecting_chats = State()  
    confirm = State()


class AdminStates(StatesGroup):
    """
    States used for admin management and security actions.
    """
    add_admin = State()
    remove_admin = State()
    verify_old_pin = State()
    change_pin = State()

    delete_chat_id = State()
    delete_chat_pin = State()
