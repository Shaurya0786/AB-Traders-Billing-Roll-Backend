from contextvars import ContextVar, Token
from typing import AsyncGenerator, Union
from uuid import uuid4

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - using SQLite for local development as fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

class Base(DeclarativeBase):
    pass

# Context variable to handle session scope
session_context: ContextVar[str] = ContextVar("session_context")

def get_session_context() -> str:
    return session_context.get()

def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)

def reset_session_context(context: Token) -> None:
    session_context.reset(context)

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    # SQL logging is off: it printed every enquiry's name, email and phone to the server logs. SQL_ECHO=1 turns it on locally.
    echo=os.getenv("SQL_ECHO") == "1",
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

session: Union[AsyncSession, async_scoped_session] = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=get_session_context
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get the database session.
    Since we are using async_scoped_session, this acts as a proxy to the
    session attached to the current scope (request).
    """
    # Create a new session for the current context if one doesn't exist
    # or return the existing one.
    # Note: With scoped_session, calling it returns the session.
    db = session() 
    try:
        yield db
    finally:
        await db.close()
        # await session.remove() # Optional: remove session from registry
