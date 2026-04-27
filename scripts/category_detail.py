#!/usr/bin/env python3
"""Fetch Naver Stock industry/theme/group detail and constituent stock lists."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, render_json, request_json


CATEGORY_PATHS = {
    "industry": "upjong",
    "theme": "theme",
    "groups": "group",
}

ORDER_TYPES = {
    "accQuant": "quantTop",
    "accAmount": "priceTop",
    "up": "up",
    "down": "down",
    "marketSum": "marketSum",
    "sales": "sales",
    "operatingProfit": "operatingProfit",
}


def fetch_ranking(category: str, start_idx: int, page_size: int, sort_type: str) -> list[dict[str, Any]]:
    path = build_path(
        f"/api/domestic/market/{CATEGORY_PATHS[category]}/list",
        {"startIdx": start_idx, "pageSize": page_size, "sortType": sort_type},
    )
    payload = request_json(path)
    return _content_or_list(payload)


def fetch_info(category: str, category_no: str, market_type: str) -> Any:
    return request_json(
        build_path(f"/api/domestic/market/{CATEGORY_PATHS[category]}/{category_no}/info", {"marketType": market_type})
    )


def fetch_stocklist(
    category: str,
    category_no: str,
    market_type: str,
    order_type: str,
    start_idx: int,
    page_size: int,
) -> list[dict[str, Any]]:
    path = build_path(
        f"/api/domestic/market/{CATEGORY_PATHS[category]}/{category_no}/stocklist",
        {
            "marketType": market_type,
            "orderType": ORDER_TYPES.get(order_type, order_type),
            "startIdx": start_idx,
            "pageSize": page_size,
        },
    )
    return _content_or_list(request_json(path))


def resolve_category_no(args: argparse.Namespace) -> str:
    if args.no:
        return args.no
    ranking_start_idx = getattr(args, "ranking_start_idx", 0)
    ranking = fetch_ranking(args.category, ranking_start_idx, max(args.rank, 1), args.sort_type)
    if len(ranking) < args.rank:
        raise RuntimeError(f"Rank {args.rank} was not available in {args.category} ranking")
    return str(ranking[args.rank - 1]["no"])


def fetch_rank(args: argparse.Namespace) -> Any:
    return fetch_ranking(args.category, args.start_idx, args.page_size, args.sort_type)


def fetch_detail(args: argparse.Namespace) -> Any:
    category_no = resolve_category_no(args)
    payload: dict[str, Any] = {"category": args.category, "no": category_no}
    if args.include_info:
        payload["info"] = fetch_info(args.category, category_no, args.market_type)
    if args.include_stocks:
        payload["stocks"] = fetch_stocklist(
            args.category,
            category_no,
            args.market_type,
            args.order_type,
            args.stock_start_idx,
            args.stock_page_size,
        )
    return payload


def fetch_stocks(args: argparse.Namespace) -> Any:
    category_no = resolve_category_no(args)
    return fetch_stocklist(
        args.category,
        category_no,
        args.market_type,
        args.order_type,
        args.start_idx,
        args.page_size,
    )


def _content_or_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("content"), list):
        return payload["content"]
    raise RuntimeError(f"Unexpected list payload shape: {payload!r}")


def add_category_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("category", choices=sorted(CATEGORY_PATHS))
    parser.add_argument("--sort-type", default="changeRate")


def add_resolver_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--no", help="Use a concrete category no from the list API")
    parser.add_argument("--rank", type=int, default=1, help="Resolve category no from current ranking position")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    ranking = sub.add_parser("rank", help="List ranked industries, themes, or groups")
    add_category_args(ranking)
    ranking.add_argument("--start-idx", type=int, default=0)
    ranking.add_argument("--page-size", type=int, default=20)
    ranking.add_argument("--output")
    ranking.set_defaults(func=fetch_rank)

    info = sub.add_parser("detail", help="Fetch category info and/or constituent stocks")
    add_category_args(info)
    add_resolver_args(info)
    info.add_argument("--market-type", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL")
    info.add_argument("--order-type", default="accQuant")
    info.add_argument("--ranking-start-idx", type=int, default=0, help="Ranking start index for rank resolution")
    info.add_argument("--include-info", action="store_true", default=True)
    info.add_argument("--no-info", action="store_false", dest="include_info")
    info.add_argument("--include-stocks", action="store_true", default=True)
    info.add_argument("--no-stocks", action="store_false", dest="include_stocks")
    info.add_argument("--stock-start-idx", type=int, default=0)
    info.add_argument("--stock-page-size", type=int, default=20)
    info.add_argument("--output")
    info.set_defaults(func=fetch_detail)

    stocks = sub.add_parser("stocks", help="Fetch constituent stocks for one category")
    add_category_args(stocks)
    add_resolver_args(stocks)
    stocks.add_argument("--market-type", choices=["ALL", "KOSPI", "KOSDAQ"], default="ALL")
    stocks.add_argument("--order-type", default="accQuant")
    stocks.add_argument("--ranking-start-idx", type=int, default=0, help="Ranking start index for rank resolution")
    stocks.add_argument("--start-idx", type=int, default=0)
    stocks.add_argument("--page-size", type=int, default=20)
    stocks.add_argument("--output")
    stocks.set_defaults(func=fetch_stocks)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
