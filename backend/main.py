import logging
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
