#!/usr/bin/env python3
"""Shared helpers for read-only Naver Stock web API scripts."""

from __future__ import annotations

import argparse
import csv
import http.client
import io
import json
from pathlib import Path
import re
import socket
import sys
from typing import Any
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = "https://stock.naver.com"
DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 120

# These are deliberately API-family allowlists, not a blanket ``/api`` pass.
# Every caller is still restricted to GET unless its exact path appears in the
# read-only POST allowlist below.
PUBLIC_READ_PREFIXES = (
    "/api/coin/",
    "/api/community/discussion/",
    "/api/content/",
    "/api/domestic/",
    "/api/foreign/",
    "/api/polling/",
    "/api/securityai/",
    "/api/securityfe/",
    "/api/securityservice/",
    "/api/stockdomestic/",
    "/api/stocksecurity/",
)
PUBLIC_READ_EXACT_PATHS = frozenset(
    {
        "/api/autocomplete/search",
        "/api/autocomplete/search/autocomplete",
        "/api/myasset/resources/invest/stock-floor",
        "/api/myasset/resources/invest/stock-invest-rate",
        "/api/myasset/resources/invest/stock-investor-age",
        "/api/myasset/resources/invest/stock-investor-rank",
        "/api/myasset/resources/invest/stock-trade",
        "/api/shorttents",
    }
)
_COIN_PROFILE_PATH = re.compile(r"^/api/coin/profile/[a-z0-9][a-z0-9_-]{0,31}$")
READ_ONLY_POST_PATHS = frozenset(
    {
        "/api/domestic/home/marketaggregate/aggregateinvestor",
    }
)

_DENIED_PATH_SEGMENTS = frozenset(
    {
        "account",
        "accounts",
        "auth",
        "authorization",
        "block",
        "bookmark",
        "cancel",
        "create",
        "delete",
        "favorite",
        "favorites",
        "follow",
        "holding",
        "holdings",
        "like",
        "login",
        "logout",
        "member",
        "members",
        "mystock",
        "myasset",
        "notification",
        "notification-settings",
        "notifications",
        "order",
        "orders",
        "personal",
        "portfolio",
        "profile",
        "profiles",
        "reaction",
        "report",
        "register",
        "session",
        "settings",
        "subscribe",
        "unsubscribe",
        "update",
        "user",
        "users",
    }
)
_DENIED_PATH_PREFIXES = (
    "/api/securityfe/api/mystock/",
    "/api/securityservice/home/v3/mystock/",
    "/api/stockdomestic/notification-settings/",
)
_SENSITIVE_INPUT_KEYS = frozenset(
    {
        "accessToken",
        "accountId",
        "accountNumber",
        "authorization",
        "memberId",
        "memberNo",
        "orderNo",
        "password",
        "pin",
        "profileId",
        "profileNo",
        "refreshToken",
        "sessionId",
        "uno",
        "userId",
        "userNo",
        "viewerProfileId",
    }
)
_SENSITIVE_INPUT_KEYS_NORMALIZED = frozenset(
    re.sub(r"[-_.\s]", "", key).casefold() for key in _SENSITIVE_INPUT_KEYS
)
_PAGINATION_BOUNDS = {
    "count": (1, 500),
    "index": (0, 100_000),
    "limit": (1, 500),
    "page": (0, 10_000),
    "pagesize": (1, 500),
    "size": (1, 500),
    "startidx": (0, 100_000),
}
_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
_ENCODED_PATH_CONTROL = re.compile(r"%(?:00|0a|0d|2e|2f|5c)", re.IGNORECASE)


class RequestValidationError(ValueError):
    """Raised when a request falls outside the public read-only boundary."""


class NaverStockAPIError(RuntimeError):
    """Represent a remote Naver Stock API failure with structured context."""

    def __init__(
        self,
        message: str,
        *,
        path: str,
        status_code: int | None = None,
        detail: str | None = None,
    ) -> None:
        super().__init__(message)
        self.path = path
        self.status_code = status_code
        self.detail = detail

    def as_dict(self) -> dict[str, Any]:
        error: dict[str, Any] = {"message": str(self), "path": self.path}
        if self.status_code is not None:
            error["statusCode"] = self.status_code
        if self.detail:
            try:
                error["detail"] = json.loads(self.detail)
            except (json.JSONDecodeError, TypeError):
                error["detail"] = self.detail
        return error


