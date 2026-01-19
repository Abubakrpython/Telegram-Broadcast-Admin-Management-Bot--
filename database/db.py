import asyncpg
from config import DATABASE_URL
from database.models import Database

db_pool: asyncpg.Pool | None = None
db: Database | None = None


async def init_db() -> Database:
    """
    Initialize PostgreSQL connection pool
    and create required database tables.
    """
    global db_pool, db

    db_pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=5,
        max_size=20
    )

    db = Database(db_pool)
    await db.create_tables()
    return db


async def close_db():
    """
    Gracefully close PostgreSQL connection pool.
    """
    global db_pool

    if db_pool:
