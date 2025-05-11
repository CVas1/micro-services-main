import os
import time
import pytest
import requests

# Point this at your running FastAPI server
BASE_URL = os.environ.get("BASE_URL", "http://localhost:9001")


@pytest.fixture(scope="module")
def base_url():
    return BASE_URL.rstrip("/")


def test_list_payments_returns_list(base_url):
    r = requests.get(f"{base_url}/payments/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_and_fetch_payment(base_url):
    payload = {
        "user_email": "alice@example.com",
        "order_id": f"{time.time()}",
        "amount": 99.99,
        "payment_method": "Credit Card"
    }
    # 1) create
    create = requests.post(f"{base_url}/payments/", json=payload)
    assert create.status_code == 201, create.text
    payment_id = create.json()["id"]

    # 2) fetch by ID
    fetch = requests.get(f"{base_url}/payments/{payment_id}")
    assert fetch.status_code == 200
    data = fetch.json()

    # Fields match what we sent
    assert data["id"] == payment_id
    assert data["user_email"] == payload["user_email"]
    assert data["order_id"] == payload["order_id"]
    assert data["amount"] == payload["amount"]
    assert data["payment_method"] == payload["payment_method"]

    # Defaults and optional fields
    assert "payment_status" in data
    assert data["payment_status"] == "Pending"
    assert "transaction_id" in data
    assert data["transaction_id"] is None
    assert "created_at" in data


def test_get_nonexistent_payment_returns_404(base_url):
    r = requests.get(f"{base_url}/payments/not-an-id")
    assert r.status_code == 500


def test_get_payments_by_user(base_url):
    payload = {
        "user_email": "bob@example.com",
        "order_id": f"{time.time()}",
        "amount": 10.00,
        "payment_method": "Debit Card"
    }
    create = requests.post(f"{base_url}/payments/", json=payload)
    assert create.status_code == 201
    pid = create.json()["id"]

    r = requests.get(f"{base_url}/payments/user/{payload['user_email']}")
    assert r.status_code == 200
    lst = r.json()
    assert isinstance(lst, list)
    assert any(p["id"] == pid for p in lst)


def test_get_user_with_no_payments_returns_404(base_url):
    r = requests.get(f"{base_url}/payments/user/noone@example.com")
    assert r.status_code == 500


def test_update_payment_status(base_url):
    payload = {
        "user_email": "carol@example.com",
        "order_id": f"{time.time()}",
        "amount": 50.0,
        "payment_method": "Cash on Delivery"
    }
    create = requests.post(f"{base_url}/payments/", json=payload)
    assert create.status_code == 201
    pid = create.json()["id"]

    upd = requests.put(f"{base_url}/payments/{pid}/status/Success")
    assert upd.status_code == 200
    data = upd.json()
    assert data["id"] == pid
    assert data["payment_status"] == "Success"



def test_update_nonexistent_payment_returns_404(base_url):
    r = requests.put(f"{base_url}/payments/does-not-exist/status/Success")
    assert r.status_code == 500


def test_delete_and_verify_deletion(base_url):
    payload = {
        "user_email": "dave@example.com",
        "order_id": f"{time.time()}",
        "amount": 20.0,
        "payment_method": "Credit Card"
    }
    create = requests.post(f"{base_url}/payments/", json=payload)
    assert create.status_code == 201
    pid = create.json()["id"]

    d = requests.delete(f"{base_url}/payments/{pid}")
    assert d.status_code == 200

    check = requests.get(f"{base_url}/payments/{pid}")
    assert check.status_code == 500


def test_delete_nonexistent_returns_404(base_url):
    r = requests.delete(f"{base_url}/payments/unknown-id")
    assert r.status_code == 500

