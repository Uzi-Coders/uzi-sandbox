def test_login_page_loads(client):
    resp = client.get("/sandbox/auth/login")
    assert resp.status_code == 200


def test_dashboard_requires_login(client):
    resp = client.get("/sandbox/")
    assert resp.status_code == 302
    assert "/sandbox/auth/login" in resp.headers["Location"]


def test_login_success(client, user):
    resp = client.post(
        "/sandbox/auth/login",
        data={"username": user.username, "password": user.password},
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/sandbox/")
    assert client.get("/sandbox/").status_code == 200


def test_login_wrong_password(client, user):
    resp = client.post(
        "/sandbox/auth/login",
        data={"username": user.username, "password": "wrong-password"},
    )
    assert resp.status_code == 200
    assert b"Invalid username or password." in resp.data


def test_logout_requires_login(client):
    resp = client.post("/sandbox/auth/logout")
    assert resp.status_code == 302
    assert "/sandbox/auth/login" in resp.headers["Location"]


def test_logout_after_login(client, user):
    client.post(
        "/sandbox/auth/login",
        data={"username": user.username, "password": user.password},
    )
    resp = client.post("/sandbox/auth/logout")
    assert resp.status_code == 302
    assert client.get("/sandbox/").status_code == 302
