import os
import sqlite3

ADMIN = {"X-Admin-Key": os.environ["ADMIN_API_KEY"]}
PRODUCT = {
    "name": "Test Roll", "price_per_roll": 100, "slug": "test-roll", "category": "Thermal Paper & POS Rolls",
    "category_slug": "thermal-pos", "description": "A test roll.", "image_url": "https://example.com/a.jpg",
}
INQUIRY = {"full_name": "Test Buyer", "email": "buyer@example.com", "phone_number": "+91 98765 43210",
           "product_type": "thermal", "estimated_quantity": "100-500", "message": "Prices please."}


def _db_count(table):
    path = os.environ["DATABASE_URL"].split("///", 1)[1]
    with sqlite3.connect(path) as c:
        return c.execute(f"select count(*) from {table}").fetchone()[0]


# 1. products can only be changed with the admin key
def test_create_product_needs_admin_key(client):
    assert client.post("/products", json=PRODUCT).status_code in (401, 403)
    assert client.post("/products", json=PRODUCT, headers={"X-Admin-Key": "wrong"}).status_code in (401, 403)
    r = client.post("/products", json=PRODUCT, headers=ADMIN)
    assert r.status_code == 201 and r.json()["slug"] == "test-roll"


def test_update_and_delete_product_with_admin_key(client):
    pid = next(p["id"] for p in client.get("/products").json() if p["slug"] == "test-roll")
    assert client.patch(f"/products/{pid}", json={"name": "Renamed"}).status_code in (401, 403)
    r = client.patch(f"/products/{pid}", json={"name": "Renamed Roll"}, headers=ADMIN)
    assert r.status_code == 200 and r.json()["name"] == "Renamed Roll" and r.json()["slug"] == "test-roll"
    assert client.delete(f"/products/{pid}").status_code in (401, 403)
    assert client.delete(f"/products/{pid}", headers=ADMIN).status_code == 204
    assert client.get(f"/products/{pid}").status_code == 404


def test_missing_product_is_a_404_and_slug_lookup_works(client):
    assert client.get("/products/00000000-0000-0000-0000-000000000000").status_code == 404
    assert client.get("/products/no-such-product").status_code == 404
    client.post("/products", json={**PRODUCT, "slug": "slug-roll"}, headers=ADMIN)
    assert client.get("/products/slug-roll").json()["slug"] == "slug-roll"


def test_products_come_in_a_stable_order(client):
    for s, c in (("z-roll", "a-line"), ("a-roll", "b-line"), ("b-roll", "a-line")):
        client.post("/products", json={**PRODUCT, "slug": s, "name": s, "category_slug": c}, headers=ADMIN)
    keys = [(p["category_slug"], p["name"]) for p in client.get("/products").json()]
    assert keys == sorted(keys)


# 2. the enquiry email cannot carry the sender's own HTML
def test_enquiry_email_escapes_what_the_visitor_typed():
    from backend.inquiries.notification_service import render_inquiry_email
    subject, html = render_inquiry_email({**INQUIRY, "full_name": "<b>Evil</b>",
                                          "message": '<a href="http://phish.example">Your bank</a>'})
    assert "<a href" not in html and "&lt;a href=" in html and "<b>Evil</b>" not in html
    assert subject.isascii()


# 3. enquiries: field limits and a per-visitor rate limit
def test_enquiry_rejects_oversized_fields(client):
    assert client.post("/inquiries", json={**INQUIRY, "message": "x" * 6000}).status_code == 422
    assert client.post("/inquiries", json={**INQUIRY, "phone_number": "1" * 40}).status_code == 422


def test_enquiry_is_saved(client):
    before = _db_count("inquiries")
    assert client.post("/inquiries", json=INQUIRY).status_code == 201
    assert _db_count("inquiries") == before + 1


def test_enquiries_are_rate_limited(client):
    from backend.inquiries import router as inquiries_router
    inquiries_router.limiter.reset()
    codes = [client.post("/inquiries", json=INQUIRY).status_code for _ in range(inquiries_router.limiter.limit + 2)]
    assert codes[: inquiries_router.limiter.limit] == [201] * inquiries_router.limiter.limit and codes[-1] == 429
    inquiries_router.limiter.reset()


# 4. no SQL echo (it printed customers' details to the logs)
def test_sql_echo_is_off():
    from backend.database import engine
    assert engine.echo is False


# 5. only the website's own addresses may call the API from a browser
def test_cors_allows_the_site_only(client):
    ok = client.options("/inquiries", headers={"Origin": "https://www.thermalpaperlabels.com", "Access-Control-Request-Method": "POST"})
    assert ok.headers.get("access-control-allow-origin") == "https://www.thermalpaperlabels.com"
    bad = client.options("/inquiries", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    assert bad.headers.get("access-control-allow-origin") is None


# 6. the reset script refuses a real (non-SQLite) database
def test_reset_refuses_production():
    from backend.scripts.reset_db import guard
    import pytest
    with pytest.raises(SystemExit):
        guard("postgresql+asyncpg://user:pw@db.example/prod", force=False)
    guard("sqlite+aiosqlite:///./local.db", force=False)
