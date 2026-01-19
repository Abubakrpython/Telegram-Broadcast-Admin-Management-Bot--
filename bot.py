import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from middlewares.block import BlockGroupMessagesMiddleware

import config
from database import init_db, close_db
from handlers import (
    start_router,
    chat_member_router,
    statistics_router,
    broadcast_router,
    admin_router,
    users_router,
    delete_chat
)

# =====================
# LOGGING CONFIGURATION
# =====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def notify_super_admins(bot: Bot, db, text: str):
    """
    Send a notification message to all super admins.
    """
    try:
        super_admins = await db.get_all_super_admins()
        for admin in super_admins:
            try:
                await bot.send_message(admin["user_id"], text)
            except Exception as e:
                logger.warning(
                    f"Failed to send message to super admin {admin['user_id']}: {e}"
                )
    except Exception as e:
        logger.error(f"Failed to fetch super admins: {e}")


async def main():
    """
    Application entry point.
    Initializes bot, dispatcher, database, middlewares and routers.
    """
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())

    # =====================
    # MIDDLEWARES
    # =====================
    dp.message.middleware(BlockGroupMessagesMiddleware())
    dp.callback_query.middleware(BlockGroupMessagesMiddleware())

    # =====================
    # DATABASE
    # =====================
    db = await init_db()
    dp["db"] = db

    # =====================
    # ROUTERS
    # =====================
    dp.include_router(start_router)
    dp.include_router(chat_member_router)
    dp.include_router(statistics_router)
    dp.include_router(broadcast_router)
    dp.include_router(users_router)
    dp.include_router(delete_chat)
    dp.include_router(admin_router)

    logger.info("🚀 Bot is starting...")

    try:
        await dp.start_polling(bot)

    finally:
        await close_db()
        await bot.session.close()
        logger.info("👋 Bot has been stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped manually (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"❌ Bot crashed with error: {e}")
