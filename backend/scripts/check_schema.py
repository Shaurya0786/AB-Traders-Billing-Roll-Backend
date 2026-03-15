import asyncio
from sqlalchemy import text
from ..database import engine

async def check_schema():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'products';"))
        rows = result.fetchall()
        print("Schema for products table:")
        for row in rows:
            print(f"{row[0]}: {row[1]}")

if __name__ == "__main__":
    asyncio.run(check_schema())
