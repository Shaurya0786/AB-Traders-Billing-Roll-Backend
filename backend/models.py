from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import String, Integer, Float, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from .database import Base

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    price_per_roll: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    category_slug: Mapped[str] = mapped_column(String(255), nullable=False)
    features: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON string or delimiter separated
    specifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON string or delimiter separated

class Inquiry(Base):
    __tablename__ = "inquiries"
    
    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Generic inquiry fields
    product_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    estimated_quantity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Custom Quote specific fields
    is_custom_quote: Mapped[bool] = mapped_column(Boolean, default=False)
    roll_width: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    roll_diameter: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    exact_quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class SiteStatistic(Base):
    __tablename__ = "site_statistics"
    
    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, index=True) # e.g., 'experience_years'
    value: Mapped[str] = mapped_column(String(50)) # e.g., '15+'
