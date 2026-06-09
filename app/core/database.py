from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# Use an environment variable or default to a local MySQL DB.
# For demonstration/testing without a real mysql server, one might use sqlite, 
# but the prompt specifically requested MySQL. Ensure asyncmy or aiomysql is used.
# Since it's MySQL + async, usually mysql+aiomysql://
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://root:root@localhost:3306/clinic_db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
