#!/usr/bin/env python3
"""Fetch read-only Naver Stock discussion payloads."""

from __future__ import annotations

import argparse
from typing import Any

from naverstock_api import build_path, emit_output, render_json, request_json


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
    return request_json(
        build_path("/api/community/discussion/posts/popular/hot", {"viewerProfileId": args.viewer_profile_id})
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
    popular.add_argument("--viewer-profile-id")
    popular.add_argument("--output")
    popular.set_defaults(func=fetch_popular_hot)

    args = parser.parse_args()
    emit_output(render_json(args.func(args)), args.output)


if __name__ == "__main__":
    main()
