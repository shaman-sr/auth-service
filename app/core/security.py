"""Security primitives for the auth flow.

⚠️  PLACEHOLDERS — these implementations are INSECURE and exist only so the
auth skeleton runs end to end. Every function below is an intentional
decision point left to you:

  * password hashing  -> pick a KDF (bcrypt / argon2 via passlib, etc.)
  * token format      -> opaque vs JWT, claims, signing key
  * token lifetime    -> access/refresh expiry + refresh rotation

Replace the bodies; the call sites in the services/routes stay the same.
"""

import uuid


def hash_password(password: str) -> str:
    # TODO(auth): replace with a real password hash (e.g. passlib bcrypt/argon2).
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # TODO(auth): replace with the verifier matching hash_password().
    return plain_password == hashed_password


def create_access_token(subject: str) -> str:
    # TODO(auth): issue a real access token (e.g. signed JWT with exp claim).
    return uuid.uuid4().hex


def create_refresh_token(subject: str) -> str:
    # TODO(auth): issue a real refresh token with an expiry + rotation strategy.
    return uuid.uuid4().hex