def normalize_item_code(code: str) -> str:
    value = code.strip().upper() if isinstance(code, str) else ""
    if value.startswith("A") and value[1:].isdigit() and len(value) == 7:
        value = value[1:]
    if not (len(value) == 6 and value.isascii() and value.isdigit()):
        raise ValueError("item code must be exactly six digits, optionally prefixed with A")
    return value


def build_path(path: str, params: dict[str, Any] | None = None) -> str:
    if not params:
        return path
    query = urllib.parse.urlencode(
        [(key, _query_value(value)) for key, value in params.items() if value is not None],
        doseq=True,
    )
    return f"{path}?{query}" if query else path


def request_json(
    path: str,
    *,
    method: str = "GET",
    body: Any | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Any:
    clean_path = validate_public_request(path, method=method, body=body, timeout=timeout)
    clean_method = method.strip().upper()
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    if data is not None and len(data) > 65_536:
        raise RequestValidationError("Request body is too large for a bounded read-only query")
    req = urllib.request.Request(
        BASE_URL + clean_path,
        data=data,
        method=clean_method,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://stock.naver.com/",
            "User-Agent": "Mozilla/5.0 naverstock-web-api-skill/1.0",
            **({"Content-Type": "application/json"} if data is not None else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read(2_048).decode("utf-8", errors="replace")
        if exc.code in {403, 429}:
            message = (
                f"Naver Stock API returned HTTP {exc.code}. Stop; do not retry automatically. "
                "Re-verify that the endpoint is public and wait before trying again."
            )
        else:
            message = f"Naver Stock API returned HTTP {exc.code}"
        raise NaverStockAPIError(
            message,
            path=clean_path,
            status_code=exc.code,
            detail=detail,
        ) from exc
    except (TimeoutError, socket.timeout) as exc:
        raise NaverStockAPIError(
            f"Naver Stock API request timed out after {timeout} seconds",
            path=clean_path,
            detail=str(exc),
        ) from exc
    except urllib.error.URLError as exc:
        raise NaverStockAPIError(
            "Naver Stock API request failed",
            path=clean_path,
            detail=str(exc.reason),
        ) from exc
    except UnicodeDecodeError as exc:
        raise NaverStockAPIError(
            "Naver Stock API returned a non-UTF-8 response",
            path=clean_path,
            detail=str(exc),
        ) from exc
    except (http.client.HTTPException, OSError) as exc:
        raise NaverStockAPIError(
            "Naver Stock API transport failed",
            path=clean_path,
            detail=str(exc),
        ) from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        preview = text[:200].replace("\n", " ")
        raise NaverStockAPIError(
            "Naver Stock API returned invalid JSON (a non-JSON response)",
            path=clean_path,
            detail=preview,
        ) from exc
    if isinstance(payload, dict) and ("detailCode" in payload or payload.get("error")):
        status_code = payload.get("statusCode")
        raise NaverStockAPIError(
            "Naver Stock API returned an error payload",
            path=clean_path,
            status_code=status_code if isinstance(status_code, int) else None,
            detail=json.dumps(payload, ensure_ascii=False),
        )
    return payload


def validate_public_request(
    path: str,
    *,
    method: str = "GET",
    body: Any | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """Validate a same-origin, public, bounded read-only API request."""

    if not isinstance(path, str) or not path:
        raise RequestValidationError("API path must be a non-empty string")
    if len(path) > 8_192:
        raise RequestValidationError("API path and query must not exceed 8192 characters")
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= MAX_TIMEOUT:
        raise RequestValidationError(f"timeout must be an integer from 1 to {MAX_TIMEOUT} seconds")
    if "\\" in path or any(ord(char) < 32 or ord(char) == 127 for char in path):
        raise RequestValidationError("API path contains an unsafe character")

    parsed = urllib.parse.urlsplit(path)
    if parsed.scheme or parsed.netloc or parsed.fragment:
        raise RequestValidationError("API path must be a same-origin relative path without a fragment")
    if not parsed.path.startswith("/api/") or parsed.path.startswith("//"):
        raise RequestValidationError("API path must start with exactly /api/")

    decoded_path = parsed.path
    for _ in range(3):
        if _ENCODED_PATH_CONTROL.search(decoded_path):
            raise RequestValidationError("Encoded separators, dot segments, and controls are not allowed in API paths")
        next_path = urllib.parse.unquote(decoded_path)
        if next_path == decoded_path:
            break
        decoded_path = next_path
    if "\\" in decoded_path or any(ord(char) < 32 or ord(char) == 127 for char in decoded_path):
        raise RequestValidationError("Decoded API path contains an unsafe character")
    segments = decoded_path.split("/")
    if any(segment in {".", ".."} for segment in segments):
        raise RequestValidationError("Dot segments are not allowed in API paths")

    normalized_path = decoded_path.casefold()
    normalized_segments = {segment.casefold() for segment in segments if segment}
    is_public_resource = normalized_path in PUBLIC_READ_EXACT_PATHS
    is_public_coin_profile = _COIN_PROFILE_PATH.fullmatch(normalized_path) is not None
    if any(normalized_path.startswith(prefix) for prefix in _DENIED_PATH_PREFIXES):
        raise RequestValidationError("API path crosses a private or mutating boundary")
    denied_segments = normalized_segments & _DENIED_PATH_SEGMENTS
    if denied_segments and not is_public_resource and not is_public_coin_profile:
        denied = ", ".join(sorted(denied_segments))
        raise RequestValidationError(f"API path crosses a private or mutating boundary: {denied}")

    is_public_read = (
        any(normalized_path.startswith(prefix) for prefix in PUBLIC_READ_PREFIXES)
        or is_public_resource
    )
    if not is_public_read:
        raise RequestValidationError("API path is outside the approved public-read families")

    clean_method = method.strip().upper() if isinstance(method, str) else ""
    if clean_method == "GET":
        if body is not None:
            raise RequestValidationError("GET requests cannot include a body")
    elif clean_method == "POST":
        if normalized_path not in READ_ONLY_POST_PATHS:
            raise RequestValidationError("POST is allowed only for an explicitly approved read-only endpoint")
        if body is None:
            raise RequestValidationError("Approved read-only POST requests require a JSON body")
    else:
        raise RequestValidationError("Only GET and explicitly approved read-only POST requests are allowed")

    query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    if len(query_pairs) > 100:
        raise RequestValidationError("API query has too many parameters")
    if any(len(key) > 128 or len(value) > 4_096 for key, value in query_pairs):
        raise RequestValidationError("API query key or value is too long")
    _reject_sensitive_keys(key for key, _ in query_pairs)
    _validate_pagination(query_pairs)
    if body is not None:
        _validate_body_keys(body)
    return path


def bounded_int(value: int | str, *, name: str, minimum: int, maximum: int) -> int:
    """Return an integer inside an explicit inclusive bound."""

    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer from {minimum} to {maximum}")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer from {minimum} to {maximum}") from exc
    if not minimum <= parsed <= maximum:
        raise ValueError(f"{name} must be an integer from {minimum} to {maximum}")
    return parsed


def validate_identifier(value: str, *, name: str = "identifier") -> str:
    """Validate an identifier before interpolating it into an API path."""

    clean = value.strip() if isinstance(value, str) else ""
    if not _SAFE_IDENTIFIER.fullmatch(clean):
        raise ValueError(f"{name} must contain only letters, digits, underscore, or hyphen")
    return clean


def _reject_sensitive_keys(keys: Any) -> None:
    for key in keys:
        normalized = re.sub(r"[-_.\s]", "", str(key)).casefold()
        if normalized in _SENSITIVE_INPUT_KEYS_NORMALIZED:
            raise RequestValidationError(f"Sensitive query/body key is not allowed: {key}")


def _validate_body_keys(value: Any, *, depth: int = 0) -> None:
    if depth > 32:
        raise RequestValidationError("Request body is nested too deeply")
    if isinstance(value, dict):
        _reject_sensitive_keys(value.keys())
        for nested in value.values():
            _validate_body_keys(nested, depth=depth + 1)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            _validate_body_keys(nested, depth=depth + 1)


def _validate_pagination(query_pairs: list[tuple[str, str]]) -> None:
    for key, value in query_pairs:
        normalized = re.sub(r"[-_.\s]", "", key).casefold()
        bounds = _PAGINATION_BOUNDS.get(normalized)
        if bounds is None:
            continue
        minimum, maximum = bounds
        try:
            bounded_int(value, name=key, minimum=minimum, maximum=maximum)
        except ValueError as exc:
            raise RequestValidationError(str(exc)) from exc


def render_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def emit_output(text: str, output_path: str | None) -> None:
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8")
            except (AttributeError, ValueError, OSError):
                pass
        print(text, end="" if text.endswith("\n") else "\n")


def add_output_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", help="Write output to a file instead of stdout")


def _query_value(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return [_query_value(item) for item in value]
    return str(value)
