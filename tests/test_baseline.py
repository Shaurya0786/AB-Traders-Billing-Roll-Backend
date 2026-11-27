def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

def test_products_list(client):
    r = client.get("/products")
    assert r.status_code == 200 and isinstance(r.json(), list)
