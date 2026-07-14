from httpx import AsyncClient

REGISTER = {"username": "alice", "email": "alice@example.com", "password": "pw"}


async def test_register_login_logout_flow(client: AsyncClient) -> None:
    # Register
    reg = await client.post("/auth/register", json=REGISTER)
    assert reg.status_code == 201
    body = reg.json()
    assert body["username"] == "alice"
    assert "id" in body
    assert "password" not in body and "hashed_password" not in body

    # Login
    login = await client.post("/auth/login", json={"username": "alice", "password": "pw"})
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["access_token"] and tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"

    # Logout with the issued refresh token
    logout = await client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logout.status_code == 200

    # The refresh token is now revoked
    again = await client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert again.status_code == 401


async def test_register_duplicate_conflicts(client: AsyncClient) -> None:
    first = await client.post("/auth/register", json=REGISTER)
    assert first.status_code == 201
    dup = await client.post("/auth/register", json=REGISTER)
    assert dup.status_code == 409


async def test_login_bad_credentials(client: AsyncClient) -> None:
    await client.post("/auth/register", json=REGISTER)
    resp = await client.post("/auth/login", json={"username": "alice", "password": "wrong"})
    assert resp.status_code == 401
