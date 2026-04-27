#!/usr/bin/env python3
"""Fetch Naver Stock research report payloads."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, render_json, request_json


CATEGORIES = ["INVEST", "MARKET", "INDUSTRY", "COMPANY", "ECONOMY", "DEBENTURE"]


def fetch_category(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/research/category",
            {
                "category": args.category,
                "page": args.page,
                "pageSize": args.page_size,
                "searchText": args.search_text,
                "startDate": args.start_date,
                "endDate": args.end_date,
            },
        )
    )


def fetch_detail(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(f"/api/domestic/research/category/{args.research_id}", {"category": args.category})
    )


def fetch_recent_popular(args: argparse.Namespace) -> Any:
    return request_json("/api/domestic/research/recent-popular")


def fetch_broker_list(args: argparse.Namespace) -> Any:
    return request_json("/api/domestic/research/broker-list")


def fetch_aggregate_static(args: argparse.Namespace) -> Any:
    return request_json(
        "/api/domestic/home/researchaggregate/static",
        method="POST",
        body={
            "sections": {
                "researchCategory": args.research_category,
                "researchRanking": args.research_ranking,
                "recentPopular": args.recent_popular,
            }
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    category = sub.add_parser("category", help="Research list by category")
    category.add_argument("--category", choices=CATEGORIES, default="COMPANY")
    category.add_argument("--page", type=int, default=1)
    category.add_argument("--page-size", type=int, default=15)
    category.add_argument("--search-text")
    category.add_argument("--start-date")
    category.add_argument("--end-date")
    category.add_argument("--output")
    category.set_defaults(func=fetch_category)

    detail = sub.add_parser("detail", help="Research detail by category and id")
    detail.add_argument("--category", choices=CATEGORIES, default="COMPANY")
    detail.add_argument("--research-id", required=True)
    detail.add_argument("--output")
    detail.set_defaults(func=fetch_detail)

    recent = sub.add_parser("recent-popular", help="Recent popular research")
    recent.add_argument("--output")
    recent.set_defaults(func=fetch_recent_popular)

    brokers = sub.add_parser("broker-list", help="Broker list")
    brokers.add_argument("--output")
    brokers.set_defaults(func=fetch_broker_list)

    aggregate = sub.add_parser("aggregate-static", help="Research home aggregate blocks")
    aggregate.add_argument("--research-category", action=argparse.BooleanOptionalAction, default=True)
    aggregate.add_argument("--research-ranking", action=argparse.BooleanOptionalAction, default=True)
    aggregate.add_argument("--recent-popular", action=argparse.BooleanOptionalAction, default=True)
    aggregate.add_argument("--output")
    aggregate.set_defaults(func=fetch_aggregate_static)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
