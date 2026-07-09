#!/usr/bin/env python3
"""Fetch read-only Naver Stock discussion payloads."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, normalize_item_code, render_json, request_json


def fetch_hot_home(args: argparse.Namespace) -> Any:
    return request_json(
        build_path("/api/community/discussion/posts/hot/home", {"pageSize": args.page_size, "page": args.page})
    )


def fetch_post(args: argparse.Namespace) -> Any:
    return request_json(f"/api/community/discussion/posts/{args.post_id}")


def fetch_adjacent(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            f"/api/community/discussion/posts/{args.post_id}/adjacent",
            {
                "itemCode": args.item_code,
                "pageSize": args.page_size,
                "discussionGroupType": args.discussion_group_type,
                "excludesItemNews": args.excludes_item_news,
                "isItemNewsOnly": args.is_item_news_only,
                "excludesBlockPost": args.excludes_block_post,
            },
        )
    )


def fetch_related_hot(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/community/discussion/posts/related/hot",
            {"itemCode": args.item_code, "pageSize": args.page_size, "discussionType": args.discussion_type},
        )
    )


def fetch_popular_hot(args: argparse.Namespace) -> Any:
    return request_json("/api/community/discussion/posts/popular/hot")


def fetch_feed(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/community/discussion/posts",
            {
                "pageSize": args.page_size,
                "offset": args.offset,
                "discussionGroupType": args.discussion_group_type,
            },
        )
    )


def fetch_market_feed(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/community/discussion/posts/market",
            {
                "filterType": args.filter_type,
                "pageSize": args.page_size,
                "offset": args.offset,
                "discussionGroupType": args.discussion_group_type,
            },
        )
    )


def fetch_item_posts(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/community/discussion/posts/by-item",
            {
                "itemCode": normalize_item_code(args.item_code),
                "discussionType": args.discussion_type,
                "pageSize": args.page_size,
                "offset": args.offset,
                "isHolderOnly": args.is_holder_only,
                "excludesItemNews": args.excludes_item_news,
                "isItemNewsOnly": args.is_item_news_only,
            },
        )
    )


def fetch_stats_by_items(args: argparse.Namespace) -> Any:
    domestic_codes = ",".join(normalize_item_code(code) for code in args.domestic_codes) if args.domestic_codes else None
    foreign_codes = ",".join(args.foreign_codes) if args.foreign_codes else None
    return request_json(
        build_path(
            "/api/community/discussion/stats/by-items",
            {
                "startDate": args.start_date,
                "domesticCodes": domestic_codes,
                "foreignCodes": foreign_codes,
            },
        )
    )


def fetch_rankings(args: argparse.Namespace) -> Any:
    return request_json(
        build_path(
            "/api/community/discussion/rankings",
            {
                "nationType": args.nation_type,
                "page": args.page,
                "size": args.size,
                "postType": args.post_type,
            },
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    hot = sub.add_parser("hot-home", help="Home hot discussion posts")
    hot.add_argument("--page", type=int, default=1)
    hot.add_argument("--page-size", type=int, default=20)
    hot.add_argument("--output")
    hot.set_defaults(func=fetch_hot_home)

    post = sub.add_parser("post", help="Discussion post detail")
    post.add_argument("--post-id", required=True)
    post.add_argument("--output")
    post.set_defaults(func=fetch_post)

    adjacent = sub.add_parser("adjacent", help="Adjacent posts around a detail post")
    adjacent.add_argument("--post-id", required=True)
    adjacent.add_argument("--item-code")
    adjacent.add_argument("--page-size", type=int, default=20)
    adjacent.add_argument("--discussion-group-type")
    adjacent.add_argument("--excludes-item-news", action=argparse.BooleanOptionalAction, default=None)
    adjacent.add_argument("--is-item-news-only", action=argparse.BooleanOptionalAction, default=None)
    adjacent.add_argument("--excludes-block-post", action=argparse.BooleanOptionalAction, default=None)
    adjacent.add_argument("--output")
    adjacent.set_defaults(func=fetch_adjacent)

    related = sub.add_parser("related-hot", help="Related hot discussion posts for an item")
    related.add_argument("--item-code", required=True)
    related.add_argument("--page-size", type=int, default=20)
    related.add_argument("--discussion-type", default="domesticStock")
    related.add_argument("--output")
    related.set_defaults(func=fetch_related_hot)

    popular = sub.add_parser("popular-hot", help="Popular hot discussion posts")
    popular.add_argument("--output")
    popular.set_defaults(func=fetch_popular_hot)

    feed = sub.add_parser("feed", help="General discussion feed")
    feed.add_argument("--page-size", type=int, default=20)
    feed.add_argument("--offset")
    feed.add_argument("--discussion-group-type")
    feed.add_argument("--output")
    feed.set_defaults(func=fetch_feed)

    market_feed = sub.add_parser("market-feed", help="Market discussion feed")
    market_feed.add_argument("--filter-type", default="marketIndex")
    market_feed.add_argument("--page-size", type=int, default=20)
    market_feed.add_argument("--offset")
    market_feed.add_argument("--discussion-group-type")
    market_feed.add_argument("--output")
    market_feed.set_defaults(func=fetch_market_feed)

    item_posts = sub.add_parser("item-posts", help="Discussion posts for an item")
    item_posts.add_argument("--item-code", required=True)
    item_posts.add_argument("--discussion-type", default="domesticStock")
    item_posts.add_argument("--page-size", type=int, default=20)
    item_posts.add_argument("--offset")
    item_posts.add_argument("--is-holder-only", action=argparse.BooleanOptionalAction, default=False)
    item_posts.add_argument("--excludes-item-news", action=argparse.BooleanOptionalAction, default=False)
    item_posts.add_argument("--is-item-news-only", action=argparse.BooleanOptionalAction, default=False)
    item_posts.add_argument("--output")
    item_posts.set_defaults(func=fetch_item_posts)

    stats = sub.add_parser("stats-by-items", help="Discussion statistics for domestic or foreign item codes")
    stats.add_argument("--start-date", required=True)
    stats.add_argument("--domestic-codes", action="append", help="Repeat for each domestic item code")
    stats.add_argument("--foreign-codes", action="append", help="Repeat for each foreign code")
    stats.add_argument("--output")
    stats.set_defaults(func=fetch_stats_by_items)

    rankings = sub.add_parser("rankings", help="Discussion item rankings")
    rankings.add_argument("--nation-type", choices=["KOR", "USA"], default="KOR")
    rankings.add_argument("--page", type=int, default=1)
    rankings.add_argument("--page-size", type=int, default=20, dest="size")
    rankings.add_argument("--post-type", choices=["HOT", "LATEST"], default="HOT")
    rankings.add_argument("--output")
    rankings.set_defaults(func=fetch_rankings)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
