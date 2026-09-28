import json

PAY_URL = "/sandbox/gateway/payment"
VERIFY_URL = "/sandbox/gateway/payment/verify"


def _post_json(client, url, payload, headers):
    return client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
        headers=headers,
    )


def _create_payment(client, api_headers, **overrides):
    payload = {
        "order_id": "order-123",
        "amount": 50000,
        "callback": "https://myshop.ir/verify",
    }
    payload.update(overrides)
    return _post_json(client, PAY_URL, payload, api_headers)


def test_create_payment_success(client, api_headers):
    resp = _create_payment(client, api_headers)
    assert resp.status_code == 201
    body = resp.get_json()
    assert len(body["id"]) == 32
    assert body["link"].endswith(f"/sandbox/gateway/fake-pay/{body['id']}")


def test_create_payment_rejects_small_amount(client, api_headers):
    resp = _create_payment(client, api_headers, amount=500)
    assert resp.status_code == 400


def test_create_payment_rejects_bad_callback(client, api_headers):
    resp = _create_payment(client, api_headers, callback="ftp://myshop.ir/x")
    assert resp.status_code == 400


def test_create_payment_requires_api_key(client):
    resp = _post_json(
        client,
        PAY_URL,
        {"order_id": "o", "amount": 50000, "callback": "https://x.ir"},
        {},
    )
    assert resp.status_code == 401


def test_fake_pay_page_only_while_pending(client, api_headers):
    tx_id = _create_payment(client, api_headers).get_json()["id"]
    assert client.get(f"/sandbox/gateway/fake-pay/{tx_id}").status_code == 200


def test_confirm_then_verify(client, api_headers):
    tx_id = _create_payment(client, api_headers).get_json()["id"]

    confirm = client.post(
        f"/sandbox/gateway/fake-pay/{tx_id}", data={"action": "confirm"}
    )
    assert confirm.status_code == 302
    assert "status=10" in confirm.headers["Location"]

    verify = _post_json(
        client, VERIFY_URL, {"id": tx_id, "order_id": "order-123"}, api_headers
    )
    assert verify.status_code == 200
    body = verify.get_json()
    assert body["status"] == "100"
    assert body["order_id"] == "order-123"
    assert body["payment"]["card_no"]

    # Second verify must fail: already verified.
    again = _post_json(
        client, VERIFY_URL, {"id": tx_id, "order_id": "order-123"}, api_headers
    )
    assert again.status_code == 405
    assert again.get_json()["error_code"] == 53


def test_cancel_cannot_be_verified(client, api_headers):
    tx_id = _create_payment(client, api_headers).get_json()["id"]

    cancel = client.post(
        f"/sandbox/gateway/fake-pay/{tx_id}", data={"action": "cancel"}
    )
    assert cancel.status_code == 302
    assert "status=2" in cancel.headers["Location"]

    verify = _post_json(
        client, VERIFY_URL, {"id": tx_id, "order_id": "order-123"}, api_headers
    )
    assert verify.status_code == 405
    assert verify.get_json()["error_code"] == 53


def test_verify_unknown_transaction(client, api_headers):
    resp = _post_json(
        client,
        VERIFY_URL,
        {"id": "0" * 32, "order_id": "nope"},
        api_headers,
    )
    assert resp.status_code == 400
    assert resp.get_json()["error_code"] == 52


def test_verify_rejects_missing_fields(client, api_headers):
    resp = _post_json(client, VERIFY_URL, {"id": "abc"}, api_headers)
    assert resp.status_code == 406
    assert resp.get_json()["error_code"] == 31
