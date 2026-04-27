#!/usr/bin/env python3
"""Fetch Naver Stock domestic market list and ranking payloads."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, render_json, request_json


def fetch_default(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/market/stock/default",
            {
                "tradeType": args.trade_type,
                "marketType": args.market_type,
                "orderType": args.order_type,
                "startIdx": args.start_idx,
                "pageSize": args.page_size,
                "alertType": args.alert_type,
            },
        )
    )


def fetch_dividend(args: argparse.Namespace) -> Any:
    return request_json(
        build_path("/api/domestic/market/stock/dividend", {"page": args.page, "pageSize": args.page_size})
    )


def fetch_search_top(args: argparse.Namespace) -> Any:
    return request_json(
        build_path("/api/domestic/market/searchTop", {"page": args.page, "pageSize": args.page_size})
    )


def fetch_ipo(args: argparse.Namespace) -> Any:
    return request_json(
        build_path("/api/domestic/market/ipo/progress", {"page": args.page, "pageSize": args.page_size})
    )


def fetch_upjong_theme(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/home/upjongTheme/ranking",
            {"rankingType": args.ranking_type, "page": args.page, "pageSize": args.page_size},
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    default = sub.add_parser("default", help="Domestic stock default ranking/list")
    default.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    default.add_argument("--market-type", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL")
    default.add_argument("--order-type", default="marketSum")
    default.add_argument("--start-idx", type=int, default=0)
    default.add_argument("--page-size", type=int, default=20)
    default.add_argument("--alert-type")
    default.add_argument("--output")
    default.set_defaults(func=fetch_default)

    for name, help_text, func in [
        ("dividend", "High-dividend stock list", fetch_dividend),
        ("search-top", "Popular search ranking", fetch_search_top),
        ("ipo", "IPO progress list", fetch_ipo),
    ]:
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("--page", type=int, default=1)
        cmd.add_argument("--page-size", type=int, default=20)
        cmd.add_argument("--output")
        cmd.set_defaults(func=func)

    upjong = sub.add_parser("upjong-theme", help="Sector/theme ranking")
    upjong.add_argument("--ranking-type", default="upjong")
    upjong.add_argument("--page", type=int, default=1)
    upjong.add_argument("--page-size", type=int, default=20)
    upjong.add_argument("--output")
    upjong.set_defaults(func=fetch_upjong_theme)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
