from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Read the DATABASE_URL from .env. The user provides a sync connection string (mysql+pymysql://),
# but since we are using AsyncSession, we need to replace 'pymysql' with 'aiomysql'.
raw_db_url = os.getenv("DATABASE_URL", "mysql+aiomysql://root:root@localhost:3306/clinic_db")
DATABASE_URL = raw_db_url.replace("mysql+pymysql", "mysql+aiomysql")

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
