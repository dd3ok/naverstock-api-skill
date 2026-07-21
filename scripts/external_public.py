#!/usr/bin/env python3
"""Bounded helpers for explicitly approved public HTML sources."""

from __future__ import annotations

import html
from html.parser import HTMLParser
import http.client
import re
import socket
from typing import Any
import urllib.error
import urllib.parse
import urllib.request

from naverstock_api import bounded_int, normalize_item_code


DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 60
MAX_RESPONSE_BYTES = 5 * 1024 * 1024

WISEREPORT_COMPANY_PATHS = {
    "status": "/v3/company/c1010001.aspx",
    "overview": "/v3/company/c1020001.aspx",
    "financial-analysis": "/v3/company/c1030001.aspx",
    "indicators": "/v3/company/c1040001.aspx",
    "consensus": "/v3/company/c1050001.aspx",
    "industry": "/v3/company/c1060001.aspx",
    "shareholders": "/v3/company/c1070001.aspx",
    "sector": "/v3/company/c1090001.aspx",
}

FINANCE_TECHNICAL_PATHS = {
    "disparity-overheat": "/sise/item_igyuk.naver",
    "gap-up": "/sise/item_gap.naver",
    "golden-cross": "/sise/item_gold.naver",
    "relative-strength-overheat": "/sise/item_overheating_2.naver",
    "sentiment-overheat": "/sise/item_overheating_1.naver",
}

FINANCE_PRICE_POSITION_PATHS = {
    "high-down": "/sise/sise_high_down.naver",
    "low-up": "/sise/sise_low_up.naver",
}

SOURCE_CONFIG = {
    "finance": {
        "base_url": "https://finance.naver.com",
        "paths": frozenset(
            {*FINANCE_TECHNICAL_PATHS.values(), *FINANCE_PRICE_POSITION_PATHS.values()}
        ),
        "query_keys": frozenset({"page", "sosok"}),
        "referer": "https://finance.naver.com/sise/",
    },
    "wisereport": {
        "base_url": "https://navercomp.wisereport.co.kr",
        "paths": frozenset(WISEREPORT_COMPANY_PATHS.values()),
        "query_keys": frozenset({"cmp_cd"}),
        "referer": "https://stock.naver.com/",
    },
}

class ExternalRequestValidationError(ValueError):
    """Raised when an external request is outside the narrow public allowlist."""


class ExternalPublicError(RuntimeError):
    """Raised when an approved external public source cannot be read safely."""


def build_external_url(
    source: str, path: str, params: dict[str, Any] | None = None
) -> str:
    config = SOURCE_CONFIG.get(source)
    if config is None:
        raise ExternalRequestValidationError(f"Unsupported external source: {source}")
    if path not in config["paths"]:
        raise ExternalRequestValidationError(
            f"Path is outside the {source} public-read allowlist: {path}"
        )

    clean_params: dict[str, str] = {}
    for key, value in (params or {}).items():
        if value is None:
            continue
        if key not in config["query_keys"]:
            raise ExternalRequestValidationError(
                f"Unsupported {source} query parameter: {key}"
            )
        if key == "cmp_cd":
            try:
                clean_params[key] = normalize_item_code(str(value))
            except ValueError as exc:
                raise ExternalRequestValidationError(str(exc)) from exc
        elif key == "page":
            clean_params[key] = str(
                bounded_int(value, name="page", minimum=1, maximum=10_000)
            )
        elif key == "sosok":
            clean = str(value)
            if clean not in {"0", "1"}:
                raise ExternalRequestValidationError("sosok must be 0 or 1")
            clean_params[key] = clean

    query = urllib.parse.urlencode(clean_params)
    url = str(config["base_url"]) + path
    return f"{url}?{query}" if query else url


