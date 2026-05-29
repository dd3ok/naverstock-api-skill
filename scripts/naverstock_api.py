#!/usr/bin/env python3
"""Shared helpers for read-only Naver Stock web API scripts."""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
import sys
from typing import Any
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = "https://stock.naver.com"
DEFAULT_TIMEOUT = 30


def normalize_item_code(code: str) -> str:
    value = code.strip().upper()
    if value.startswith("A") and value[1:].isdigit() and len(value) == 7:
        return value[1:]
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
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        method=method,
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
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Naver Stock API returned HTTP {exc.code}: {detail}") from exc
    payload = json.loads(text)
    if isinstance(payload, dict) and ("detailCode" in payload or payload.get("error")):
        raise RuntimeError(f"Naver Stock API returned error payload: {payload}")
    return payload


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
            except (AttributeError, ValueError):
                pass
        print(text, end="" if text.endswith("\n") else "\n")


def add_output_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", help="Write output to a file instead of stdout")


def _query_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
