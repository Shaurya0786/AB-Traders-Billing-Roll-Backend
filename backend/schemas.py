from typing import Optional
from pydantic import BaseModel, EmailStr, Field

# --- Pydantic Models for Input Validation ---

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    price_per_roll: float = Field(..., gt=0)
    image_url: Optional[str] = None
    description: Optional[str] = None
    slug: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    category_slug: str = Field(..., min_length=1)
    features: Optional[str] = None
    specifications: Optional[str] = None

class InquiryCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    company_name: Optional[str] = None
    
    product_type: Optional[str] = None
    estimated_quantity: Optional[str] = None
    message: Optional[str] = None
    
    is_custom_quote: bool = False
    roll_width: Optional[str] = None
    roll_diameter: Optional[int] = None
    exact_quantity: Optional[int] = None

class StatisticCreate(BaseModel):
    key: str
    value: str
