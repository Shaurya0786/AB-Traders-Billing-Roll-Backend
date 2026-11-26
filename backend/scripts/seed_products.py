# Seed a database with the catalogue, for a local or new database only.
# The live catalogue is edited in Supabase or through the admin product endpoints, not with this script.
#
#   python -m backend.scripts.seed_products                       local SQLite (the default DATABASE_URL)
#   python -m backend.scripts.seed_products --force-production    any other database, on purpose
import asyncio
import sys
from uuid import uuid4

from ..database import DATABASE_URL, Base, engine, reset_session_context, set_session_context
from ..products.service import ProductService
from ..schemas import ProductCreate
from .reset_db import guard

# The nine products as they are in the live database (November 2026). No claims the business has not
# confirmed: features and specifications stay empty unless the owner gives them.
products_data = [
    {
        "slug": "coloured-labels",
        "name": "Coloured Labels",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1795675141/AB%20Traders/clean/coloured-labels-stack.jpg",
        "category": "Labels & Ribbons",
        "category_slug": "barcode-ribbons",
        "price_per_roll": 100.0,
        "description": "Label rolls in yellow, blue, pink, green and more, for sorting stock and pricing."
    },
    {
        "slug": "labels",
        "name": "Labels, All Shapes and Sizes",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1795673405/AB%20Traders/clean/labels-1-z.jpg",
        "category": "Labels & Ribbons",
        "category_slug": "barcode-ribbons",
        "price_per_roll": 100.0,
        "description": "Label rolls in any shape and size, for barcode, price and product labels."
    },
    {
        "slug": "resin-ribbons",
        "name": "Resin Ribbons",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1795675848/AB%20Traders/clean/ribbon-resin-1.jpg",
        "category": "Labels & Ribbons",
        "category_slug": "barcode-ribbons",
        "price_per_roll": 100.0,
        "description": "Resin ribbons for barcode printers, for printing on plastic and synthetic labels."
    },
    {
        "slug": "wax-ribbons",
        "name": "Wax Ribbons",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1795675847/AB%20Traders/clean/ribbon-wax-1.jpg",
        "category": "Labels & Ribbons",
        "category_slug": "barcode-ribbons",
        "price_per_roll": 100.0,
        "description": "Wax ribbons for barcode printers, for printing on paper labels."
    },
    {
        "slug": "computer-paper",
        "name": "Computer Paper",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1795673404/AB%20Traders/clean/computer-paper-1-z.jpg",
        "category": "Dot Matrix Paper",
        "category_slug": "dot-matrix",
        "price_per_roll": 100.0,
        "description": "Continuous computer paper for dot-matrix printers, for invoices and reports."
    },
    {
        "slug": "butter-paper",
        "name": "Butter Paper Roll",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1795673401/AB%20Traders/clean/butter-paper-1-z.jpg",
        "category": "Food Wrapping Paper",
        "category_slug": "food-wrapping",
        "price_per_roll": 100.0,
        "description": "RajSon food wrap paper (butter paper) on a roll, for wrapping food at counters and for takeaway.",
        "features": "Grease resistant"
    },
    {
        "slug": "colour-printed-thermal-rolls",
        "name": "Colour / Printed Thermal Rolls",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1795673403/AB%20Traders/clean/colour-printed-thermal-rolls-1-z.jpg",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Thermal rolls printed in colour with your shop name, logo or terms."
    },
    {
        "slug": "pos-rolls",
        "name": "POS Rolls",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1795673406/AB%20Traders/clean/pos-rolls-1-z.jpg",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Thermal rolls for POS, billing and card machines, in the width your machine takes."
    },
    {
        "slug": "thermal-paper-rolls",
        "name": "Thermal Paper Rolls",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1795671910/AB%20Traders/clean/thermal-paper-roll-single.jpg",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "RajSon thermal paper rolls for bills and receipts, in standard and custom sizes."
    }
]


async def seed_products():
    token = set_session_context(str(uuid4()))
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        service = ProductService()
        print(f"Seeding {len(products_data)} products...")
        count = 0
        for p_data in products_data:
            if await service.get(p_data["slug"]):
                print(f"Skipping {p_data['slug']} - already exists")
                continue
            await service.create(ProductCreate(**p_data))
            print(f"Created: {p_data['name']}")
            count += 1
        print(f"Seeding complete. Added {count} new products.")
    finally:
        reset_session_context(token)


if __name__ == "__main__":
    guard(DATABASE_URL, force="--force-production" in sys.argv)
    asyncio.run(seed_products())
