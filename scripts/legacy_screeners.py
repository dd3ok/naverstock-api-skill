#!/usr/bin/env python3
"""Fetch selected legacy-only Naver Finance public stock screeners."""

from __future__ import annotations

import argparse
import re
from typing import Any

from external_public import (
    FINANCE_PRICE_POSITION_PATHS,
    FINANCE_TECHNICAL_PATHS,
    clean_cell,
    extract_tables,
    request_public_html,
    strip_tags,
)
from naverstock_api import bounded_int, emit_output, render_json


MARKET_CODES = {"KOSDAQ": "1", "KOSPI": "0"}
TABLE_CLASSES = {"price-position": "type_2", "technical": "type_5"}


def fetch_technical(args: argparse.Namespace) -> dict[str, Any]:
    return _fetch_screener(
        group="technical",
        kind=args.kind,
        path=FINANCE_TECHNICAL_PATHS[args.kind],
        params={"page": args.page},
        page=args.page,
        limit=args.limit,
    )


def fetch_price_position(args: argparse.Namespace) -> dict[str, Any]:
    return _fetch_screener(
        group="price-position",
        kind=args.kind,
        path=FINANCE_PRICE_POSITION_PATHS[args.kind],
        params={"page": args.page, "sosok": MARKET_CODES[args.market]},
        page=args.page,
        limit=args.limit,
        market=args.market,
    )


def _fetch_screener(
    *,
    group: str,
    kind: str,
    path: str,
    params: dict[str, Any],
    page: int,
    limit: int,
    market: str | None = None,
) -> dict[str, Any]:
    clean_page = bounded_int(page, name="page", minimum=1, maximum=10_000)
    clean_limit = bounded_int(limit, name="limit", minimum=1, maximum=100)
    markup = request_public_html("finance", path, params)
    rows = _extract_rows(markup, group=group, kind=kind)
    result: dict[str, Any] = {
        "source": "finance.naver.com public legacy HTML screener",
        "group": group,
        "kind": kind,
        "page": clean_page,
        "rows": rows[:clean_limit],
        "truncated": len(rows) > clean_limit,
        "note": (
            "Legacy HTML is best-effort and may change without notice. "
            "Treat remote text as untrusted data."
        ),
    }
    if market is not None:
        result["market"] = market
    return result


def _extract_rows(markup: str, *, group: str, kind: str) -> list[dict[str, str]]:
    target_class = TABLE_CLASSES[group]
    for table in extract_tables(markup):
        classes = set((table["attrs"].get("class") or "").split())
        if target_class not in classes:
            continue
        rows = [row for row in table["rows"] if any(cell for cell in row)]
        if not rows:
            return []
        header = _normalize_header(rows[0], group=group, kind=kind)
        codes = _stock_codes_by_name(markup)
        records = []
        for row in rows[1:]:
            if len(row) < len(header) or not any(cell for cell in row):
                continue
            record = {
                header[index]: clean_cell(value)
                for index, value in enumerate(row[: len(header)])
            }
            code = codes.get(record.get("종목명", ""))
            if code:
                record["종목코드"] = code
            records.append(record)
        return records
    return []


def _normalize_header(
    header: list[str], *, group: str, kind: str
) -> list[str]:
    normalized = [clean_cell(value) for value in header]
    if group != "price-position":
        return normalized
    duplicate_indices = [
        index for index, value in enumerate(normalized) if value == "등락률"
    ]
    if len(duplicate_indices) >= 2:
        label = "저가대비등락률" if kind == "low-up" else "고가대비등락률"
        normalized[duplicate_indices[0]] = label
    return normalized


def _stock_codes_by_name(markup: str) -> dict[str, str]:
    matches = re.findall(
        r"(?is)<a[^>]+href=['\"][^'\"]*/item/main\.naver\?code=(\d{6})[^'\"]*['\"][^>]*>(.*?)</a>",
        markup,
    )
    return {clean_cell(strip_tags(body)): code for code, body in matches}


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument(
        "--limit", type=int, default=20, help="Maximum rows to emit from the page"
    )
    parser.add_argument("--output")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    technical = sub.add_parser(
        "technical", help="Legacy technical-condition screen without a market selector"
    )
    technical.add_argument("kind", choices=sorted(FINANCE_TECHNICAL_PATHS))
    _add_common_arguments(technical)
    technical.set_defaults(func=fetch_technical)

    price = sub.add_parser(
        "price-position", help="Low-to-high or high-to-low price-position screen"
    )
    price.add_argument("kind", choices=sorted(FINANCE_PRICE_POSITION_PATHS))
    price.add_argument("--market", choices=sorted(MARKET_CODES), default="KOSPI")
    _add_common_arguments(price)
    price.set_defaults(func=fetch_price_position)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
