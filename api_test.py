import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:5000"


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def show(title, result):
    status, data = result
    print(f"\n=== {title} (status {status}) ===")
    print(json.dumps(data, indent=2))


show("1. Add product", call("POST", "/api/products", {
    "name": "Custom Name Resin Keychain",
    "price": 150,
    "category_id": 1,
}))

show("2. Create order", call("POST", "/api/orders", {
    "customer": {
        "name": "Priya",
        "phone": "9876543210",
        "address": "Anna Nagar, Madurai",
    },
    "items": [
        {"product_id": 1, "quantity": 2, "customization_note": "Name: Priya, colour: pink"}
    ],
}))

show("3. Mark paid", call("PUT", "/api/orders/1/payment", {"upi_reference": "UPI123456"}))

show("4. Update status", call("PUT", "/api/orders/1/status", {"status": "In Making"}))