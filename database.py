# ----------- dependencies ----------- #
from sqlalchemy import Column, Integer, String, Boolean, update, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from configuration import DATABASE_FILENAME
import asyncio
# ----------- ------------ ----------- #

async_engine = create_async_engine(f'sqlite+aiosqlite:///{DATABASE_FILENAME}')
async_session = async_sessionmaker(async_engine, expire_on_commit = False)

# --------------- -------------- --------------- #
class Base(AsyncAttrs, DeclarativeBase):
    pass
# --------------- -------------- --------------- #

# --------------- ---------------- --------------- #
class TelegramChat(Base):
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key = True)
    username = Column(String, nullable = False) # also can be chat ID (in string)
    title = Column(String, nullable = False)
    status = Column(Boolean, nullable = False)
# --------------- ---------------- --------------- #

# help functions
# --------------- ---------------- --------------- #
async def fetchone(stmt, session):
    result = await session.execute(stmt)
    return result.scalar()
# --------------- ---------------- --------------- #

# --------------- ---------------- --------------- #
async def fetchmany(stmt, session):
    result = await session.execute(stmt)
    return result.scalars()
# --------------- ---------------- --------------- #

# --------------- ---------------- --------------- #
async def insert(object_, session):
    session.add(object_)
    await session.commit()
# --------------- ---------------- --------------- #

# --------------- ---------------- --------------- #
async def execute_stmt(stmt, session) -> None:
    await session.execute(stmt)
    await session.commit()
# --------------- ---------------- --------------- #