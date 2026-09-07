#!/usr/bin/env python3
"""Fetch Naver Stock domestic stock detail and quote payloads."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import (
    bounded_int, build_path, emit_output, normalize_item_code, render_json,
    request_json, validate_public_request,
)


def fetch_stock_summary(args: argparse.Namespace) -> dict[str, Any]:
    code = normalize_item_code(args.code)
    industry_path = None
    if args.include_industry:
        industry_path = build_path(
            f"/api/domestic/detail/{code}/stock/industry",
            {
                "page": bounded_int(args.industry_page, name="industry-page", minimum=1, maximum=10_000),
                "pageSize": bounded_int(args.industry_page_size, name="industry-page-size", minimum=1, maximum=500),
                "marketType": args.market_type,
            },
        )
        validate_public_request(industry_path)
    payload: dict[str, Any] = {
        "itemCode": code,
        "codeType": args.code_type,
        "detail": request_json(f"/api/domestic/detail/{code}/detail?codeType={args.code_type}"),
    }
    if args.include_sosok:
        payload["sosok"] = request_json(f"/api/domestic/detail/{code}/sosok")
    if args.include_consensus:
        payload["consensus"] = request_json(f"/api/domestic/detail/{code}/consensus")
    if args.include_polling:
        polling_path = (
            "/api/polling/domestic/NXT/stock"
            if args.code_type == "NXT"
            else "/api/polling/domestic/stock"
        )
        payload["polling"] = request_json(
            build_path(polling_path, {"itemCodes": code})
        )
    if industry_path:
        payload["industry"] = request_json(industry_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", required=True, help="Six-character ASCII item code, e.g. 005930 or 0193W0")
    parser.add_argument("--code-type", choices=["KRX", "NXT"], default="KRX")
    parser.add_argument("--market-type", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL")
    parser.add_argument("--include-sosok", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--include-consensus", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--include-polling", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--include-industry", action="store_true")
    parser.add_argument("--industry-page", type=int, default=1)
    parser.add_argument("--industry-page-size", type=int, default=10)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        payload = fetch_stock_summary(args)
    except ValueError as exc:
        parser.error(str(exc))
    emit_output(render_json(payload), args.output)


if __name__ == "__main__":
    main()
