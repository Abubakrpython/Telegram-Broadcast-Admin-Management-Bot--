import asyncpg
from typing import List, Dict, Optional


class Database:
    """
    PostgreSQL database wrapper using asyncpg.
    Provides all CRUD operations for admins, users, chats and broadcasts.
    """

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    # =====================================================
    # UNIVERSAL QUERY HELPERS
    # =====================================================

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    # =====================================================
    # TABLE CREATION
    # =====================================================

    async def create_tables(self):
        """Create all required tables if they do not exist"""
        async with self.pool.acquire() as conn:

            # Admins
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE NOT NULL,
                    username TEXT,
                    full_name TEXT,
                    pin_code VARCHAR(4) NOT NULL,
                    added_date TIMESTAMP DEFAULT NOW()
                )
            """)

            # Users
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    first_seen TIMESTAMP DEFAULT NOW()
                )
            """)

            # Chats
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chats (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT UNIQUE NOT NULL,
                    chat_type VARCHAR(50) NOT NULL,
                    title TEXT,
                    username TEXT,
                    invite_link TEXT,
                    description TEXT,
                    added_date TIMESTAMP DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)

            # Broadcasts
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS broadcasts (
                    id SERIAL PRIMARY KEY,
                    admin_id BIGINT NOT NULL,
                    total_chats INTEGER DEFAULT 0,
                    success INTEGER DEFAULT 0,
                    failed INTEGER DEFAULT 0,
                    broadcast_date TIMESTAMP DEFAULT NOW(),
                    message_type VARCHAR(50),
                    message_text TEXT
                )
            """)

            # Super admins
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS super_admins (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE NOT NULL,
                    added_date TIMESTAMP DEFAULT NOW()
                )
            """)

    # =====================================================
    # USER METHODS
    # =====================================================

    async def get_all_users(self) -> List[Dict]:
        """Return all users ordered by first_seen DESC"""
        rows = await self.fetch("""
            SELECT * FROM users
            ORDER BY first_seen DESC
        """)
        return [dict(r) for r in rows]

    async def add_user(self, user_id: int, username: str, full_name: str) -> bool:
        """
        Add new user or update existing one.
        Returns True if user is new, False otherwise.
        """
        exists = await self.fetchval(
            "SELECT 1 FROM users WHERE user_id = $1", user_id
        )

        if exists:
            await self.execute("""
                UPDATE users
                SET username = $2, full_name = $3
                WHERE user_id = $1
            """, user_id, username, full_name)
            return False

        await self.execute("""
            INSERT INTO users (user_id, username, full_name)
            VALUES ($1, $2, $3)
        """, user_id, username, full_name)

        return True

    # =====================================================
    # ADMIN METHODS
    # =====================================================

    async def add_admin(
        self,
        user_id: int,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        pin_code: Optional[str] = None
    ) -> str:
        """Add admin and generate PIN if not provided"""
        import random

        if not pin_code:
            pin_code = "".join(str(random.randint(0, 9)) for _ in range(4))

        await self.execute("""
            INSERT INTO admins (user_id, username, full_name, pin_code)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id)
            DO UPDATE SET pin_code = $4
        """, user_id, username, full_name, pin_code)

        return pin_code

    async def is_admin(self, user_id: int) -> bool:
        return bool(await self.fetchval(
            "SELECT 1 FROM admins WHERE user_id = $1",
            user_id
        ))

    async def remove_admin(self, user_id: int) -> bool:
        await self.execute("DELETE FROM admins WHERE user_id = $1", user_id)
        return True

    async def get_all_admins(self) -> List[Dict]:
        rows = await self.fetch("""
            SELECT * FROM admins
            ORDER BY added_date DESC
        """)
        return [dict(r) for r in rows]

    # =====================================================
    # SUPER ADMIN METHODS
    # =====================================================

    async def add_super_admin(self, user_id: int):
        await self.execute("""
            INSERT INTO super_admins (user_id)
            VALUES ($1)
            ON CONFLICT (user_id) DO NOTHING
        """, user_id)

    async def remove_super_admin(self, user_id: int):
        await self.execute(
            "DELETE FROM super_admins WHERE user_id = $1",
            user_id
        )

    async def is_super_admin(self, user_id: int) -> bool:
        return bool(await self.fetchval(
            "SELECT 1 FROM super_admins WHERE user_id = $1",
            user_id
        ))

    async def get_all_super_admins(self) -> List[Dict]:
        rows = await self.fetch("""
            SELECT sa.user_id, a.username, a.full_name, sa.added_date
            FROM super_admins sa
            LEFT JOIN admins a ON sa.user_id = a.user_id
            ORDER BY sa.added_date DESC
        """)
        return [dict(r) for r in rows]

    # =====================================================
    # PIN MANAGEMENT
    # =====================================================

    async def verify_pin(self, user_id: int, pin: str) -> bool:
        return bool(await self.fetchval("""
            SELECT 1 FROM admins
            WHERE user_id = $1 AND pin_code = $2
        """, user_id, pin))

    async def get_admin_pin(self, user_id: int) -> Optional[str]:
        return await self.fetchval(
            "SELECT pin_code FROM admins WHERE user_id = $1",
            user_id
        )

    async def update_pin(self, user_id: int, new_pin: str):
        await self.execute("""
            UPDATE admins
            SET pin_code = $1
            WHERE user_id = $2
        """, new_pin, user_id)

    # =====================================================
    # CHAT METHODS
    # =====================================================

    async def add_chat(
        self,
        chat_id: int,
        chat_type: str,
        title: str,
        username: Optional[str] = None,
        invite_link: Optional[str] = None,
        description: Optional[str] = None
    ) -> bool:
        """Insert or update chat when bot becomes admin"""
        await self.execute("""
            INSERT INTO chats (
                chat_id, chat_type, title, username,
                invite_link, description, is_active
            )
            VALUES ($1, $2, $3, $4, $5, $6, TRUE)
            ON CONFLICT (chat_id)
            DO UPDATE SET
                chat_type = EXCLUDED.chat_type,
                title = EXCLUDED.title,
                username = EXCLUDED.username,
                invite_link = EXCLUDED.invite_link,
                description = EXCLUDED.description,
                is_active = TRUE
        """, chat_id, chat_type, title, username, invite_link, description)

        return True

    async def delete_chat(self, chat_id: int) -> bool:
        try:
            await self.execute(
                "DELETE FROM chats WHERE chat_id = $1",
                chat_id
            )
            return True
        except Exception as e:
            return False

    async def get_chat_by_id(self, chat_id: int) -> Optional[Dict]:
        row = await self.fetchrow(
            "SELECT * FROM chats WHERE chat_id = $1",
            chat_id
        )
        return dict(row) if row else None

    async def get_all_chats(self, only_active: bool = True) -> List[Dict]:
        if only_active:
            rows = await self.fetch("""
                SELECT * FROM chats
                WHERE is_active = TRUE
                ORDER BY added_date DESC
            """)
        else:
            rows = await self.fetch("""
                SELECT * FROM chats
                ORDER BY added_date DESC
            """)

        return [dict(r) for r in rows]

    async def get_chats_by_type(self, chat_type: str) -> List[Dict]:
        rows = await self.fetch("""
            SELECT * FROM chats
            WHERE chat_type = $1 AND is_active = TRUE
            ORDER BY added_date DESC
        """, chat_type)
        return [dict(r) for r in rows]

    async def get_chat_type_counts(self) -> Dict[str, int]:
        return {
            "channels": await self.fetchval(
                "SELECT COUNT(*) FROM chats WHERE chat_type = 'channel' AND is_active = TRUE"
            ) or 0,
            "groups": await self.fetchval(
                "SELECT COUNT(*) FROM chats WHERE chat_type = 'group' AND is_active = TRUE"
            ) or 0,
            "supergroups": await self.fetchval(
                "SELECT COUNT(*) FROM chats WHERE chat_type = 'supergroup' AND is_active = TRUE"
            ) or 0,
            "total": await self.fetchval(
                "SELECT COUNT(*) FROM chats WHERE is_active = TRUE"
            ) or 0
        }

    # =====================================================
    # BROADCAST METHODS
    # =====================================================

    async def add_broadcast(
        self,
        admin_id: int,
        total: int,
        success: int,
        failed: int,
        message_type: str,
        message_text: Optional[str] = None
    ):
        await self.execute("""
            INSERT INTO broadcasts (
                admin_id, total_chats, success,
                failed, message_type, message_text
            )
            VALUES ($1, $2, $3, $4, $5, $6)
        """, admin_id, total, success, failed, message_type, message_text)

    async def get_broadcast_stats(self, limit: int = 10) -> List[Dict]:
        rows = await self.fetch("""
            SELECT b.*, a.username AS admin_username
            FROM broadcasts b
            LEFT JOIN admins a ON b.admin_id = a.user_id
            ORDER BY broadcast_date DESC
            LIMIT $1
        """, limit)
        return [dict(r) for r in rows]

    async def get_total_broadcast_stats(self) -> Dict:
        row = await self.fetchrow("""
            SELECT
                COUNT(*) AS total_broadcasts,
                SUM(success) AS total_success,
                SUM(failed) AS total_failed
            FROM broadcasts
        """)

        return dict(row) if row else {
            "total_broadcasts": 0,
            "total_success": 0,
            "total_failed": 0
        }

    async def get_time_based_broadcast_stats(self) -> Dict[str, int]:
        today = await self.fetchval("""
            SELECT COUNT(*)
            FROM broadcasts
            WHERE DATE(broadcast_date) = CURRENT_DATE
        """)

        week = await self.fetchval("""
            SELECT COUNT(*)
            FROM broadcasts
            WHERE broadcast_date >= CURRENT_DATE - INTERVAL '7 days'
        """)

        month = await self.fetchval("""
            SELECT COUNT(*)
            FROM broadcasts
            WHERE DATE_TRUNC('month', broadcast_date)
                  = DATE_TRUNC('month', CURRENT_DATE)
        """)

        total = await self.fetchval("SELECT COUNT(*) FROM broadcasts")

        return {
            "today": today or 0,
            "week": week or 0,
            "month": month or 0,
            "total": total or 0
        }

    async def get_today_broadcast_admins(self) -> List[Dict]:
        rows = await self.fetch("""
            SELECT DISTINCT a.full_name, a.username, a.user_id
            FROM broadcasts b
            JOIN admins a ON b.admin_id = a.user_id
            WHERE DATE(b.broadcast_date) = CURRENT_DATE
        """)
        return [dict(r) for r in rows]
