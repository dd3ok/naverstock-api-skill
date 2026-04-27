#!/usr/bin/env python3
"""Fetch Naver Stock domestic ETF list and filter metadata."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, render_json, request_json


LISTING_TYPES = {
    "priceTop": "tradingValueDesc",
    "capitalization": "aumDesc",
    "upper": "changeRateDescUpAll",
    "lower": "changeRateDescDownAll",
    "trading": "tradingVolumeDesc",
    "quantHigh": "tradingVolumeIncreaseRateDesc",
    "quantLow": "tradingVolumeIncreaseRateAsc",
    "return1m": "returnRate1mDesc",
    "return3m": "returnRate3mDesc",
    "return6m": "returnRate6mDesc",
    "new": "listedAtDesc",
    "marketCap": "marketCapDesc",
}

ETN_ORDER_TYPES = {
    "marketSum": "MARKET_SUM_ETN",
    "priceTop": "AMOUNT_ETN",
    "upper": "UP_ETN",
    "lower": "DOWN_ETN",
    "trading": "QUANT_ETN",
    "quantHigh": "QUANT_HIGH_ETN",
    "quantLow": "QUANT_LOW_ETN",
    "new": "NEW_STOCK_ETN",
}


def fetch_list(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/stockSecurity/etfs/v1/domestic",
            {
                "listingType": LISTING_TYPES.get(args.listing_type, args.listing_type),
                "size": args.size,
                "index": args.index,
                "largeCategoryCode": args.large_category_code,
                "middleCategoryCode": args.middle_category_code,
                "leverageType": args.leverage_type,
            },
        )
    )


def fetch_themes(args: argparse.Namespace) -> Any:
    return request_json("/api/stockSecurity/etfs/v1/domestic/themes")


def fetch_leverage_types(args: argparse.Namespace) -> Any:
    return request_json("/api/stockSecurity/etfs/v1/domestic/leverage-types")


def fetch_etn_list(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/market/etn",
            {
                "orderType": ETN_ORDER_TYPES.get(args.order_type, args.order_type),
                "largeCodeList": args.large_code,
                "middleCodeList": args.middle_code,
                "startIdx": args.start_idx,
                "pageSize": args.page_size,
            },
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    listing = sub.add_parser("list", help="Domestic ETF list")
    listing.add_argument("--listing-type", default="priceTop")
    listing.add_argument("--size", type=int, default=20)
    listing.add_argument("--index", type=int, default=0)
    listing.add_argument("--large-category-code")
    listing.add_argument("--middle-category-code")
    listing.add_argument("--leverage-type")
    listing.add_argument("--output")
    listing.set_defaults(func=fetch_list)

    themes = sub.add_parser("themes", help="ETF large and middle category metadata")
    themes.add_argument("--output")
    themes.set_defaults(func=fetch_themes)

    leverage = sub.add_parser("leverage-types", help="ETF leverage-type metadata")
    leverage.add_argument("--output")
    leverage.set_defaults(func=fetch_leverage_types)

    etn = sub.add_parser("etn-list", help="Domestic ETN market list")
    etn.add_argument("--order-type", default="priceTop")
    etn.add_argument("--large-code")
    etn.add_argument("--middle-code")
    etn.add_argument("--start-idx", type=int, default=0)
    etn.add_argument("--page-size", type=int, default=20)
    etn.add_argument("--output")
    etn.set_defaults(func=fetch_etn_list)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
