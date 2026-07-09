#!/usr/bin/env python3
"""Fetch Naver Stock research report payloads."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, normalize_item_code, render_json, request_json


CATEGORIES = ["INVEST", "MARKET", "INDUSTRY", "COMPANY", "ECONOMY", "DEBENTURE"]
V1_CATEGORIES = ["company", "industry", "invest", "economy"]


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


def fetch_ranking(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/research/ranking",
            {"rankingType": args.ranking_type, "selectedRank": args.selected_rank},
        )
    )


def fetch_category_latest(args: argparse.Namespace) -> Any:
    return request_json("/api/domestic/research/category-lastest")


def fetch_industry_research(args: argparse.Namespace) -> Any:
    return request_json("/api/domestic/research/industry-research")


def fetch_broker_list(args: argparse.Namespace) -> Any:
    return request_json("/api/domestic/research/broker-list")


def fetch_v1_category(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/stockSecurity/researches/v1/{args.category}",
            {"index": args.index, "size": args.size},
        )
    )


def fetch_v1_brokers(args: argparse.Namespace) -> Any:
    return request_json("/api/stockSecurity/researches/v1/brokers")


def fetch_v1_latest(args: argparse.Namespace) -> Any:
    return request_json(build_path("/api/stockSecurity/researches/v1/latestResearch", {"size": args.size}))


def fetch_v1_by_items(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/stockSecurity/researches/v1/company/by-items",
            {"itemCodes": [normalize_item_code(code) for code in args.item_codes], "size": args.size},
        )
    )


def fetch_v1_analysis_focus(args: argparse.Namespace) -> Any:
    return request_json("/api/stockSecurity/researches/v1/analysis-focus")


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

    ranking = sub.add_parser("ranking", help="Research ranking")
    ranking.add_argument("--ranking-type", default="SEARCH_TOP")
    ranking.add_argument("--selected-rank", type=int, default=1)
    ranking.add_argument("--output")
    ranking.set_defaults(func=fetch_ranking)

    latest = sub.add_parser("category-latest", help="Latest research category blocks")
    latest.add_argument("--output")
    latest.set_defaults(func=fetch_category_latest)

    industry = sub.add_parser("industry-research", help="Industry research block")
    industry.add_argument("--output")
    industry.set_defaults(func=fetch_industry_research)

    brokers = sub.add_parser("broker-list", help="Broker list")
    brokers.add_argument("--output")
    brokers.set_defaults(func=fetch_broker_list)

    v1_category = sub.add_parser("v1-category", help="stockSecurity v1 research list by category")
    v1_category.add_argument("--category", choices=V1_CATEGORIES, default="company")
    v1_category.add_argument("--index", type=int, default=0)
    v1_category.add_argument("--size", type=int, default=15)
    v1_category.add_argument("--output")
    v1_category.set_defaults(func=fetch_v1_category)

    v1_brokers = sub.add_parser("v1-brokers", help="stockSecurity v1 broker list")
    v1_brokers.add_argument("--output")
    v1_brokers.set_defaults(func=fetch_v1_brokers)

    v1_latest = sub.add_parser("v1-latest", help="stockSecurity v1 latest research blocks")
    v1_latest.add_argument("--size", type=int, default=5)
    v1_latest.add_argument("--output")
    v1_latest.set_defaults(func=fetch_v1_latest)

    v1_by_items = sub.add_parser("v1-by-items", help="stockSecurity v1 company research by item codes")
    v1_by_items.add_argument("--item-codes", action="append", required=True, help="Repeat for each domestic item code")
    v1_by_items.add_argument("--size", type=int, default=5)
    v1_by_items.add_argument("--output")
    v1_by_items.set_defaults(func=fetch_v1_by_items)

    v1_analysis = sub.add_parser("v1-analysis-focus", help="stockSecurity v1 analysis focus")
    v1_analysis.add_argument("--output")
    v1_analysis.set_defaults(func=fetch_v1_analysis_focus)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
