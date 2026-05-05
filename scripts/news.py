#!/usr/bin/env python3
"""Fetch Naver Stock market news payloads."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, render_json, request_json


FOCUS_SIDS = {
    "market-outlook": "401",
    "company-analysis": "402",
    "global-market": "403",
    "bond-futures": "404",
    "disclosure-memo": "406",
    "exchange-rate": "429",
}


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
    list_cmd.add_argument("--category", default="mainnews")
    list_cmd.add_argument("--page", type=int, default=1)
    list_cmd.add_argument("--page-size", type=int, default=20)
    list_cmd.add_argument("--date")
    list_cmd.add_argument("--output")
    list_cmd.set_defaults(func=fetch_list)

    focus = sub.add_parser("focus", help="Focus news section")
    focus.add_argument("--focus", default="market-outlook", help="Slug or raw sid")
    focus.add_argument("--page", type=int, default=1)
    focus.add_argument("--page-size", type=int, default=20)
    focus.add_argument("--date")
    focus.add_argument("--enable-fallback", action=argparse.BooleanOptionalAction, default=None)
    focus.add_argument("--max-days", type=int)
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
    notice.add_argument("--page", type=int, default=1)
    notice.add_argument("--page-size", type=int, default=20)
    notice.add_argument("--keyword")
    notice.add_argument("--start-date")
    notice.add_argument("--end-date")
    notice.add_argument("--type-idx", action="append")
    notice.add_argument("--output")
    notice.set_defaults(func=fetch_notice)

    aggregate = sub.add_parser("aggregate", help="News home aggregate blocks")
    aggregate.add_argument("--flash-news-size", type=int, default=5)
    aggregate.add_argument("--main-news-size", type=int, default=5)
    aggregate.add_argument("--ranking-news-size", type=int, default=5)
    aggregate.add_argument("--overseas-news-size", type=int, default=5)
    aggregate.add_argument("--focus-size", type=int, default=5)
    aggregate.add_argument("--money-story-size", type=int, default=5)
    aggregate.add_argument("--notice-size", type=int, default=5)
    aggregate.add_argument("--output")
    aggregate.set_defaults(func=fetch_aggregate)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
