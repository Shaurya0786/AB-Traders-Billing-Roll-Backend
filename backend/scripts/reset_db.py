import asyncio
from ..database import engine, Base
from .. import models # Import models to populate Base.metadata

async def reset_db():
    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Tables dropped.")
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created.")

if __name__ == "__main__":
    asyncio.run(reset_db())
