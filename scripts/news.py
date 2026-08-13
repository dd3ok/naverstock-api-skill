#!/usr/bin/env python3
"""Fetch Naver Stock market news payloads."""

from __future__ import annotations

import argparse
import calendar
from datetime import date
from typing import Any

from naverstock_api import build_path, emit_output, render_json, request_json


NEWS_CATEGORIES = ("MAINNEWS", "FLASHNEWS", "RANKNEWS")
FOCUS_SIDS = {
    "market-outlook": "401",
    "company-analysis": "402",
    "global-market": "403",
    "bond-futures": "404",
    "disclosure-memo": "406",
    "exchange-rate": "429",
}


def _numeric_id(value: str) -> str:
    clean = value.strip()
    if not clean.isascii() or not clean.isdigit() or not 1 <= len(clean) <= 30:
        raise argparse.ArgumentTypeError("article-id must contain 1-30 digits")
    return clean


def _news_category(value: str) -> str:
    clean = value.strip().upper()
    if clean not in NEWS_CATEGORIES:
        choices = ", ".join(NEWS_CATEGORIES)
        raise argparse.ArgumentTypeError(f"category must be one of: {choices}")
    return clean


def _notice_date_range(current: date) -> tuple[str, str]:
    target_month = current.year * 12 + current.month - 1 - 3
    start_year, zero_based_month = divmod(target_month, 12)
    start_month = zero_based_month + 1
    start_day = min(current.day, calendar.monthrange(start_year, start_month)[1])
    start = date(start_year, start_month, start_day)
    return start.strftime("%Y%m%d"), current.strftime("%Y%m%d")


def fetch_list(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/news/list",
            {"category": args.category, "page": args.page, "pageSize": args.page_size, "date": args.date},
        )
    )


def fetch_focus(args: argparse.Namespace) -> Any:
    sid = FOCUS_SIDS.get(args.focus, args.focus)
    return request_json(
        build_path(
            "/api/domestic/news/focus",
            {
                "sid": sid,
                "page": args.page,
                "pageSize": args.page_size,
                "date": args.date,
                "enableFallback": args.enable_fallback,
                "maxDays": args.max_days,
            },
        )
    )


def fetch_search(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/news/search",
            {
                "query": args.query,
                "page": args.page,
                "pageSize": args.page_size,
                "startDate": args.start_date,
                "endDate": args.end_date,
            },
        )
    )


def fetch_notice(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/news/noticeList",
            {
                "page": args.page,
                "pageSize": args.page_size,
                "keyword": args.keyword,
                "startDate": args.start_date,
                "endDate": args.end_date,
                "typeIdx": args.type_idx,
            },
        )
    )


def fetch_world_news(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/foreign/news/worldNews",
            {"page": args.page, "pageSize": args.page_size, "date": args.date},
        )
    )


def fetch_world_detail(args: argparse.Namespace) -> Any:
    return request_json(f"/api/foreign/news/worldNews/{args.article_id}")


def fetch_aggregate(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/domestic/news/aggregate/home",
            {
                "flashNewsSize": args.flash_news_size,
                "mainNewsSize": args.main_news_size,
                "rankingNewsSize": args.ranking_news_size,
                "overseasNewsSize": args.overseas_news_size,
                "focusSize": args.focus_size,
                "moneyStorySize": args.money_story_size,
                "noticeSize": args.notice_size,
            },
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list", help="News list")
    list_cmd.add_argument(
        "--category",
        type=_news_category,
        choices=NEWS_CATEGORIES,
        default="MAINNEWS",
    )
    list_cmd.add_argument("--page", type=int, default=1)
    list_cmd.add_argument("--page-size", type=int, default=15)
    list_cmd.add_argument("--date")
    list_cmd.add_argument("--output")
    list_cmd.set_defaults(func=fetch_list)

    focus = sub.add_parser("focus", help="Focus news section")
    focus.add_argument("--focus", default="market-outlook", help="Slug or raw sid")
    focus.add_argument("--page", type=int, default=1)
    focus.add_argument("--page-size", type=int, default=15)
    focus.add_argument("--date")
    focus.add_argument("--enable-fallback", action=argparse.BooleanOptionalAction, default=None)
    focus.add_argument("--max-days", type=int, choices=range(1, 8), metavar="1..7")
    focus.add_argument("--output")
    focus.set_defaults(func=fetch_focus)

    search = sub.add_parser("search", help="Keyword news search")
    search.add_argument("--query", required=True)
    search.add_argument("--page", type=int, default=1)
    search.add_argument("--page-size", type=int, default=20)
    search.add_argument("--start-date")
    search.add_argument("--end-date")
    search.add_argument("--output")
    search.set_defaults(func=fetch_search)

    notice = sub.add_parser("notice", help="Market disclosure/notice news list")
    notice_start, notice_end = _notice_date_range(date.today())
    notice.add_argument("--page", type=int, default=1)
    notice.add_argument("--page-size", type=int, default=15)
    notice.add_argument("--keyword")
    notice.add_argument("--start-date", default=notice_start)
    notice.add_argument("--end-date", default=notice_end)
    notice.add_argument("--type-idx", action="append")
    notice.add_argument("--output")
    notice.set_defaults(func=fetch_notice)

    world_news = sub.add_parser("world-news", help="Overseas news from /news/worldnews")
    world_news.add_argument("--page", type=int, default=1)
    world_news.add_argument("--page-size", type=int, default=15)
    world_news.add_argument("--date")
    world_news.add_argument("--output")
    world_news.set_defaults(func=fetch_world_news)

    world_detail = sub.add_parser("world-detail", help="World/foreign market news article detail")
    world_detail.add_argument(
        "--article-id",
        type=_numeric_id,
        required=True,
        help="World news aid from the world list",
    )
    world_detail.add_argument("--output")
    world_detail.set_defaults(func=fetch_world_detail)

    aggregate = sub.add_parser("aggregate", help="News home aggregate blocks")
    aggregate.add_argument("--flash-news-size", type=int, default=4)
    aggregate.add_argument("--main-news-size", type=int, default=6)
    aggregate.add_argument("--ranking-news-size", type=int, default=5)
    aggregate.add_argument("--overseas-news-size", type=int, default=5)
    aggregate.add_argument("--focus-size", type=int, default=5)
    aggregate.add_argument("--money-story-size", type=int, default=20)
    aggregate.add_argument("--notice-size", type=int, default=5)
    aggregate.add_argument("--output")
    aggregate.set_defaults(func=fetch_aggregate)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
