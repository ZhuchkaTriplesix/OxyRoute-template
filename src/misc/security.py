from __future__ import annotations

import base64
import secrets


def parse_basic_auth(value: str | None) -> tuple[str, str] | None:
    if not value:
        return None

    scheme, _, token = value.partition(" ")
    if scheme.lower() != "basic" or not token:
        return None

    try:
        decoded = base64.b64decode(token, validate=True).decode("utf-8")
    except ValueError:
        return None
    except UnicodeDecodeError:
        return None

    username, separator, password = decoded.partition(":")
    if not separator:
        return None
    return username, password


def basic_auth_matches(
    authorization: str | None,
    expected_username: str,
    expected_password: str,
) -> bool:
    credentials = parse_basic_auth(authorization)
    if credentials is None:
        return False

    username, password = credentials
    return secrets.compare_digest(username, expected_username) and secrets.compare_digest(
        password,
        expected_password,
    )
