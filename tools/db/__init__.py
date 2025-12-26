import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine

Base = declarative_base()

DATABASE_URL = "sqlite+aiosqlite:///" + os.getenv("COURSES_DATABASE_PATH", "data/courses.db")

class DatabaseInitializer:
    def __init__(self):
        self.engine = create_async_engine(DATABASE_URL, echo=True)

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
class DatabaseSessionManager:
    def __init__(self):
        self.engine = create_async_engine(DATABASE_URL, echo=True)

    async def get_session(self):
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker

        async_session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with async_session() as session:
            yield session