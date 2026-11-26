from typing import Optional
from pydantic import BaseModel, EmailStr, Field

# --- Pydantic Models for Input Validation ---

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price_per_roll: float = Field(..., gt=0)
    image_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    slug: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    category: str = Field(..., min_length=1, max_length=255)
    category_slug: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    features: Optional[str] = Field(None, max_length=5000)
    specifications: Optional[str] = Field(None, max_length=5000)

class ProductUpdate(BaseModel):
    """Every field optional: only the fields sent are changed."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    price_per_roll: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    category: Optional[str] = Field(None, min_length=1, max_length=255)
    category_slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    features: Optional[str] = Field(None, max_length=5000)
    specifications: Optional[str] = Field(None, max_length=5000)

class InquiryItemCreate(BaseModel):
    product_slug: str = Field(..., min_length=1, max_length=255)
    boxes: int = Field(..., ge=1, le=100000)

class InquiryCreate(BaseModel):
    # limits follow the database columns, so an oversized field is a clear 422, not a database error
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone_number: str = Field(..., min_length=5, max_length=20)
    company_name: Optional[str] = Field(None, max_length=255)

    product_type: Optional[str] = Field(None, max_length=100)
    estimated_quantity: Optional[str] = Field(None, max_length=100)
    message: Optional[str] = Field(None, max_length=5000)

    is_custom_quote: bool = False
    roll_width: Optional[str] = Field(None, max_length=50)
    roll_diameter: Optional[int] = Field(None, ge=0, le=100000)
    exact_quantity: Optional[int] = Field(None, ge=0, le=10_000_000)

    # the products in the visitor's cart, if any (at most 50)
    items: list[InquiryItemCreate] = Field(default_factory=list, max_length=50)

class StatisticCreate(BaseModel):
    key: str
    value: str
