import logging
import os
import uuid

from fastapi import FastAPI, Request

from .database import engine, Base
from .products import router as products_router
from .inquiries import router as inquiries_router
from .stats import router as stats_router
from .middlewares.sqlalchemy import SQLAlchemyMiddleware

app = FastAPI(title="Thermal Paper Backend")

# Setup Logger
logger = logging.getLogger("uvicorn")

from fastapi.middleware.cors import CORSMiddleware

# Middleware
# Browsers may call the API only from the website (and its Vercel previews and local development).
# ALLOWED_ORIGINS (comma separated) and ALLOWED_ORIGIN_REGEX override the defaults.
DEFAULT_ORIGINS = "https://thermalpaperlabels.com,https://www.thermalpaperlabels.com,http://localhost:5173,http://localhost:8080,http://localhost:4300"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()],
    allow_origin_regex=os.getenv("ALLOWED_ORIGIN_REGEX", r"https://roll-ready-custom[a-z0-9-]*\.vercel\.app"),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Key"],
)
app.add_middleware(SQLAlchemyMiddleware)

# Database Initialization
@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables created.")

# Include Routers
app.include_router(inquiries_router.router)
app.include_router(products_router.router)
app.include_router(stats_router.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
