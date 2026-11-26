import os
import sqlite3

ADMIN = {"X-Admin-Key": os.environ["ADMIN_API_KEY"]}
BUYER = {"full_name": "Ravi Kumar", "email": "ravi@shop.in", "phone_number": "+91 98765 43210", "message": "Prices please."}


def _rows(sql):
    path = os.environ["DATABASE_URL"].split("///", 1)[1]
    with sqlite3.connect(path) as c:
        return c.execute(sql).fetchall()


def _product(client, slug, name):
    client.post("/products", headers=ADMIN, json={"name": name, "price_per_roll": 100, "slug": slug,
                "category": "Thermal Paper & POS Rolls", "category_slug": "thermal-pos"})


def test_enquiry_saves_the_cart_products(client):
    from backend.inquiries import router
    router.limiter.reset()
    _product(client, "pos-rolls-t", "POS Rolls T")
    _product(client, "wax-ribbons-t", "Wax Ribbons T")
    r = client.post("/inquiries", json={**BUYER, "items": [{"product_slug": "pos-rolls-t", "boxes": 8},
                                                           {"product_slug": "wax-ribbons-t", "boxes": 5}]})
    assert r.status_code == 201
    body = r.json()
    assert [(i["product_slug"], i["product_name"], i["boxes"]) for i in body["items"]] == [("pos-rolls-t", "POS Rolls T", 8), ("wax-ribbons-t", "Wax Ribbons T", 5)]
    saved = _rows(f"select product_slug, product_name, boxes from inquiry_items where inquiry_id = '{body['id'].replace('-', '')}' or inquiry_id = '{body['id']}' order by product_slug")
    assert saved == [("pos-rolls-t", "POS Rolls T", 8), ("wax-ribbons-t", "Wax Ribbons T", 5)]


def test_enquiry_without_products_still_works(client):
    from backend.inquiries import router
    router.limiter.reset()
    r = client.post("/inquiries", json=BUYER)
    assert r.status_code == 201 and r.json()["items"] == []


def test_unknown_product_is_kept_under_its_slug(client):
    # a product deleted between the visitor adding it and sending: the enquiry must not be lost
    from backend.inquiries import router
    router.limiter.reset()
    r = client.post("/inquiries", json={**BUYER, "items": [{"product_slug": "gone-product", "boxes": 6}]})
    assert r.status_code == 201 and r.json()["items"][0]["product_name"] == "gone-product"


def test_bad_items_are_rejected(client):
    from backend.inquiries import router
    router.limiter.reset()
    assert client.post("/inquiries", json={**BUYER, "items": [{"product_slug": "pos-rolls-t", "boxes": 0}]}).status_code == 422
    assert client.post("/inquiries", json={**BUYER, "items": [{"product_slug": "x", "boxes": 5}] * 60}).status_code == 422


def test_email_lists_the_products():
    from backend.inquiries.notification_service import render_inquiry_email
    _, html = render_inquiry_email({**BUYER, "items": [{"product_slug": "p", "product_name": "<i>POS</i> Rolls", "boxes": 8}]})
    assert "8 boxes (400 pcs)" in html and "&lt;i&gt;POS&lt;/i&gt; Rolls" in html
