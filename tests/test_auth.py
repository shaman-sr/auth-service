from httpx import AsyncClient

REGISTER = {"username": "alice", "email": "alice@example.com", "password": "pw"}


async def _register_and_login(client: AsyncClient) -> dict[str, str]:
    reg = await client.post("/auth/register", json=REGISTER)
    assert reg.status_code == 201
    login = await client.post("/auth/login", json={"username": "alice", "password": "pw"})
    assert login.status_code == 200
    return login.json()


async def test_register_does_not_leak_password(client: AsyncClient) -> None:
    reg = await client.post("/auth/register", json=REGISTER)
    assert reg.status_code == 201
    body = reg.json()
    assert body["username"] == "alice"
    assert "id" in body
    assert "password" not in body and "hashed_password" not in body


async def test_login_returns_jwt_pair(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)
    assert tokens["access_token"] and tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"
    # JWTs have three dot-separated segments.
    assert tokens["access_token"].count(".") == 2


async def test_refresh_rotates_and_invalidates_old_token(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)

    rotated = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert rotated.status_code == 200
    new_tokens = rotated.json()
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    # The old refresh token no longer works after rotation.
    reused = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert reused.status_code == 401


async def test_logout_requires_bearer_token(client: AsyncClient) -> None:
    resp = await client.post("/auth/logout")
    # HTTPBearer rejects a missing Authorization header (401/403 across versions).
    assert resp.status_code in (401, 403)


async def test_logout_revokes_refresh_token(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)

    logout = await client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert logout.status_code == 200

    # Refresh is rejected once the token has been revoked by logout.
    after = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert after.status_code == 401


async def test_register_duplicate_conflicts(client: AsyncClient) -> None:
    first = await client.post("/auth/register", json=REGISTER)
    assert first.status_code == 201
    dup = await client.post("/auth/register", json=REGISTER)
    assert dup.status_code == 409


async def test_login_bad_credentials(client: AsyncClient) -> None:
    await client.post("/auth/register", json=REGISTER)
    resp = await client.post("/auth/login", json={"username": "alice", "password": "wrong"})
    assert resp.status_code == 401
