from app.db.database import Base, engine
from app.models import User, Job, Application


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
