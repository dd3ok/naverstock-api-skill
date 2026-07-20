#!/usr/bin/env python3
"""Fetch current Naver Stock research report payloads."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from typing import Any

from naverstock_api import (
    NaverStockAPIError,
    build_path,
    emit_output,
    normalize_item_code,
    render_json,
    request_json,
)


CATEGORIES = ["INVEST", "MARKET", "INDUSTRY", "COMPANY", "ECONOMY", "DEBENTURE"]
V1_CATEGORIES = ["company", "industry", "invest", "economy"]
RESEARCH_TYPES = {category: category.lower() for category in CATEGORIES}
RESEARCH_BASE = "/api/stockSecurity/researches/v2"


def _numeric_id(value: str) -> str:
    clean = value.strip()
    if not clean.isascii() or not clean.isdigit() or not 1 <= len(clean) <= 30:
        raise argparse.ArgumentTypeError("research-id must contain 1-30 digits")
    return clean


def fetch_category(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"{RESEARCH_BASE}/{RESEARCH_TYPES[args.category]}",
            {
                "index": max(args.page - 1, 0),
                "size": args.page_size,
                "query": args.search_text,
                "startDate": _normalize_date(args.start_date),
                "endDate": _normalize_date(args.end_date),
                "brokerCodes": args.broker_code,
                "industryTypes": args.industry_type,
                "itemCodes": _normalize_item_codes(args.item_code),
            },
        )
    )


def fetch_detail(args: argparse.Namespace) -> Any:
    return request_json(f"{RESEARCH_BASE}/{RESEARCH_TYPES[args.category]}/{args.research_id}")


def fetch_weekly_hot(args: argparse.Namespace) -> Any:
    return _request_weekly_hot(args.start_date, args.size)


def fetch_recent_popular(args: argparse.Namespace) -> Any:
    """Keep the old function name as a compatibility alias for weekly-hot."""

    return fetch_weekly_hot(args)


def fetch_ranking(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/research/ranking",
            {"rankingType": args.ranking_type, "selectedRank": args.selected_rank},
        )
    )


def fetch_latest(args: argparse.Namespace) -> Any:
    return _request_latest(args.size)


def fetch_category_latest(args: argparse.Namespace) -> Any:
    """Keep the old function name as a compatibility alias for latest."""

    return fetch_latest(args)


def fetch_industry_research(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"{RESEARCH_BASE}/industry",
            {
                "index": max(args.page - 1, 0),
                "size": args.size,
                "query": args.search_text,
                "startDate": _normalize_date(args.start_date),
                "endDate": _normalize_date(args.end_date),
                "brokerCodes": args.broker_code,
                "industryTypes": args.industry_type,
            },
        )
    )


def fetch_broker_list(args: argparse.Namespace) -> Any:
    return request_json(f"{RESEARCH_BASE}/brokers")


def fetch_by_items(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"{RESEARCH_BASE}/company/by-items",
            {"itemCodes": _normalize_item_codes(args.item_code), "size": args.size},
        )
    )


def fetch_goal_price_changed(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"{RESEARCH_BASE}/company/goal-price-changed",
            {"direction": args.direction, "size": args.size},
        )
    )


def fetch_analysis_focus(args: argparse.Namespace) -> Any:
    return request_json(f"{RESEARCH_BASE}/analysis-focus")


def fetch_home(args: argparse.Namespace) -> dict[str, Any]:
    """Fetch independent home sections without hiding unavailable endpoints as empty data."""

    sections: dict[str, Any] = {}
    if args.research_category:
        sections["latestResearch"] = _best_effort_section(lambda: _request_latest(args.latest_size))
    if args.research_ranking:
        sections["researchRanking"] = _best_effort_section(
            lambda: request_json(
                build_path(
                    "/api/domestic/research/ranking",
                    {"rankingType": args.ranking_type, "selectedRank": args.selected_rank},
                )
            )
        )
    if args.recent_popular:
        sections["weeklyHot"] = _best_effort_section(
            lambda: _request_weekly_hot(args.weekly_hot_start_date, args.weekly_hot_size)
        )
    return {
        "partial": any(section["status"] != "ok" for section in sections.values()),
        "sections": sections,
    }


def fetch_aggregate_static(args: argparse.Namespace) -> dict[str, Any]:
    """Keep the old function name as a compatibility alias for home."""

    return fetch_home(args)


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


def _request_latest(size: int) -> Any:
    return request_json(build_path(f"{RESEARCH_BASE}/latestResearch", {"size": size}))


def _request_weekly_hot(start_date: str | None, size: int) -> Any:
    return request_json(
        build_path(
            f"{RESEARCH_BASE}/weekly-hot",
            {"startDate": _normalize_date(start_date), "size": size},
        )
    )


def _best_effort_section(fetcher: Callable[[], Any]) -> dict[str, Any]:
    try:
        return {"status": "ok", "data": fetcher()}
    except NaverStockAPIError as exc:
        return {"status": "unavailable", "error": exc.as_dict()}


def _normalize_date(value: str | None) -> str | None:
    if value and len(value) == 8 and value.isdigit():
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    return value


def _normalize_item_codes(values: list[str] | None) -> list[str] | None:
    if not values:
        return None
    return [normalize_item_code(value) for value in values]


def _add_list_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--search-text")
    parser.add_argument("--start-date", help="YYYY-MM-DD or YYYYMMDD")
    parser.add_argument("--end-date", help="YYYY-MM-DD or YYYYMMDD")
    parser.add_argument("--broker-code", action="append")
    parser.add_argument("--industry-type", action="append")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    category = sub.add_parser("category", help="Research list by category")
    category.add_argument("--category", choices=CATEGORIES, default="COMPANY")
    category.add_argument("--page", type=int, default=1, help="One-based page number")
    category.add_argument("--page-size", type=int, default=15)
    category.add_argument("--item-code", action="append", help="Repeat to restrict company reports by item")
    _add_list_filters(category)
    category.add_argument("--output")
    category.set_defaults(func=fetch_category)

    detail = sub.add_parser("detail", help="Research detail by category and id")
    detail.add_argument("--category", choices=CATEGORIES, default="COMPANY")
    detail.add_argument("--research-id", type=_numeric_id, required=True)
    detail.add_argument("--output")
    detail.set_defaults(func=fetch_detail)

    weekly = sub.add_parser("weekly-hot", aliases=["recent-popular"], help="Weekly popular research")
    weekly.add_argument("--start-date", help="YYYY-MM-DD or YYYYMMDD")
    weekly.add_argument("--size", type=int, default=10)
    weekly.add_argument("--output")
    weekly.set_defaults(func=fetch_weekly_hot)

    ranking = sub.add_parser("ranking", help="Research ranking")
    ranking.add_argument("--ranking-type", default="SEARCH_TOP")
    ranking.add_argument("--selected-rank", type=int, default=1)
    ranking.add_argument("--output")
    ranking.set_defaults(func=fetch_ranking)

    latest = sub.add_parser("latest", aliases=["category-latest"], help="Latest research category blocks")
    latest.add_argument("--size", type=int, default=3)
    latest.add_argument("--output")
    latest.set_defaults(func=fetch_latest)

    industry = sub.add_parser("industry-research", help="Industry research list")
    industry.add_argument("--page", type=int, default=1, help="One-based page number")
    industry.add_argument("--size", type=int, default=15)
    _add_list_filters(industry)
    industry.add_argument("--output")
    industry.set_defaults(func=fetch_industry_research)

    brokers = sub.add_parser("broker-list", help="Broker list")
    brokers.add_argument("--output")
    brokers.set_defaults(func=fetch_broker_list)

    by_items = sub.add_parser("by-items", help="Company research grouped by item code")
    by_items.add_argument("--item-code", action="append", required=True)
    by_items.add_argument("--size", type=int, default=3)
    by_items.add_argument("--output")
    by_items.set_defaults(func=fetch_by_items)

    goal_price = sub.add_parser("goal-price-changed", help="Company reports with changed goal prices")
    goal_price.add_argument("--direction", choices=["up", "down"], required=True)
    goal_price.add_argument("--size", type=int, default=10)
    goal_price.add_argument("--output")
    goal_price.set_defaults(func=fetch_goal_price_changed)

    focus = sub.add_parser("analysis-focus", help="Research analysis focus block")
    focus.add_argument("--output")
    focus.set_defaults(func=fetch_analysis_focus)

    home = sub.add_parser(
        "home",
        aliases=["aggregate-static"],
        help="Best-effort research home sections with explicit unavailable status",
    )
    home.add_argument("--research-category", action=argparse.BooleanOptionalAction, default=True)
    home.add_argument("--research-ranking", action=argparse.BooleanOptionalAction, default=True)
    home.add_argument("--recent-popular", action=argparse.BooleanOptionalAction, default=True)
    home.add_argument("--latest-size", type=int, default=3)
    home.add_argument("--weekly-hot-start-date", help="YYYY-MM-DD or YYYYMMDD")
    home.add_argument("--weekly-hot-size", type=int, default=10)
    home.add_argument("--ranking-type", default="SEARCH_TOP")
    home.add_argument("--selected-rank", type=int, default=1)
    home.add_argument("--output")
    home.set_defaults(func=fetch_home)

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
