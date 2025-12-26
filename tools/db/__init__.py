import os
# 新增 create_engine 用於同步連線
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

db_file = os.getenv("COURSES_DATABASE_PATH", "data/courses.db")
db_dir = os.path.dirname(db_file) or "."
try:
    os.makedirs(db_dir, exist_ok=True)
except OSError:
    pass

ASYNC_DATABASE_URL = "sqlite+aiosqlite:///" + db_file
SYNC_DATABASE_URL = "sqlite:///" + db_file

class DBInitializer:
    def __init__(self):
        self.engine = create_engine(SYNC_DATABASE_URL)

    def init_db(self):
        with self.engine.begin() as conn:
            Base.metadata.create_all(conn)

class DBAsyncSessionManager:
    def __init__(self):
        self.engine = create_async_engine(ASYNC_DATABASE_URL)

    async def get_session(self):
        async_session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        async with async_session() as session:
            yield session

class DBSessionManager:
    def __init__(self):
        self.engine = create_engine(SYNC_DATABASE_URL)
        self.session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def get_session(self):
        return self.session()

# 更新 __all__ 讓外部可以 import 新的 class
__all__ = ["Base", "DBInitializer", "DBAsyncSessionManager", "DBSessionManager"]