def request_public_html(
    source: str,
    path: str,
    params: dict[str, Any] | None = None,
    *,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    clean_timeout = bounded_int(
        timeout, name="timeout", minimum=1, maximum=MAX_TIMEOUT
    )
    url = build_external_url(source, path, params)
    config = SOURCE_CONFIG[source]
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "text/html,application/xhtml+xml",
            "Referer": str(config["referer"]),
            "User-Agent": "Mozilla/5.0 naverstock-web-api-skill/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=clean_timeout) as response:
            final_url = response.geturl()
            _validate_final_url(url, final_url)
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            content_type = response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read(2_048).decode("utf-8", errors="replace")
        if exc.code in {403, 429}:
            message = (
                f"External public source returned HTTP {exc.code}. "
                "Stop; do not retry automatically."
            )
        else:
            message = f"External public source returned HTTP {exc.code}"
        raise ExternalPublicError(f"{message}: {detail}") from exc
    except (TimeoutError, socket.timeout) as exc:
        raise ExternalPublicError(
            f"External public source timed out after {clean_timeout} seconds"
        ) from exc
    except urllib.error.URLError as exc:
        raise ExternalPublicError(
            f"External public source request failed: {exc.reason}"
        ) from exc
    except (http.client.HTTPException, OSError) as exc:
        raise ExternalPublicError(
            f"External public source transport failed: {exc}"
        ) from exc

    if len(raw) > MAX_RESPONSE_BYTES:
        raise ExternalPublicError(
            f"External public source exceeded {MAX_RESPONSE_BYTES} response bytes"
        )
    if content_type and not content_type.casefold().startswith(
        ("text/html", "application/xhtml+xml")
    ):
        raise ExternalPublicError(
            f"External public source returned unexpected content type: {content_type}"
        )
    return _decode_html(raw, content_type)


def extract_tables(markup: str) -> list[dict[str, Any]]:
    parser = _TableParser()
    parser.feed(markup)
    parser.close()
    return parser.tables


def clean_cell(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def strip_tags(markup: str) -> str:
    text = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", markup)
    return clean_cell(re.sub(r"(?s)<[^>]+>", " ", text))


def _validate_final_url(requested_url: str, final_url: str) -> None:
    requested = urllib.parse.urlsplit(requested_url)
    final = urllib.parse.urlsplit(final_url)
    if (
        final.scheme != "https"
        or final.hostname != requested.hostname
        or final.path != requested.path
        or final.query != requested.query
    ):
        raise ExternalPublicError(
            "External public source redirected outside the approved path"
        )


def _decode_html(raw: bytes, content_type: str) -> str:
    match = re.search(r"charset=([^;\s]+)", content_type, flags=re.I)
    candidates = [match.group(1).strip('"\'')] if match else []
    candidates.extend(["utf-8", "euc-kr", "cp949"])
    for encoding in dict.fromkeys(candidates):
        try:
            return raw.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode("utf-8", errors="replace")


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[dict[str, Any]] = []
        self._stack: list[dict[str, Any]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        tag = tag.casefold()
        if tag == "table":
            self._stack.append(
                {
                    "table": {"attrs": dict(attrs), "rows": []},
                    "row": None,
                    "cell": None,
                }
            )
            return
        if not self._stack:
            return
        current = self._stack[-1]
        if tag == "tr":
            current["row"] = []
        elif tag in {"td", "th"}:
            current["cell"] = []
        elif current["cell"] is not None and tag in {"br", "div", "p"}:
            current["cell"].append(" ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if not self._stack:
            return
        current = self._stack[-1]
        if tag in {"td", "th"} and current["cell"] is not None:
            if current["row"] is not None:
                current["row"].append(clean_cell("".join(current["cell"])))
            current["cell"] = None
        elif tag == "tr" and current["row"] is not None:
            current["table"]["rows"].append(current["row"])
            current["row"] = None
        elif tag == "table":
            finished = self._stack.pop()["table"]
            self.tables.append(finished)

    def handle_data(self, data: str) -> None:
        if self._stack and self._stack[-1]["cell"] is not None:
            self._stack[-1]["cell"].append(data)
