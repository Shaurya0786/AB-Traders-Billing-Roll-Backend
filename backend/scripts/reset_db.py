# Drop and recreate every table. Deletes all products AND all enquiries.
# It refuses any database but a local SQLite one unless --force-production is given.
#
#   python -m backend.scripts.reset_db
import asyncio
import sys

from .. import models  # noqa: F401  (registers the tables on Base.metadata)
from ..database import DATABASE_URL, Base, engine


def guard(url: str, force: bool) -> None:
    """Stop unless the database is a local SQLite file, or the caller forced it."""
    if url.startswith("sqlite") or force:
        return
    host = url.split("@")[-1].split("/")[0] if "@" in url else url.split("://")[0]
    print(f"Refusing: DATABASE_URL points at {host}, not a local SQLite file.\n"
          "This would affect the live data. Add --force-production only if you mean it.")
    raise SystemExit(1)


async def reset_db():
    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Done.")


if __name__ == "__main__":
    guard(DATABASE_URL, force="--force-production" in sys.argv)
    asyncio.run(reset_db())
