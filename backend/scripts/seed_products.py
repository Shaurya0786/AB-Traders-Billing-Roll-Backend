import asyncio
from uuid import uuid4
from sqlalchemy import select

from ..database import session, engine, Base, set_session_context, reset_session_context
from ..models import Product
from ..products.service import ProductService
from ..schemas import ProductCreate

products_data = [
    # Barcode Labels & Ribbons
    {
        "slug": "barcode-label-coloured",
        "name": "Barcode Label (Coloured)",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769342875/AB%20Traders/barcode_label_color_1_yrhwim.png",
        "category": "Barcode Labels & Ribbons",
        "category_slug": "barcode-ribbons",
        "price_per_roll": 100.0,
        "description": "High-quality colored barcode labels for inventory management and categorization.",
        "features": "Vibrant colors,Strong adhesive,Durable material,Custom sizes",
        "specifications": "Width: Various,Length: standard roll,Core: 1 inch,Color: Multi"
    },
    {
        "slug": "barcode-label-rajson-5",
        "name": "Barcode Label RajSon 5",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769339844/AB%20Traders/Bar%20Code%20label%20RajSon%205.png",
        "category": "Barcode Labels & Ribbons",
        "category_slug": "barcode-ribbons",
        "price_per_roll": 100.0,
        "description": "Standard barcode labels for retail and industrial use. Reliable scanning performance.",
        "features": "Clear print,Scuff resistant,Permanent adhesive,Universal compatibility",
        "specifications": "Size: 50x25mm (approx),Labels/Roll: 1000+,Material: Semigloss"
    },
    {
        "slug": "barcode-label-white-printing",
        "name": "Barcode Label (White Printing)",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769339845/AB%20Traders/Bar%20Code%20label%20RajSon%203.png",
        "category": "Barcode Labels & Ribbons",
        "category_slug": "barcode-ribbons",
        "price_per_roll": 100.0,
        "description": "Premium white barcode labels designed for thermal transfer printing.",
        "features": "High contrast,Smudge-proof,Long-lasting,Crisp definition",
        "specifications": "Size: Customizable,Core: 1-3 inch,Gap: 3mm"
    },
    {
        "slug": "barcode-label-multiple-angles",
        "name": "Barcode Label (Multiple Angles)",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769339834/AB%20Traders/Bar%20Code%20label%20RajSon%207.png",
        "category": "Barcode Labels & Ribbons",
        "category_slug": "barcode-ribbons",
        "price_per_roll": 100.0,
        "description": "Versatile barcode labels suitable for various packaging surfaces and angles.",
        "features": "Flexible material,Strong tack,Curved surface compatible",
        "specifications": " Adhesive: Rubber/Acrylic based,Liner: Glassine"
    },

    # Dot Matrix Paper
    {
         "slug": "computer-paper-rajson-9",
         "name": "Computer Paper RajSon 9",
         "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769339878/AB%20Traders/Computer%20Paper%20RajSon%209.png",
         "category": "Dot Matrix Paper",
         "category_slug": "dot-matrix",
         "price_per_roll": 100.0,
         "description": "Continuous computer paper for dot matrix printers. Reliable feed and print quality.",
         "features": "Jam-free,Precise perforation,Carbonless options",
         "specifications": "Size: 10x12,GSM: 60-80,Ply: 1-3"
    },
    {
         "slug": "computer-paper-rajson-3",
         "name": "Computer Paper RajSon 3",
         "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769339831/AB%20Traders/Computer%20Paper%20RajSon%203.png",
         "category": "Dot Matrix Paper",
         "category_slug": "dot-matrix",
         "price_per_roll": 100.0,
         "description": "Standard continuous form paper. Ideal for invoices, reports, and data logging.",
         "features": "Bright white,Clean tear edges,Dust-free",
         "specifications": "Size: Standard,Box: 1000/2000 sheets"
    },
    {
         "slug": "computer-paper-rajson-6",
         "name": "Computer Paper RajSon 6",
         "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769339837/AB%20Traders/Computer%20Paper%20RajSon%206.png",
         "category": "Dot Matrix Paper",
         "category_slug": "dot-matrix",
         "price_per_roll": 100.0,
         "description": "High-performance dot matrix paper. Ensures smooth operation in high-speed printers.",
         "features": "Smooth surface,High opacity,Consistent quality",
         "specifications": "GSM: 70,Ply: Single/Multi"
    },

    # Thermal Paper & POS Rolls
    {
        "slug": "billing-roll-colour-printing",
        "name": "Billing Roll (Colour Printing)",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769339832/AB%20Traders/Billing%20Roll%20RajSon%2010.png",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Custom color printed billing rolls for branding and marketing on receipts.",
        "features": "Custom logo printing,BPA free,Clear thermal image",
        "specifications": "Width: 79mm/57mm,Length: 50m+,Colors: Up to 4"
    },
    {
        "slug": "billing-roll-rajson-3",
        "name": "Billing Roll RajSon 3",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769339831/AB%20Traders/Billing%20Roll%20RajSon%203.png",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Standard thermal billing roll for POS machines. Essential for retail businesses.",
        "features": "High brightness,Quick dry,Long image life",
        "specifications": "Width: 3 inch (79mm),Core: 13mm"
    },
    {
        "slug": "billing-roll-write",
        "name": "Billing Roll (Write)",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769339832/AB%20Traders/Billing%20Roll%20RajSon%204.png",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Versatile billing roll suitable for writing and printing.",
        "features": "Smooth texture,Ink absorbent (non-thermal side)",
        "specifications": "Paper Type: Bond/Thermal"
    },
    {
        "slug": "billing-roll-rajson-8",
        "name": "Billing Roll RajSon 8",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769339836/AB%20Traders/Billing%20Roll%20RajSon%208.png",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Premium billing rolls for high-volume environments. Reduces roll change frequency.",
        "features": "Tightly wound,End-of-roll indicator,Lint-free",
        "specifications": "Length: Extended meterage,Pack: 50/100 rolls"
    },
    {
        "slug": "billing-roll-rajson-5",
        "name": "Billing Roll RajSon 5",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769339834/AB%20Traders/Billing%20Roll%20RajSon%205.png",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Cost-effective billing rolls for everyday use. Reliable quality.",
        "features": "Economical,Standard tear,Dark print",
        "specifications": "Width: 57mm,Diameter: 40mm"
    },
    {
        "slug": "billing-roll-white",
        "name": "Billing Roll (White)",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769339835/AB%20Traders/Billing%20Roll%20RajSon%207.png",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Classic white thermal rolls. Provides professional looking receipts.",
        "features": "Clean white finish,Sharp black text,Preservation > 5 years",
        "specifications": "GSM: 55/65/70"
    },
    {
        "slug": "teleprinter-rajson",
        "name": "Teleprinter Roll RajSon",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769366361/AB%20Traders/telepriter_rajson_cicrd0.png",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Specialized rolls for teleprinter and telex machines. High tensile strength.",
        "features": "Durable,Continuous feed,Low dust",
        "specifications": "Ply: Multi-ply options,Width: Specific to machine"
    },
    {
        "slug": "teleprinter-rajson-2",
        "name": "Teleprinter Roll RajSon 2",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769366361/AB%20Traders/teleprinter_rajson_roll_2_cycwq0.png",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "High-grade teleprinter paper. Ensures clear communication logs.",
        "features": "Fade resistant,Uniform thickness",
        "specifications": "Core: Standard cardboard/plastic"
    },
    {
        "slug": "cashier-roll-rajson",
        "name": "Cashier Roll RajSon",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769365760/AB%20Traders/cashier_rolll_rajson_logo_1_avl7z5.png",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Efficient cashier rolls for quick transactions. Fits most cash registers.",
        "features": "Easy load,Clear print,BPA free",
        "specifications": "Width: 44mm/57mm/76mm"
    },
     {
        "slug": "thermal-paper-roll-box",
        "name": "Thermal Paper Roll Box",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769365759/AB%20Traders/box_of_rolls_rajson_n91phj.png",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Bulk box of premium thermal paper rolls. Best value for businesses.",
        "features": "Bulk packaging,Protective wrapping,Consistent quality",
        "specifications": "Pack Size: 50/100 rolls,Storage: Cool dry place"
    },

    # Collections / Mix
    {
        "slug": "collective-rajson-roll-4",
        "name": "Collective RajSon Rolls",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769366581/AB%20Traders/collective_rajson_roll_4_ksvevh.png",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Assortment of RajSon paper rolls suitable for various business needs.",
        "features": "Variety pack,Multi-purpose",
        "specifications": "Contains: Billing, POS, and Fax rolls"
    },
    {
        "slug": "collective-image-2",
        "name": "RajSon Collection Overview",
        "image_url": "https://res.cloudinary.com/shadowprojects/image/upload/v1769365857/AB%20Traders/collective_image_gbfaa8.png",
        "category": "Thermal Paper & POS Rolls",
        "category_slug": "thermal-pos",
        "price_per_roll": 100.0,
        "description": "Comprehensive range of paper products available at RajSon.",
        "features": "Full catalog visualization",
        "specifications": "Range: Thermal, Bond, Carbonless"
    }
]

async def seed_products():
    # Set session context
    token = set_session_context(str(uuid4()))
    try:
        # Ensure tables exist (redundant if main.py ran, but safe)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        service = ProductService()
        
        print(f"Seeding {len(products_data)} new products...")
        count = 0
        for p_data in products_data:
            try:
                # Check if product exists by slug
                existing = await service.get_by_slug(p_data["slug"])
                if existing:
                    print(f"Skipping {p_data['slug']} - already exists")
                    continue
                
                product = ProductCreate(**p_data)
                await service.create(product)
                print(f"Created: {p_data['name']}")
                count += 1
            except Exception as e:
                print(f"Error creating {p_data['name']}: {e}")
        
        print(f"Seeding complete. Added {count} new products.")
            
    finally:
        reset_session_context(token)

if __name__ == "__main__":
    asyncio.run(seed_products())
