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
        build_path(
            "/api/domestic/market/stock/dividend",
            {
                "tradeType": args.trade_type,
                "marketType": args.market_type,
                "dividend": args.dividend,
                "startIdx": args.start_idx,
                "pageSize": args.page_size,
            },
        )
    )


def fetch_search_top(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/market/searchTop",
            {"nationType": args.nation_type, "startIdx": args.start_idx, "pageSize": args.page_size},
        )
    )


def fetch_ipo(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/market/ipo/progress",
            {"IpoProgressType": args.ipo_progress_type, "startIdx": args.start_idx, "pageSize": args.page_size},
        )
    )


def fetch_upjong_theme(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/home/upjongTheme/ranking",
            {"sortType": args.sort_type},
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

    dividend = sub.add_parser("dividend", help="High-dividend stock list")
    dividend.add_argument("--trade-type", choices=["KRX", "NXT"], default="KRX")
    dividend.add_argument("--market-type", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL")
    dividend.add_argument("--dividend", default="dividendRate")
    dividend.add_argument("--start-idx", type=int, default=0)
    dividend.add_argument("--page-size", type=int, default=20)
    dividend.add_argument("--output")
    dividend.set_defaults(func=fetch_dividend)

    search = sub.add_parser("search-top", help="Popular search ranking")
    search.add_argument("--nation-type", choices=["KOR", "USA"], default="KOR")
    search.add_argument("--start-idx", type=int, default=0)
    search.add_argument("--page-size", type=int, default=20)
    search.add_argument("--output")
    search.set_defaults(func=fetch_search_top)

    ipo = sub.add_parser("ipo", help="IPO progress list")
    ipo.add_argument("--ipo-progress-type", help="Observed value: LISTING")
    ipo.add_argument("--start-idx", type=int, default=0)
    ipo.add_argument("--page-size", type=int, default=20)
    ipo.add_argument("--output")
    ipo.set_defaults(func=fetch_ipo)

    upjong = sub.add_parser("upjong-theme", help="Sector/theme ranking")
    upjong.add_argument("--sort-type", default="changeRate")
    upjong.add_argument("--output")
    upjong.set_defaults(func=fetch_upjong_theme)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
