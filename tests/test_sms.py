import json

URL = "/sandbox/sms/send"


def _post(client, payload, headers=None):
    return client.post(
        URL,
        data=json.dumps(payload),
        content_type="application/json",
        headers=headers or {},
    )


def test_send_requires_api_key(client):
    resp = _post(client, {"receptor": "09123456789", "message": "hi"})
    assert resp.status_code == 401


def test_send_rejects_invalid_api_key(client):
    resp = _post(
        client,
        {"receptor": "09123456789", "message": "hi"},
        {"X-API-Key": "nope"},
    )
    assert resp.status_code == 401


def test_send_success(client, api_headers):
    resp = _post(
        client,
        {"receptor": "+989123456789", "message": "Hello from sandbox!"},
        api_headers,
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["return"]["status"] == 200
    assert body["entries"]["status"] == 10
    # Receptor is normalized to the 09xxxxxxxxx form.
    assert body["entries"]["receptor"] == "09123456789"
    assert body["entries"]["message"] == "Hello from sandbox!"
    assert isinstance(body["entries"]["messageid"], int)


def test_send_rejects_bad_phone(client, api_headers):
    resp = _post(client, {"receptor": "12345", "message": "hi"}, api_headers)
    assert resp.status_code == 411


def test_send_rejects_long_message(client, api_headers):
    resp = _post(
        client, {"receptor": "09123456789", "message": "x" * 901}, api_headers
    )
    assert resp.status_code == 413


def test_send_rejects_missing_field(client, api_headers):
    resp = _post(client, {"receptor": "09123456789"}, api_headers)
    assert resp.status_code == 400
